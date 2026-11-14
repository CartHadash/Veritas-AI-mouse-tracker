"""
smoothness.py - choose how strongly to penalise a jumpy cursor (corrector v4), fairly.

The team leader saw our corrector look jumpy on the demo page although its distance score was
good. Corrector v4 is trained with an extra penalty on the corrected cursor's jerkiness
(models/corrector/train.py --smooth S). We trained S = 0.5, 2 and 8.

THE RULE (fixed before looking at the results): on VALIDATION sequences with marked tremor,
gated by detector v2 as in the app, pick the SMALLEST S whose jerkiness is at most that of no
filter (our cursor must not be jumpier than doing nothing). Smaller S keeps more accuracy.
If none qualifies, take the least jerky one and say so. Then, with --test, score it on TEST
people once, next to no filter, One Euro, v1 and v3.

Run from the repository folder (after training the three v4 versions):
    python evaluation/smoothness.py
    python evaluation/smoothness.py --test
Writes evaluation/results/smoothness.md.
"""

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from baselines.classical_filters import OneEuroFilter  # noqa: E402
from evaluation.evaluate_corrector import SKIP, corrector_offsets, detector_gate  # noqa: E402
from evaluation.metrics import corrector_scores, jerkiness, run_filter  # noqa: E402
from models.corrector.live import load_corrector  # noqa: E402
from models.detector.predict import Detector  # noqa: E402

DERIVED = ROOT / "data" / "derived"
CORRECTOR = ROOT / "models" / "corrector"
RESULT = ROOT / "evaluation" / "results" / "smoothness.md"
CANDIDATES = [("v1", "weights.pt"), ("v3", "weights_v3.pt"), ("v4, S=0.5", "weights_v4_s0.5.pt"),
              ("v4, S=2", "weights_v4_s2.pt"), ("v4, S=8", "weights_v4_s8.pt"),
              # Added Sun 15 Nov for reporting only (the rule below picks among v4 versions): the
              # network the app uses now, chosen by evaluation/option_b.py.
              ("v5, shake penalty 3 (the app's network)", "weights_v5_k3.pt")]


def score_split(split):
    """All candidates on one split. Returns table rows and {name: jerkiness on tremor sequences}."""
    data = np.load(DERIVED / f"corrector_{split}.npz")
    shaky, clean = data["shaky"], data["clean"]
    tremor = data["tremor"].astype(bool)
    gate = detector_gate(Detector(), shaky)[..., None]
    outputs = {"No filter": shaky, "One Euro (original)": run_filter(OneEuroFilter, shaky)}
    for name, file in CANDIDATES:
        outputs[name] = shaky + gate * corrector_offsets(load_corrector(CORRECTOR / file), shaky)

    rows, jerk = [], {}
    for name, out in outputs.items():
        s = corrector_scores(out[tremor], clean[tremor], shaky[tremor], skip=SKIP)
        steady = out[~tremor][:, SKIP:]
        jerk[name] = s["jerkiness"]
        rows.append("| %s | %.2f / %.2f | %.0f%% | %.0f | %.2f | %.2f / %.2f |" % (
            name, s["distance_moving"], s["distance_still"], 100 * s["tremor_removed"], s["lag_ms"],
            s["jerkiness"], np.linalg.norm(steady - clean[~tremor][:, SKIP:], axis=2).mean(), jerkiness(steady)))
    intended = jerkiness(clean[tremor][:, SKIP:])
    return rows, jerk, intended, tremor.sum(), (~tremor).sum()


HEADER = ["| Method (gated by detector v2) | Off the path moving / still (px) | Tremor removed | Lag (ms) "
          "| Jerkiness (px) | No marked tremor: off the path / jerkiness (px) |", "|---|---|---|---|---|---|"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()

    rows, jerk, intended, n_t, n_s = score_split("val")
    allowed = jerk["No filter"]
    qualifying = [n for n, _ in CANDIDATES if n.startswith("v4") and jerk[n] <= allowed]
    if qualifying:
        chosen = qualifying[0]       # the list is ordered from the smallest S
        reason = "the smallest S whose jerkiness (%.2f px) is at most no filter's (%.2f px)" % (jerk[chosen], allowed)
    else:
        chosen = min((n for n, _ in CANDIDATES if n.startswith("v4")), key=lambda n: jerk[n])
        reason = "no v4 version was as smooth as no filter (%.2f px); this is the least jerky (%.2f px)" % (allowed, jerk[chosen])

    lines = ["# Smoother corrector (v4): choosing the penalty S on validation", "",
             "Produced by `python evaluation/smoothness.py%s`. Sequences with marked tremor: %d; "
             "sequences without marked tremor: %d. Scored after the first 2.56 s. Jerkiness = average size of the "
             "change in cursor velocity from one 10 ms sample to the next (px); the intended path "
             "itself has %.2f px." % (" --test" if args.test else "", n_t, n_s, intended), "",
             "## Validation", ""] + HEADER + rows + ["", "**Chosen: %s** - %s." % (chosen, reason), ""]

    if args.test:
        rows, _, intended, n_t, n_s = score_split("test")
        lines += ["## Test (scored once, after choosing on validation)", "",
                  "Sequences with marked tremor: %d; without marked tremor: %d; intended path jerkiness %.2f px." % (
                      n_t, n_s, intended), ""] + HEADER + rows + [""]
    lines += ["This project is a prototype and is not medical advice.", ""]
    RESULT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
