"""
smoother_output.py - can the corrected cursor be made less jittery? (team leader's request,
Sat 14 Nov 21:35: "closer than One Euro but still fast and jittery")

Candidates, all built on the app's corrector v4 (penalty 0.5) gated by detector v2:
  - extra smoothing of the corrected cursor by a One Euro filter (cut-off 2, 4, 8 or 16 Hz) or
    by a short moving average (30 or 50 ms). The extra smoothing is applied only as much as the
    correction itself is on (the detector's gate), so a steady hand gets no added lag;
  - the stronger-penalty correctors already trained in step 12 (v4 with S = 2 and S = 8).

THE RULE (fixed before looking at any result): on VALIDATION sequences with marked tremor, keep
the candidate with the LOWEST jerkiness among those with a lag of at most 20 ms and a distance
from the path while moving at most 10% above the current corrector's. The current corrector
always qualifies, so if nothing is better it stays. With --test, score the choice on TEST
people once, next to no filter, One Euro and the current corrector.

Run from the repository folder (a few minutes):
    python evaluation/smoother_output.py
    python evaluation/smoother_output.py --test
Writes evaluation/results/smoother_output.md.
"""

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from baselines.classical_filters import MovingAverageFilter, OneEuroFilter  # noqa: E402
from evaluation.evaluate_corrector import SKIP, corrector_offsets, detector_gate  # noqa: E402
from evaluation.metrics import corrector_scores, jerkiness, run_filter  # noqa: E402
from models.corrector.live import load_corrector  # noqa: E402
from models.detector.predict import Detector  # noqa: E402

DERIVED = ROOT / "data" / "derived"
CORRECTOR = ROOT / "models" / "corrector"
RESULT = ROOT / "evaluation" / "results" / "smoother_output.md"
CURRENT = "Corrector v4, penalty S=0.5 (the app's corrector when this was chosen)"
MAX_LAG_MS = 20
MAX_DISTANCE_INCREASE = 0.10

# name -> how to make the extra smoothing filter (None = no extra smoothing)
POST_FILTERS = {"+ One Euro 2 Hz": lambda: OneEuroFilter(min_cutoff=2.0, beta=0.01),
                "+ One Euro 4 Hz": lambda: OneEuroFilter(min_cutoff=4.0, beta=0.01),
                "+ One Euro 8 Hz": lambda: OneEuroFilter(min_cutoff=8.0, beta=0.01),
                "+ One Euro 16 Hz": lambda: OneEuroFilter(min_cutoff=16.0, beta=0.01),
                "+ average of 30 ms": lambda: MovingAverageFilter(window=0.03),
                "+ average of 50 ms": lambda: MovingAverageFilter(window=0.05)}


def outputs_for(split, only=None):
    """Every candidate's cursor on one split (or only the names in `only`)."""
    data = np.load(DERIVED / f"corrector_{split}.npz")
    shaky, clean = data["shaky"], data["clean"]
    gate = detector_gate(Detector(), shaky)[..., None]
    v4 = shaky + gate * corrector_offsets(load_corrector(CORRECTOR / "weights_v4_s0.5.pt"), shaky)
    outs = {"No filter": shaky, "One Euro (original settings)": run_filter(OneEuroFilter, shaky), CURRENT: v4}
    for name, make in POST_FILTERS.items():
        if only is None or "v4 " + name in only:
            smoothed = run_filter(make, v4)
            outs["v4 " + name] = v4 + gate * (smoothed - v4)
    for s in ["2", "8"]:
        name = "Corrector v4, penalty S=%s" % s
        if only is None or name in only:
            outs[name] = shaky + gate * corrector_offsets(load_corrector(CORRECTOR / f"weights_v4_s{s}.pt"), shaky)
    return outs, clean, shaky, data["tremor"].astype(bool)


def table(outs, clean, shaky, tremor):
    scores, rows = {}, []
    for name, out in outs.items():
        s = corrector_scores(out[tremor], clean[tremor], shaky[tremor], skip=SKIP)
        steady = out[~tremor][:, SKIP:]
        scores[name] = s
        rows.append("| %s | %.2f / %.2f | %.0f%% | %.0f | %.2f | %.2f / %.2f |" % (
            name, s["distance_moving"], s["distance_still"], 100 * s["tremor_removed"], s["lag_ms"],
            s["jerkiness"], np.linalg.norm(steady - clean[~tremor][:, SKIP:], axis=2).mean(), jerkiness(steady)))
    return scores, rows


HEADER = ["| Method | Off the path moving / still (px) | Tremor removed | Lag (ms) | Jerkiness (px) "
          "| No marked tremor: off the path / jerkiness (px) |", "|---|---|---|---|---|---|"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()

    outs, clean, shaky, tremor = outputs_for("val")
    scores, rows = table(outs, clean, shaky, tremor)
    limit = (1 + MAX_DISTANCE_INCREASE) * scores[CURRENT]["distance_moving"]
    qualifying = [n for n in scores if (n == CURRENT or n.startswith("Corrector v4, ") or n.startswith("v4 + "))
                  and scores[n]["lag_ms"] <= MAX_LAG_MS and scores[n]["distance_moving"] <= limit]
    chosen = min(qualifying, key=lambda n: scores[n]["jerkiness"])

    lines = ["# A smoother corrected cursor: choosing on validation", "",
             "Produced by `python evaluation/smoother_output.py%s`. Sequences with marked tremor, gated by "
             "detector v2 as in the app, scored after 2.56 s. Jerkiness = average size of the change in "
             "cursor velocity from one 10 ms sample to the next (px). Extra smoothing is applied only as "
             "much as the correction is on." % (" --test" if args.test else ""), "",
             "## Validation (%d sequences with marked tremor)" % tremor.sum(), ""] + HEADER + rows + [
             "", "Rule fixed in advance: lowest jerkiness with lag at most %d ms and distance while moving at "
             "most %.2f px (10%% above the current corrector's %.2f px)." % (
                 MAX_LAG_MS, limit, scores[CURRENT]["distance_moving"]),
             "", "**Chosen: %s** (jerkiness %.2f px, lag %.0f ms)." % (
                 chosen, scores[chosen]["jerkiness"], scores[chosen]["lag_ms"]), ""]

    if args.test:
        keep = {"No filter", "One Euro (original settings)", CURRENT, chosen}
        outs, clean, shaky, tremor = outputs_for("test", only=keep)
        outs = {n: o for n, o in outs.items() if n in keep}
        _, rows = table(outs, clean, shaky, tremor)
        lines += ["## Test (scored once, after choosing on validation; %d sequences with marked tremor)" % tremor.sum(),
                  ""] + HEADER + rows + [""]
    lines += ["This project is a prototype and is not medical advice.", ""]
    RESULT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
