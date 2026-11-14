"""
option_b.py - does a corrector retrained to aim at what the eye sees beat the app's (option A)?

Option B (team's choice, Sat 14 Nov): retrain the network with an extra penalty on the cursor's
error wobbling around its own average over 0.3 s (models/corrector/train.py --shake K), which is
close to the "shake" a person sees. Each candidate network is run the way the app would run it:
with the gated One Euro smoothing of option A, through the demo page's own code, over the same
nine situations as evaluation/vs_one_euro.py (mild/medium/strong tremor x reaching/gliding/still,
browser-like timing).

THE RULE (fixed before training): a candidate replaces the app's network only if, on
VALIDATION people's replayed tremor, both its average shake and its average jerk are lower than
option A's, and its average distance is at most 5% higher. Among those, the lowest shake wins.
With --test, the winner (if any) is scored once on TEST people next to option A.

Run from the repository folder (after training the candidates; a few minutes each):
    python evaluation/option_b.py
    python evaluation/option_b.py --test
Writes evaluation/results/option_b.md.
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
from models.corrector.live import VERSION, load_corrector  # noqa: E402

CORRECTOR = ROOT / "models" / "corrector"
RESULT = ROOT / "evaluation" / "results" / "option_b.md"
CANDIDATES = ["v5_k1", "v5_k3"]
MAX_DISTANCE_INCREASE = 0.05


def averages(version, people):
    """Average distance, shake and jerk of the app's pipeline with this network."""
    server.DEMO_TREMOR_FILE = cm.DEMO_FILES[people]
    server.CORRECTOR_MODEL = load_corrector(CORRECTOR / f"weights_{version}.pt")
    t, paths = cm.intended_paths(rate=60, uneven=True)
    rows = []
    for level in ["mild", "medium", "strong"]:
        for name in ["reaches", "glide", "still"]:
            out, _ = cm.run("learned", t, paths[name], level=level)
            rows.append(measure(out, paths[name], t, moving=False))
    return {k: float(np.mean([r[k] for r in rows])) for k in ("distance", "shake", "jerk")}


def table(results):
    lines = ["| Network (with the app's gated One Euro smoothing) | Distance | Shake | Jerk |", "|---|---|---|---|"]
    for name, r in results.items():
        lines.append("| %s | %.2f | %.2f | %.2f |" % (name, r["distance"], r["shake"], r["jerk"]))
    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    current = "%s (option A, the app)" % VERSION
    val = {current: averages(VERSION, "val")}
    for c in CANDIDATES:
        if (CORRECTOR / f"weights_{c}.pt").exists():
            val[c] = averages(c, "val")
    a = val[current]
    qualifying = [c for c in val if c != current and val[c]["shake"] < a["shake"] and val[c]["jerk"] < a["jerk"]
                  and val[c]["distance"] <= (1 + MAX_DISTANCE_INCREASE) * a["distance"]]
    winner = min(qualifying, key=lambda c: val[c]["shake"]) if qualifying else None

    lines = ["# Option B: a corrector retrained to aim at what the eye sees", "",
             "Produced by `python evaluation/option_b.py%s`. Averages over mild/medium/strong replayed tremor x "
             "reaching/gliding/still, demo page code, browser-like timing (as `vs_one_euro.py`). Candidates "
             "trained with `models/corrector/train.py --loss distance --smooth 2 --shake K` (v5_kK)." % (
                 " --test" if args.test else ""), "",
             "## Validation people", ""] + table(val) + [
             "", "Rule fixed before training: replace option A only if shake and jerk are both lower and "
             "distance at most 5% higher; then the lowest shake.", "",
             "**Result: %s**" % ("%s qualifies and wins." % winner if winner else
                                 "no candidate qualifies; the app keeps option A."), ""]
    if args.test and winner:
        test = {current: averages(VERSION, "test"), winner: averages(winner, "test")}
        lines += ["## Test people (scored once)", ""] + table(test) + [""]
    lines += ["This project is a prototype and is not medical advice.", ""]
    RESULT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
