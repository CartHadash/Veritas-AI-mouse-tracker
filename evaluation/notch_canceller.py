"""
notch_canceller.py - does a canceller tuned to the person's tremor rhythm beat our corrector?
(Idea: "measure the person's tremor, then stabilise it")

The detector measures the tremor's rhythm (peak frequency, 3-12 Hz) every 0.1 s from the last
2.56 s. A notch filter (models/corrector/notch.py) removes a narrow band around that rhythm and
lets slow, deliberate movement through. Like our corrector, it is applied only as much as the
detector's gate is open. Candidates, each with a narrow, medium or wide notch (Q = 4, 2, 1):
  - the notch alone, on the raw cursor;
  - our corrector (v4, penalty 2, the app's) followed by the notch.

THE RULE (fixed before looking at any result): on VALIDATION sequences with marked tremor, a
candidate replaces the current corrector only if it is closer to the intended path both while
moving and while still, with a lag of at most 20 ms and jerkiness no higher than the current
corrector's. Among those, the one closest while moving wins. If none qualifies, nothing changes.
With --test, the winner (if any) is scored once on TEST people.

Run from the repository folder (a few minutes):
    python evaluation/notch_canceller.py
    python evaluation/notch_canceller.py --test
Writes evaluation/results/notch_canceller.md.
"""

import argparse
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
# The network these results were recorded with (the app's corrector then: v4, penalty 2).
PINNED_WEIGHTS = ROOT / "models" / "corrector" / "weights_v4_s2.pt"
sys.path.insert(0, str(ROOT))
from evaluation.evaluate_corrector import SKIP, corrector_offsets  # noqa: E402
from evaluation.metrics import corrector_scores, jerkiness  # noqa: E402
from models.corrector.live import GATE_SECONDS, WEIGHTS, gate_target, load_corrector  # noqa: E402
from models.corrector.notch import TremorNotch  # noqa: E402
from models.detector.features import FEATURE_NAMES, compute_features  # noqa: E402
from models.detector.predict import WINDOW, Detector  # noqa: E402

DERIVED = ROOT / "data" / "derived"
RESULT = ROOT / "evaluation" / "results" / "notch_canceller.md"
CURRENT = "Our corrector (v4, penalty 2; the app)"
QS = [4.0, 2.0, 1.0]
MAX_LAG_MS = 20


def gate_and_rhythm(detector, shaky):
    """Per sample: the smooth 0-1 gate (as the app computes it) and the latest measured rhythm."""
    n, length = shaky.shape[:2]
    ticks = list(range(WINDOW - 1, length, 10))
    windows = np.stack([shaky[:, t - WINDOW + 1:t + 1] for t in ticks], axis=1)
    features = compute_features(windows.reshape(-1, WINDOW, 2))
    scores = detector.classifier.predict_proba(features)[:, 1].reshape(n, len(ticks))
    rhythm = features[:, FEATURE_NAMES.index("peak frequency in 3-12 Hz")].reshape(n, len(ticks))
    gate = np.zeros((n, length))
    hz = np.full((n, length), np.nan)
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
            if k >= 0:
                hz[i, t] = rhythm[i, k]
    return gate, hz


def notched(cursor, hz, q):
    """Run the notch over every sequence, sample by sample."""
    out = np.empty_like(cursor)
    for i, seq in enumerate(cursor):
        f = TremorNotch(q=q)
        for t, (x, y) in enumerate(seq):
            r = None if np.isnan(hz[i, t]) else float(hz[i, t])
            out[i, t] = f.update(float(x), float(y), r)
    return out


def candidates(split, only=None):
    data = np.load(DERIVED / f"corrector_{split}.npz")
    shaky, clean, tremor = data["shaky"], data["clean"], data["tremor"].astype(bool)
    detector = Detector()
    gate, hz = gate_and_rhythm(detector, shaky)
    g = gate[..., None]
    ours = shaky + g * corrector_offsets(load_corrector(PINNED_WEIGHTS), shaky)
    outs = {"No filter": shaky, CURRENT: ours}
    for q in QS:
        for base_name, base in [("Notch", shaky), ("Our corrector + notch", ours)]:
            name = "%s, Q=%g" % (base_name, q)
            if only is None or name in only:
                outs[name] = base + g * (notched(base, hz, q) - base)
    return outs, shaky, clean, tremor


HEADER = ["| Method | Off the path moving / still (px) | Tremor removed | Lag (ms) | Jerkiness (px) "
          "| No marked tremor: off the path (px) |", "|---|---|---|---|---|---|"]


def table(outs, shaky, clean, tremor):
    scores, rows = {}, []
    for name, out in outs.items():
        s = corrector_scores(out[tremor], clean[tremor], shaky[tremor], skip=SKIP)
        scores[name] = s
        steady = np.linalg.norm(out[~tremor][:, SKIP:] - clean[~tremor][:, SKIP:], axis=2).mean()
        rows.append("| %s | %.2f / %.2f | %.0f%% | %.0f | %.2f | %.2f |" % (
            name, s["distance_moving"], s["distance_still"], 100 * s["tremor_removed"], s["lag_ms"],
            s["jerkiness"], steady))
    return scores, rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()

    outs, shaky, clean, tremor = candidates("val")
    scores, rows = table(outs, shaky, clean, tremor)
    cur = scores[CURRENT]
    qualifying = [n for n, s in scores.items() if n not in ("No filter", CURRENT)
                  and s["distance_moving"] < cur["distance_moving"] and s["distance_still"] < cur["distance_still"]
                  and s["lag_ms"] <= MAX_LAG_MS and s["jerkiness"] <= cur["jerkiness"]]
    winner = min(qualifying, key=lambda n: scores[n]["distance_moving"]) if qualifying else None

    lines = ["# A canceller tuned to the person's tremor rhythm (notch filter): validation first", "",
             "Produced by `python evaluation/notch_canceller.py%s`. Sequences with marked tremor, gated by "
             "detector v2 as in the app, scored after 2.56 s. The notch is centred on the rhythm the "
             "detector measures every 0.1 s; Q sets its width." % (" --test" if args.test else ""), "",
             "## Validation (%d sequences with marked tremor)" % tremor.sum(), ""] + HEADER + rows + [
             "", "Rule fixed in advance: replace the current corrector only if closer to the path both "
             "while moving and still, lag at most %d ms, jerkiness no higher; then the closest while moving." % MAX_LAG_MS,
             "", "**Result: %s**" % ("%s qualifies and wins." % winner if winner else
                                     "no candidate qualifies; the app keeps its corrector."), ""]
    if args.test and winner:
        outs, shaky, clean, tremor = candidates("test", only={winner})
        outs = {n: o for n, o in outs.items() if n in ("No filter", CURRENT, winner)}
        _, rows = table(outs, shaky, clean, tremor)
        lines += ["## Test (scored once; %d sequences with marked tremor)" % tremor.sum(), ""] + HEADER + rows + [""]
    lines += ["This project is a prototype and is not medical advice.", ""]
    RESULT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
