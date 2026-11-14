"""
realism_stress.py - step 4 stress test: do the app's models still work on more realistic
movement? (team leader's list, Sat 14 Nov)

The models were trained on the original synthetic movement. This rebuilds the VALIDATION
people's examples with the realistic version 2 (data_pipeline/synthetic_paths.py,
realistic=True) and sends the cursor (movement + tremor) through device_view() - whole
pixels, uneven 60 or 125 samples per second - as a real computer would see it. The same
people, the same tremor recordings and the same build code (build_dataset.py) are used;
only the movement and the device view change. The intended path stays exact.

THE RULE (fixed before running it): retrain on realistic movement only if the models CLEARLY
drop: the detector's missed cases or false alarms rise by more than 5 percentage points, or
the corrector's advantage over no filter (distance from the path while moving) shrinks by
more than a third.

Models: the app's detector v2 (with its cut-off) and corrector v4 (penalty 2), gated as in
the app. Validation people only: this is a design decision, so test people are not used.

Run from the repository folder (needs data/derived; a few minutes):
    python evaluation/realism_stress.py
Writes evaluation/results/realism_stress.md.
"""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "data_pipeline"))
import build_dataset  # noqa: E402
import synthetic_paths  # noqa: E402
from baselines.classical_filters import OneEuroFilter  # noqa: E402
from evaluation.evaluate_corrector import SKIP, corrector_offsets, detector_gate  # noqa: E402
from evaluation.metrics import corrector_scores, detector_scores, run_filter  # noqa: E402
from models.corrector.live import WEIGHTS, load_corrector  # noqa: E402
from models.detector.features import compute_features  # noqa: E402
from models.detector.predict import Detector  # noqa: E402

DERIVED = ROOT / "data" / "derived"
RESULT = ROOT / "evaluation" / "results" / "realism_stress.md"
SEED = 21                    # validation's normal build uses seed 2; a new stream here
MAX_RISE = 0.05              # detector: 5 percentage points
MAX_SHRINK = 1 / 3           # corrector: a third of its advantage over no filter


def realistic_val_sets():
    """Validation detector windows and corrector sequences with realistic movement + device view."""
    lib = dict(np.load(build_dataset.LIBRARY))
    with open(build_dataset.SPLIT_FILE, encoding="utf-8") as f:
        members = json.load(f)["val"]
    rng = np.random.default_rng(SEED)
    original = build_dataset.generate_path
    build_dataset.generate_path = lambda r, n, events=None: synthetic_paths.generate_path(r, n, realistic=True)
    try:
        x, _, facts = build_dataset.build_detector(lib, members, rng, 1.0)
        shaky, clean, cfacts = build_dataset.build_corrector(lib, members, rng, 1.0)
    finally:
        build_dataset.generate_path = original
    x = np.stack([synthetic_paths.device_view(w, rng) for w in x])
    shaky = np.stack([synthetic_paths.device_view(s, rng) for s in shaky])
    labels = np.array([f["label"] for f in facts], bool)
    tremor = np.array([f["tremor"] for f in cfacts], bool)
    return x, labels, shaky, clean, tremor


def detector_numbers(detector, xy, labels):
    scores = detector.classifier.predict_proba(compute_features(xy))[:, 1]
    return detector_scores(labels, scores >= detector.threshold)


def corrector_numbers(detector, shaky, clean, tremor):
    gate = detector_gate(detector, shaky)[..., None]
    ours = shaky + gate * corrector_offsets(load_corrector(WEIGHTS), shaky)
    out = {}
    for name, cursor in [("No filter", shaky), ("One Euro", run_filter(OneEuroFilter, shaky)), ("Our system", ours)]:
        out[name] = corrector_scores(cursor[tremor], clean[tremor], shaky[tremor], skip=SKIP)
    return out


def main():
    detector = Detector()
    val = np.load(DERIVED / "detector_val.npz")
    cval = np.load(DERIVED / "corrector_val.npz")
    x_r, labels_r, shaky_r, clean_r, tremor_r = realistic_val_sets()

    det = {"original": detector_numbers(detector, val["xy"], val["label"].astype(bool)),
           "realistic": detector_numbers(detector, x_r, labels_r)}
    cor = {"original": corrector_numbers(detector, cval["shaky"], cval["clean"], cval["tremor"].astype(bool)),
           "realistic": corrector_numbers(detector, shaky_r, clean_r, tremor_r)}

    def advantage(c):
        return c["No filter"]["distance_moving"] - c["Our system"]["distance_moving"]

    rise_missed = det["realistic"]["missed"] - det["original"]["missed"]
    rise_alarms = det["realistic"]["false_alarms"] - det["original"]["false_alarms"]
    shrink = 1 - advantage(cor["realistic"]) / advantage(cor["original"])
    retrain = rise_missed > MAX_RISE or rise_alarms > MAX_RISE or shrink > MAX_SHRINK

    lines = ["# Step 4 stress test: the app's models on more realistic movement (validation people)", "",
             "Produced by `python evaluation/realism_stress.py`. Same validation people and tremor "
             "recordings; the movement is the realistic version 2 and the cursor goes through "
             "`device_view()` (whole pixels, uneven 60/125 samples per second). Detector v2 with its "
             "cut-off; corrector v4 (penalty 2) gated by detector v2.", "",
             "## Detector", "", "| Movement | Windows (tremor) | Missed cases | False alarms |", "|---|---|---|---|"]
    for name, n, lab in [("original", len(val["label"]), val["label"].sum()), ("realistic", len(labels_r), labels_r.sum())]:
        lines.append("| %s | %d (%d) | %.1f%% | %.1f%% |" % (
            name, n, lab, 100 * det[name]["missed"], 100 * det[name]["false_alarms"]))
    lines += ["", "## Corrector (sequences with marked tremor, scored after 2.56 s)", "",
              "| Movement | Method | Off the path moving / still (px) | Tremor removed | Lag (ms) | Jerkiness (px) |",
              "|---|---|---|---|---|---|"]
    for name in ["original", "realistic"]:
        for method, s in cor[name].items():
            lines.append("| %s | %s | %.2f / %.2f | %.0f%% | %.0f | %.2f |" % (
                name, method, s["distance_moving"], s["distance_still"], 100 * s["tremor_removed"],
                s["lag_ms"], s["jerkiness"]))
    lines += ["", "## Decision (rule fixed in advance)", "",
              "- Missed cases changed by %+.1f points, false alarms by %+.1f points (limit +%.0f)." % (
                  100 * rise_missed, 100 * rise_alarms, 100 * MAX_RISE),
              "- The corrector's advantage over no filter while moving: %.2f px on original movement, "
              "%.2f px on realistic movement (%s by %.0f%%; limit a third)." % (
                  advantage(cor["original"]), advantage(cor["realistic"]),
                  "shrank" if shrink > 0 else "grew", 100 * abs(shrink)),
              "", "**%s**" % ("Retrain on realistic movement: the models clearly drop." if retrain else
                              "No retraining: the models do not clearly drop on realistic movement."), "",
              "This project is a prototype and is not medical advice.", ""]
    RESULT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
