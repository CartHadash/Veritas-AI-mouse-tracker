"""
improvements.py - one measured improvement to each model.

The official schedule asks for "one improvement, measured". For each model we changed one
thing, compared before and after on VALIDATION people, and keep the change only if it helps.
Only then is the kept version scored once on TEST people.

DETECTOR: v1 vs v2. v2 also learned from windows whose movement never pauses (glides,
  reaches, drifts), because the failure analysis showed v1 treats uninterrupted movement as
  a sign of tremor. Both get their cut-off the same way: at most 20% missed on the normal
  validation windows. Measured on normal AND on pause-free validation windows.

CORRECTOR: v1 vs v2. v2 is trained with every sequence's tremor randomly made 0.5x-2x as
  large (a response to "different mouse DPI settings move the cursor different distances").
  Measured on validation sequences at tremor size x0.5, x1 and x2. (Not kept.)

CORRECTOR v3 (second corrector attempt, after the demo gain looked small): trained to
  minimise the plain distance instead of the squared distance. Compared with v1 per tremor size,
  with the detector v2 gate as in the app. (Kept.)

Run from the repository folder (after training detector v2 and correctors v2 and v3):
    python evaluation/improvements.py            # validation comparison only
    python evaluation/improvements.py --test     # also score the kept versions on test, once
Writes evaluation/results/improvements.md.
"""

import argparse
import sys
from pathlib import Path

import joblib
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evaluation.evaluate_corrector import SKIP, corrector_offsets, detector_gate  # noqa: E402
from evaluation.metrics import SIZE_CLASSES, choose_threshold, corrector_scores, detector_scores  # noqa: E402
from models.corrector.live import load_corrector  # noqa: E402
from models.detector.features import compute_features  # noqa: E402
from models.detector.predict import Detector  # noqa: E402
from sklearn.metrics import average_precision_score  # noqa: E402

DERIVED = ROOT / "data" / "derived"
MODELS = ROOT / "models"
RESULT = ROOT / "evaluation" / "results" / "improvements.md"


def pct(x):
    return "%.1f%%" % (100 * x)


def detector_part(lines, use_test):
    sets = {name: dict(np.load(DERIVED / f"detector_{name}.npz"))
            for name in ["val", "val_continuous"] + (["test", "test_continuous"] if use_test else [])}
    features = {name: compute_features(d["xy"]) for name, d in sets.items()}
    lines += ["## Detector: v1 vs v2 (v2 also learned from pause-free movement)", "",
              "Cut-off for both: at most 20% missed on the normal validation windows.", "",
              "| Version | Data | Average precision | Missed cases | False alarms |", "|---|---|---|---|---|"]
    results = {}
    for version in ["v1", "v2"]:
        model = joblib.load(MODELS / "detector" / f"detector_{version}.joblib")
        scores = {n: model["classifier"].predict_proba(f)[:, 1] for n, f in features.items()}
        cut = choose_threshold(scores["val"], sets["val"]["label"], max_missed=0.20)
        results[version] = (cut, scores)
        for name in ["val", "val_continuous"]:
            s = detector_scores(sets[name]["label"], scores[name] >= cut)
            ap = average_precision_score(sets[name]["label"], scores[name])
            label = "validation, normal" if name == "val" else "validation, pause-free"
            lines.append("| %s | %s | %.3f | %s | %s |" % (version, label, ap, pct(s["missed"]), pct(s["false_alarms"])))
    lines.append("")
    return sets, results


def corrector_part(lines):
    lines += ["## Corrector: v1 vs v2 (v2 trained on tremor 0.5x-2x as large)", "",
              "Average distance to the intended path on validation sequences, corrector always on "
              "(no detector gate, to isolate the change), after the first 2.56 s.", "",
              "| Version | Tremor x0.5 | Tremor x1 | Tremor x2 | Tremor removed x0.5 / x1 / x2 |",
              "|---|---|---|---|---|"]
    for version, path in [("v1", "weights.pt"), ("v2", "weights_v2.pt")]:
        model = load_corrector(MODELS / "corrector" / path)
        cells, removed = [], []
        for suffix in ["_x0.5", "", "_x2"]:
            d = np.load(DERIVED / f"corrector_val{suffix}.npz")
            out = d["shaky"] + corrector_offsets(model, d["shaky"])
            dist = np.linalg.norm(out[:, SKIP:] - d["clean"][:, SKIP:], axis=2).mean()
            t = d["tremor"].astype(bool)
            removed.append(corrector_scores(out[t], d["clean"][t], d["shaky"][t], skip=SKIP)["tremor_removed"])
            cells.append(dist)
        lines.append("| %s | %.2f px | %.2f px | %.2f px | %s |" % (
            version, *cells, " / ".join("%.0f%%" % (100 * r) for r in removed)))
    lines.append("")


def corrector_v3_part(lines, split="val"):
    """v1 vs v3 per tremor size, gated by detector v2 like the app. split = val or test."""
    data = np.load(DERIVED / f"corrector_{split}.npz")
    shaky, clean = data["shaky"], data["clean"]
    tremor = data["tremor"].astype(bool)
    gate = detector_gate(Detector(), shaky)[..., None]
    title = "validation" if split == "val" else "TEST (scored once)"
    lines += ["## Corrector: v1 vs v3 (plain-distance training), %s, gated by detector v2" % title, "",
              "| Version | Sequences | Off the path moving / still (px) | Tremor removed | Lag (ms) |",
              "|---|---|---|---|---|"]
    for version, path in [("v1", "weights.pt"), ("v3", "weights_v3.pt")]:
        out = shaky + gate * corrector_offsets(load_corrector(MODELS / "corrector" / path), shaky)
        steady = np.linalg.norm(out[~tremor][:, SKIP:] - clean[~tremor][:, SKIP:], axis=2).mean()
        for name, lo, hi in [("all with marked tremor", 0, 1e9)] + SIZE_CLASSES:
            m = tremor & (data["strength_px"] >= lo) & (data["strength_px"] < hi)
            s = corrector_scores(out[m], clean[m], shaky[m], skip=SKIP)
            lines.append("| %s | %s (%d) | %.2f / %.2f | %.0f%% | %.0f |" % (
                version, name, m.sum(), s["distance_moving"], s["distance_still"],
                100 * s["tremor_removed"], s["lag_ms"]))
        lines.append("| %s | without marked tremor (%d) | %.2f overall | | |" % (
            version, (~tremor).sum(), steady))
    none_steady = np.linalg.norm(shaky[~tremor][:, SKIP:] - clean[~tremor][:, SKIP:], axis=2).mean()
    lines += ["", "No filter on the sequences without marked tremor: %.2f px." % none_steady, ""]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="also score the kept versions on test (once)")
    args = parser.parse_args()
    torch.set_num_threads(4)
    lines = ["# Step 12: one measured improvement to each model", "",
             "Produced by `python evaluation/improvements.py%s`. Settings and the keep/drop choice "
             "use validation people only." % (" --test" if args.test else ""), ""]
    sets, det = detector_part(lines, args.test)
    corrector_part(lines)
    corrector_v3_part(lines, "val")
    if args.test:
        corrector_v3_part(lines, "test")

    if args.test:
        lines += ["## Kept versions on TEST people (scored once)", ""]
        lines += ["| Detector | Data | Missed cases | False alarms |", "|---|---|---|---|"]
        for version in ["v1", "v2"]:
            cut, scores = det[version]
            for name, label in [("test", "test, normal"), ("test_continuous", "test, pause-free")]:
                s = detector_scores(sets[name]["label"], scores[name] >= cut)
                lines.append("| %s | %s | %s | %s |" % (version, label, pct(s["missed"]), pct(s["false_alarms"])))
        lines.append("")
    lines += ["This project is a prototype and is not medical advice.", ""]
    RESULT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
