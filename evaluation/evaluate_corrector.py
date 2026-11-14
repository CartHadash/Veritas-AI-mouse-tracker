"""
evaluate_corrector.py - step 8: score corrector v1 ONCE on TEST people, next to the baselines.

Everything is computed exactly as live.py would do it, but for all test sequences at once:
  - the corrector's offset at every sample from the 64 steps before it;
  - the detector's score every 10 samples on the last 2.56 s, turned into the smooth gate.
Because the detector needs 2.56 s of history, the first 2.56 s of every 5.12 s sequence are
ignored for ALL methods (so every row is scored on the same samples).

Run from the repository folder (about a minute):
    python evaluation/evaluate_corrector.py                  # gate = detector v1 (step 8)
    python evaluation/evaluate_corrector.py --detector v2     # gate = detector v2 (step 12, the app)
Writes evaluation/results/corrector_v1.md (or corrector_v1_gate_v2.md).
"""

import argparse
import math
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from baselines.classical_filters import MovingAverageFilter, OneEuroFilter  # noqa: E402
from evaluation.metrics import CORRECTOR_SKIP, SIZE_CLASSES, corrector_scores, run_filter  # noqa: E402
from models.corrector.live import GATE_SECONDS, gate_target, load_corrector  # noqa: E402
from models.corrector.model import HISTORY  # noqa: E402
from models.detector.features import compute_features  # noqa: E402
from models.detector.predict import MODEL_FILE, Detector  # noqa: E402

DERIVED = ROOT / "data" / "derived"
RESULTS = ROOT / "evaluation" / "results"
SKIP = CORRECTOR_SKIP  # detector warm-up: score only after 2.56 s
WINDOW = 256

# One Euro settings chosen on validation by evaluation/run_baselines.py (see baselines.md).
# Copied by hand: if run_baselines.py is re-run and picks different settings, update this.
ONE_EURO_TUNED = dict(min_cutoff=2.0, beta=0.03)


def corrector_offsets(model, shaky):
    """Offset (px) the network wants at every sample; 0 before 64 samples of history."""
    steps = np.zeros_like(shaky)
    steps[:, 1:] = shaky[:, 1:] - shaky[:, :-1]
    steps = torch.from_numpy(steps)
    offsets = np.zeros_like(shaky)
    index = torch.arange(-HISTORY + 1, 1)
    with torch.inference_mode():
        for t in range(HISTORY, shaky.shape[1]):
            offsets[:, t] = model(steps[:, t + index]).numpy()
    return offsets


def detector_gate(detector, shaky):
    """The smooth 0-1 gate at every sample, as LiveCorrector computes it live."""
    n, length = shaky.shape[:2]
    ticks = list(range(WINDOW - 1, length, 10))
    windows = np.stack([shaky[:, t - WINDOW + 1:t + 1] for t in ticks], axis=1)   # (n, ticks, 256, 2)
    scores = detector.classifier.predict_proba(
        compute_features(windows.reshape(-1, WINDOW, 2)))[:, 1].reshape(n, len(ticks))
    gate = np.zeros((n, length))
    alpha = 1 - math.exp(-(1 / 100) / GATE_SECONDS)
    for i in range(n):
        g, k, target = 0.0, -1, 0.0
        for t in range(length):
            if k + 1 < len(ticks) and t == ticks[k + 1]:
                k += 1
                target = gate_target(scores[i, k], detector.threshold)
            if t > 0:
                g += (target - g) * alpha
            gate[i, t] = g
    return gate


def row(name, output, clean, shaky, tremor, note=""):
    t, n = tremor, ~tremor
    s = corrector_scores(output[t], clean[t], shaky[t], skip=SKIP)
    steady = np.linalg.norm(output[n][:, SKIP:] - clean[n][:, SKIP:], axis=2).mean()
    return "| %s | %.2f | %.2f | %.0f%% | %.0f | %.2f | %s |" % (
        name, s["distance_moving"], s["distance_still"], 100 * s["tremor_removed"],
        s["lag_ms"], steady, note)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--detector", default="v1", help="which detector version gates the corrector")
    args = parser.parse_args()
    data = np.load(DERIVED / "corrector_test.npz")
    shaky, clean = data["shaky"], data["clean"]
    tremor = data["tremor"].astype(bool)
    print("Test sequences: %d (%d with marked tremor)" % (len(shaky), tremor.sum()))

    offsets = corrector_offsets(load_corrector(ROOT / "models" / "corrector" / "weights.pt"), shaky)   # v1
    detector = Detector(MODEL_FILE.with_name(f"detector_{args.detector}.joblib"),
                        MODEL_FILE.with_name(f"detector_{args.detector}_threshold.json"))
    gate = detector_gate(detector, shaky)[..., None]
    print("Running classical filters...")
    one_euro = run_filter(OneEuroFilter, shaky)
    one_euro_tuned = run_filter(lambda: OneEuroFilter(**ONE_EURO_TUNED), shaky)
    moving_average = run_filter(MovingAverageFilter, shaky)
    start = shaky[:, :1]

    header = ["| Method | Distance while moving (px) | Distance while still (px) | Tremor removed "
              "| Lag (ms) | Distance on sequences without marked tremor (px) | Notes |",
              "|---|---|---|---|---|---|---|"]
    rows = [
        row("No filter", shaky, clean, shaky, tremor),
        row("Lower sensitivity x0.5", start + 0.5 * (shaky - start), start + 0.5 * (clean - start),
            shaky, tremor, "hand must travel 2x as far"),
        row("Moving average 0.2 s (original)", moving_average, clean, shaky, tremor),
        row("One Euro (original settings)", one_euro, clean, shaky, tremor),
        row("One Euro (tuned on validation)", one_euro_tuned, clean, shaky, tremor),
        row("One Euro (original) + detector gate", shaky + gate * (one_euro - shaky), clean, shaky,
            tremor, "classical filter switched by our detector"),
        row("Corrector v1, always on", shaky + offsets, clean, shaky, tremor, "our network alone"),
        row("**Corrector v1 + detector gate**", shaky + gate * offsets, clean, shaky, tremor,
            "**our system: both models together**"),
    ]

    # Tremor removed and distance while still, by tremor size, for the key methods.
    strength = data["strength_px"]
    size_rows = ["| Tremor size | Sequences | Still: no filter | Still: One Euro (orig.) + gate "
                 "| Still: our system | Removed: One Euro (orig.) + gate | Removed: our system |",
                 "|---|---|---|---|---|---|---|"]
    ours, oe_gated = shaky + gate * offsets, shaky + gate * (one_euro - shaky)
    for name, lo, hi in [("mild (under 3 px)", 0, 3), ("medium (3-10 px)", 3, 10), ("strong (over 10 px)", 10, 1e9)]:
        m = tremor & (strength >= lo) & (strength < hi)
        if m.sum() == 0:
            continue
        a = corrector_scores(shaky[m], clean[m], shaky[m], skip=SKIP)
        b = corrector_scores(oe_gated[m], clean[m], shaky[m], skip=SKIP)
        c = corrector_scores(ours[m], clean[m], shaky[m], skip=SKIP)
        size_rows.append("| %s | %d | %.2f | %.2f | %.2f | %.0f%% | %.0f%% |" % (
            name, m.sum(), a["distance_still"], b["distance_still"], c["distance_still"],
            100 * b["tremor_removed"], 100 * c["tremor_removed"]))

    lines = ["# Corrector v1 (gate: detector %s): results on TEST people" % args.detector, "",
             "Produced by `python evaluation/evaluate_corrector.py%s`. Test sequences: %d (%d with "
             "marked tremor, %d without). Scored after the first 2.56 s of each 5.12 s sequence "
             "(the detector's warm-up), the same samples for every method. Distances, tremor "
             "removed and lag are on sequences with marked tremor; the last column is the "
             "average distance on sequences without marked tremor." % (
                 "" if args.detector == "v1" else " --detector " + args.detector,
                 len(shaky), tremor.sum(), (~tremor).sum()), ""] + header + rows + [
             "", "## By tremor size (sequences with marked tremor)", ""] + size_rows + [
             "", "This project is a prototype and is not medical advice.", ""]
    name = "corrector_v1.md" if args.detector == "v1" else f"corrector_v1_gate_{args.detector}.md"
    (RESULTS / name).write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
