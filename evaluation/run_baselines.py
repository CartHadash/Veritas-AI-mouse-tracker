"""
run_baselines.py - score the simplest possible approaches, so judges can see how
much our AI models add on top of them.

DETECTOR baselines (2.56 s windows):
  1. Always "no tremor".
  2. Frequency rule: "tremor" when enough of the window's movement (its sample-to-sample
     steps, i.e. velocity) lies between 3 and 12 Hz. The cut-off is chosen on VALIDATION
     only, at two operating points: best balance of missed cases and false alarms, and
     fewest false alarms with missed cases at most 10% (the cut-off rule used for our detector).

CORRECTOR baselines (5.12 s sequences):
  1. No filter.
  2. Lower pointer sensitivity: the cursor moves 1/2 (or 1/4) as far as the hand. Scored
     against the intended path scaled the same way. Its cost is extra hand travel (2x / 4x).
  3. The three classical filters in baselines/classical_filters.py (moving average, One Euro,
     Kalman). Each one's settings are chosen from a small list on VALIDATION only (lowest
     average distance to the intended path), then scored once on test.

Run from the repository folder (about 3-4 minutes):
    python evaluation/run_baselines.py
Writes evaluation/results/baselines.md.
"""

import itertools
import sys
from pathlib import Path

import numpy as np
from scipy.signal import periodogram

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from baselines.classical_filters import KalmanFilter, MovingAverageFilter, OneEuroFilter  # noqa: E402
from evaluation.metrics import (RATE, choose_threshold, corrector_scores,  # noqa: E402
                                detector_scores, run_filter)

DERIVED = ROOT / "data" / "derived"
RESULTS = ROOT / "evaluation" / "results" / "baselines.md"


def load(name):
    return dict(np.load(DERIVED / f"{name}.npz"))


# ---------------------------------------------------------------- detector

def band_share(windows):
    """Share of each window's movement (velocity) power that lies in 3-12 Hz."""
    steps = np.diff(windows, axis=1)                         # sample-to-sample movement
    freqs, power = periodogram(steps, fs=RATE, axis=1, detrend="constant")
    power = power.sum(axis=2)                                # add x and y
    band = (freqs >= 3) & (freqs <= 12)
    return power[:, band].sum(axis=1) / (power[:, freqs >= 0.5].sum(axis=1) + 1e-12)


def detector_rows(name, predict, data):
    """Score one detector overall and on moving / still windows."""
    rows = []
    for subset, mask in [("all", np.ones(len(data["label"]), bool)),
                         ("hand moving", data["moving"]), ("hand still", ~data["moving"])]:
        s = detector_scores(data["label"][mask], predict[mask])
        rows.append("| %s | %s | %.1f%% | %.1f%% | %.1f%% |" % (
            name, subset, 100 * s["missed"], 100 * s["false_alarms"], 100 * s["accuracy"]))
    return rows


def detector_baselines(lines):
    val, test = load("detector_val"), load("detector_test")
    val_share, test_share = band_share(val["xy"]), band_share(test["xy"])
    cut_balanced = choose_threshold(val_share, val["label"])
    cut_10 = choose_threshold(val_share, val["label"], max_missed=0.10)

    lines += ["## Detector baselines", "",
              "Missed cases = real tremor windows called \"no tremor\". False alarms = no-tremor "
              "windows called \"tremor\". Cut-offs chosen on validation only.", "",
              "Frequency rule cut-offs (share of movement power in 3-12 Hz): balanced %.3f; "
              "missed <= 10%% on validation %.3f." % (cut_balanced, cut_10), ""]
    for split_name, data, share in [("Validation", val, val_share), ("Test", test, test_share)]:
        lines += ["### %s (%d windows: %d tremor, %d no tremor)" % (
            split_name, len(data["label"]), data["label"].sum(), (data["label"] == 0).sum()), "",
            "| Detector | Windows | Missed cases | False alarms | Accuracy |", "|---|---|---|---|---|"]
        lines += detector_rows("Always \"no tremor\"", np.zeros(len(share), bool), data)
        lines += detector_rows("Frequency rule (balanced)", share >= cut_balanced, data)
        lines += detector_rows("Frequency rule (missed <= 10% on val)", share >= cut_10, data)
        lines.append("")


# ---------------------------------------------------------------- corrector

GRIDS = {
    "Moving average": (MovingAverageFilter, {"window": [0.1, 0.15, 0.2, 0.25, 0.3]}),
    "One Euro": (OneEuroFilter, {"min_cutoff": [0.3, 0.6, 1.0, 2.0], "beta": [0.001, 0.004, 0.01, 0.03]}),
    "Kalman": (KalmanFilter, {"measurement_std": [3.0, 6.0, 12.0, 24.0], "accel_std": [500.0, 1500.0, 4000.0]}),
}


def tune_on_validation(cls, grid, val):
    """Try every combination of settings on validation; keep the lowest average distance."""
    best, best_error = None, None
    for values in itertools.product(*grid.values()):
        params = dict(zip(grid.keys(), values))
        out = run_filter(lambda: cls(**params), val["shaky"])
        error = np.linalg.norm(out[:, 50:] - val["clean"][:, 50:], axis=2).mean()
        print("    %s %s: %.2f px" % (cls.__name__, params, error))
        if best_error is None or error < best_error:
            best, best_error = params, error
    return best


def corrector_row(name, output, clean, shaky, tremor, extra=""):
    t, n = tremor, ~tremor
    s = corrector_scores(output[t], clean[t], shaky[t])
    steady = np.linalg.norm(output[n][:, 50:] - clean[n][:, 50:], axis=2).mean()
    return "| %s | %.2f | %.2f | %.0f%% | %.0f | %.2f | %s |" % (
        name, s["distance_moving"], s["distance_still"], 100 * s["tremor_removed"],
        s["lag_ms"], steady, extra)


def corrector_baselines(lines):
    val, test = load("corrector_val"), load("corrector_test")
    shaky, clean, tremor = test["shaky"], test["clean"], test["tremor"].astype(bool)
    header = ["| Method | Distance while moving (px) | Distance while still (px) | Tremor removed "
              "| Lag (ms) | Distance on steady-hand sequences (px) | Notes |",
              "|---|---|---|---|---|---|---|"]
    rows = [corrector_row("No filter", shaky, clean, shaky, tremor)]

    # Lower sensitivity: cursor = start + gain * (hand - start); compare with the intended
    # path scaled the same way.
    for gain in (0.5, 0.25):
        start = shaky[:, :1]
        rows.append(corrector_row(
            "Lower sensitivity x%g" % gain, start + gain * (shaky - start),
            start + gain * (clean - start), shaky, tremor,
            "hand must travel %gx as far" % (1 / gain)))

    for name, (cls, grid) in GRIDS.items():
        print("  tuning %s on validation..." % name)
        params = tune_on_validation(cls, grid, val)
        out = run_filter(lambda: cls(**params), shaky)
        rows.append(corrector_row(name, out, clean, shaky, tremor,
                                  "settings chosen on validation: %s" % params))
        default = run_filter(cls, shaky)
        rows.append(corrector_row(name + " (pre-hackathon default settings)", default, clean, shaky, tremor))

    lines += ["## Corrector baselines (test: %d sequences with marked tremor, %d without)" % (
        tremor.sum(), (~tremor).sum()), "",
        "Distances, tremor removed and lag are measured on the sequences with marked tremor; the "
        "\"steady-hand\" column is the average distance on sequences without marked tremor "
        "(a good filter should not make a steady hand worse). The first 0.5 s of each sequence "
        "is ignored so every filter has warmed up. Lag = the delay (0-400 ms) that best lines "
        "the output up with the intended path while moving.", ""] + header + rows + [""]


def main():
    lines = ["# Baselines", "",
             "Produced by `python evaluation/run_baselines.py` (step 6). Do not edit by hand.", ""]
    print("Detector baselines...")
    detector_baselines(lines)
    print("Corrector baselines...")
    corrector_baselines(lines)
    lines += ["This project is a prototype and is not medical advice.", ""]
    RESULTS.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
