"""
vs_one_euro.py - an extensive comparison of our model with One Euro, the way a person SEES it.
(Team request, Sat 14 Nov 23:14: "our model doesn't work at all compared with One Euro".)

Earlier evaluations mostly scored distance from the intended path. That favours our model,
because One Euro lags behind a moving hand. What the eye notices is shaking and jitter, so
this script measures four things for every filter, through the demo page's own server code
with replayed tremor, at browser-like timing (about 60 uneven samples per second):

  distance  average distance from the intended path (px)
  shake     size of the leftover 3-12 Hz wobble (RMS, px): what looks like "shaking"
  jerk      average change in velocity from one 10 ms step to the next (px): "jumpiness"
  lag       how far behind the hand the cursor runs while moving (ms; reaches and glide)

Filters: no filter, One Euro (original settings), our model (the app's), and our model with
One Euro smoothing on top, applied only as much as our detector's gate is open.

Whose tremor (--people): val (default; development) or test (report once).
Run from the repository folder (a few minutes):
    python evaluation/vs_one_euro.py
Writes evaluation/results/vs_one_euro_<people>.md.
"""

import argparse
import sys
from pathlib import Path

import numpy as np
from scipy.signal import butter, filtfilt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import evaluation.compare_modes as cm  # noqa: E402
import server.main as server  # noqa: E402
from baselines.classical_filters import OneEuroFilter  # noqa: E402
from evaluation.metrics import estimate_lag_ms, jerkiness, moving_mask  # noqa: E402

RATE = 100
BAND_B, BAND_A = butter(4, [3, 12], btype="bandpass", fs=RATE)   # for measuring only (not live)
METHODS = ["No filter", "One Euro", "Our model", "Our model + One Euro"]


def even(positions, t):
    """Place the positions on an even 100 Hz grid after the warm-up (for fair measuring)."""
    grid = np.arange(cm.WARMUP, t[-1], 1 / RATE)
    return np.stack([np.interp(grid, t, positions[:, k]) for k in range(2)], axis=1), grid


def measure(out, path, t, moving):
    o, _ = even(out, t)
    p, _ = even(path, t)
    error = o - p
    shake = float(np.sqrt((filtfilt(BAND_B, BAND_A, error, axis=0) ** 2).sum(axis=1).mean()))
    result = {"distance": float(np.linalg.norm(error, axis=1).mean()), "shake": shake, "jerk": jerkiness(o)}
    if moving:
        result["lag"] = estimate_lag_ms(o[None], p[None], moving_mask(p[None]))
    return result


def gated_one_euro(ours, gate, t):
    f = OneEuroFilter()
    smooth = np.array([f.update(float(x), float(y), float(ti)) for (x, y), ti in zip(ours, t)])
    g = np.nan_to_num(gate)[:, None]
    return ours + g * (smooth - ours)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--people", choices=["val", "test"], default="val")
    args = parser.parse_args()
    server.DEMO_TREMOR_FILE = cm.DEMO_FILES[args.people]
    t, paths = cm.intended_paths(rate=60, uneven=True)

    lines = ["# Our model vs One Euro, as a person sees it (%s people's replayed tremor)" % (
                 "validation" if args.people == "val" else "test"), "",
             "Produced by `python evaluation/vs_one_euro.py --people %s`. Demo page server code, browser-like "
             "timing (about 60 uneven samples per second), %d s per run, scored after %.0f s. distance = from "
             "the intended path; shake = leftover 3-12 Hz wobble (RMS); jerk = change in velocity per 10 ms "
             "step; lag = how far behind a moving hand. All in px except lag (ms)." % (
                 args.people, cm.SECONDS, cm.WARMUP), "",
             "| Tremor | Movement | Method | Distance | Shake | Jerk | Lag |", "|---|---|---|---|---|---|---|"]
    totals = {m: {"shake": [], "distance": [], "jerk": []} for m in METHODS}
    for level in ["mild", "medium", "strong"]:
        for name in ["reaches", "glide", "still"]:
            path = paths[name]
            none, _ = cm.run("none", t, path, level=level)
            euro, _ = cm.run("one_euro", t, path, level=level)
            ours, gate = cm.run("learned", t, path, level=level)
            outs = {"No filter": none, "One Euro": euro, "Our model": ours,
                    "Our model + One Euro": gated_one_euro(ours, gate, t)}
            for method, out in outs.items():
                m = measure(out, path, t, moving=(name != "still"))
                for k in totals[method]:
                    totals[method][k].append(m[k])
                lines.append("| %s | %s | %s | %.2f | %.2f | %.2f | %s |" % (
                    level, name, method, m["distance"], m["shake"], m["jerk"],
                    "%.0f" % m["lag"] if "lag" in m else "-"))
                print(lines[-1])
    lines += ["", "## Average over all 9 situations", "", "| Method | Distance | Shake | Jerk |", "|---|---|---|---|"]
    for method in METHODS:
        lines.append("| %s | %.2f | %.2f | %.2f |" % (method, *(np.mean(totals[method][k]) for k in ("distance", "shake", "jerk"))))
    lines += ["", "This project is a prototype and is not medical advice.", ""]
    (ROOT / "evaluation" / "results" / f"vs_one_euro_{args.people}.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[-9:]))


if __name__ == "__main__":
    main()
