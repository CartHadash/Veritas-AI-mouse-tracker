"""
tune_lag.py - make the app's cursor less laggy without letting it shake more.
(By hand: "it feels a bit laggy in places".)

The page and server are fast (median round trip about 1 ms in the browser). The lag comes from
the One Euro smoothing the app adds to our network's cursor: with One Euro's original
settings (min_cutoff 1.0, beta 0.004) it trails a moving hand by tens of milliseconds. beta
decides how quickly smoothing backs off when the pointer moves fast; min_cutoff how smooth a slow
pointer is. This tries a grid of both, through the demo page's own code (the app's network,
gated smoothing, browser-like timing, mild/medium/strong replayed tremor x reaching/gliding/still).

THE RULE (fixed before running it): on VALIDATION people's replayed tremor, among settings whose
average shake and average jerk are each at most 5% above the current app's, choose the one with
the lowest average lag while moving (reaching and gliding); ties go to the lower shake. The
current settings always qualify, so nothing gets worse. With --test, score the choice once on
TEST people next to the current settings.

Run from the repository folder (several minutes):
    python evaluation/tune_lag.py
    python evaluation/tune_lag.py --test
Writes evaluation/results/tune_lag.md.
"""

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import evaluation.compare_modes as cm  # noqa: E402
import server.main as server  # noqa: E402
from evaluation.vs_one_euro import measure  # noqa: E402
from models.corrector.live import SMOOTHING  # noqa: E402

RESULT = ROOT / "evaluation" / "results" / "tune_lag.md"
GRID = [{"min_cutoff": c, "beta": b} for c in (1.0, 2.0, 4.0) for b in (0.004, 0.01, 0.02, 0.05)]
MAX_INCREASE = 0.05


def averages(settings, people):
    """Average distance, shake, jerk over 9 situations and average lag over the moving ones."""
    server.DEMO_TREMOR_FILE = cm.DEMO_FILES[people]
    server.SMOOTH_OUTPUT["settings"] = settings
    try:
        t, paths = cm.intended_paths(rate=60, uneven=True)
        rows, lags = [], []
        for level in ["mild", "medium", "strong"]:
            for name in ["reaches", "glide", "still"]:
                out, _ = cm.run("learned", t, paths[name], level=level)
                m = measure(out, paths[name], t, moving=(name != "still"))
                rows.append(m)
                if "lag" in m:
                    lags.append(m["lag"])
    finally:
        server.SMOOTH_OUTPUT.pop("settings", None)
    result = {k: float(np.mean([r[k] for r in rows])) for k in ("distance", "shake", "jerk")}
    result["lag"] = float(np.mean(lags))
    return result


def name(s):
    return "min_cutoff %g, beta %g" % (s["min_cutoff"], s["beta"])


def table(results):
    lines = ["| Smoothing settings | Lag while moving (ms) | Distance | Shake | Jerk |", "|---|---|---|---|---|"]
    for n, r in results.items():
        lines.append("| %s | %.0f | %.2f | %.2f | %.2f |" % (n, r["lag"], r["distance"], r["shake"], r["jerk"]))
    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    current = name(SMOOTHING) + " (now)"
    val = {current: averages(SMOOTHING, "val")}
    for s in GRID:
        if s != SMOOTHING:
            val[name(s)] = averages(s, "val")
            print(name(s), val[name(s)])
    cur = val[current]
    ok = [n for n, r in val.items() if r["shake"] <= (1 + MAX_INCREASE) * cur["shake"]
          and r["jerk"] <= (1 + MAX_INCREASE) * cur["jerk"]]
    chosen = min(ok, key=lambda n: (val[n]["lag"], val[n]["shake"]))

    lines = ["# Less lag: tuning the app's smoothing (validation first)", "",
             "Produced by `python evaluation/tune_lag.py%s`. The app's network with gated One Euro smoothing, "
             "demo page code, browser-like timing; averages over mild/medium/strong replayed tremor x "
             "reaching/gliding/still (lag: reaching and gliding only)." % (" --test" if args.test else ""), "",
             "## Validation people", ""] + table(val) + [
             "", "Rule fixed in advance: shake and jerk each at most 5% above now; then the lowest lag.", "",
             "**Chosen: %s.**" % chosen, ""]
    if args.test and chosen != current:
        settings = next(s for s in GRID if name(s) == chosen)
        test = {current: averages(SMOOTHING, "test"), chosen: averages(settings, "test")}
        lines += ["## Test people (scored once)", ""] + table(test) + [""]
    lines += ["This project is a prototype and is not medical advice.", ""]
    RESULT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
