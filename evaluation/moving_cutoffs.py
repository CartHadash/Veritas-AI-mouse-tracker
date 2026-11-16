"""
moving_cutoffs.py - a movement-aware detector, cheap version: two cut-offs instead of one.

Why: detector v2 raises more false alarms while the hand moves on purpose than while it is
still (evaluation/results/detector_v2.md), and in the app a false alarm switches smoothing on
in the middle of a reach, which adds lag. No retraining here: the same model and the same
scores, but one cut-off for windows that look like a moving hand and another for windows that
look still. "Looks moving" is models.detector.features.looks_moving, a guess from the shaky
cursor alone, because the app never sees the intended path. Each cut-off is chosen on
VALIDATION people by the project's usual rule: the fewest false alarms with at
most 20% missed cases, inside its own group.

THE RULE (fixed before looking at any result): keep the two cut-offs only if, on VALIDATION,
  (a) false alarms on windows where the hand is truly moving (the tables' own definition,
      from the intended path) are lower than with the single cut-off,
  (b) missed cases overall are still at most 20%, and
  (c) false alarms overall are not higher than with the single cut-off.
Only then are TEST people scored, once (--test). Missed cases and false alarms are always
reported separately. If the rule fails, nothing in the app changes.

Run from the repository folder (under a minute):
    python evaluation/moving_cutoffs.py
    python evaluation/moving_cutoffs.py --test
Writes evaluation/results/moving_cutoffs.md (and, with --test and a pass, the two cut-offs
into models/detector/detector_v2_threshold.json for the live detector).
"""

import argparse
import json
import sys
from pathlib import Path

import joblib
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evaluation.metrics import choose_threshold, detector_scores  # noqa: E402
from models.detector.features import compute_features, looks_moving  # noqa: E402

DERIVED = ROOT / "data" / "derived"
MODEL_DIR = ROOT / "models" / "detector"
RESULT = ROOT / "evaluation" / "results" / "moving_cutoffs.md"
VERSION = "v2"
MAX_MISSED = 0.20


def load(split, model):
    data = dict(np.load(DERIVED / f"detector_{split}.npz"))
    scores = model["classifier"].predict_proba(compute_features(data["xy"]))[:, 1]
    return dict(scores=scores, labels=data["label"].astype(bool), moving=data["moving"].astype(bool),
                looks=looks_moving(data["xy"]), task=data["task_type"])


def predictions(d, single=None, cuts=None):
    """Tremor yes/no per window: with one cut-off, or with (moving cut-off, still cut-off)."""
    if cuts is None:
        return d["scores"] >= single
    return np.where(d["looks"], d["scores"] >= cuts[0], d["scores"] >= cuts[1])


def pct(x):
    return "-" if np.isnan(x) else "%.1f%%" % (100 * x)


def table(d, single, cuts):
    groups = [("all windows", np.ones(len(d["labels"]), bool)),
              ("hand truly moving", d["moving"]), ("hand truly still", ~d["moving"]),
              ("\"moving on purpose\" tasks (action)", d["task"] == "action")]
    lines = ["| Windows | One cut-off: missed | One cut-off: false alarms | Two cut-offs: missed | Two cut-offs: false alarms |",
             "|---|---|---|---|---|"]
    out = {}
    for name, mask in groups:
        a = detector_scores(d["labels"][mask], predictions(d, single=single)[mask])
        b = detector_scores(d["labels"][mask], predictions(d, cuts=cuts)[mask])
        out[name] = (a, b)
        lines.append("| %s | %s | %s | %s | %s |" % (name, pct(a["missed"]), pct(a["false_alarms"]),
                                                    pct(b["missed"]), pct(b["false_alarms"])))
    return lines, out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    model = joblib.load(MODEL_DIR / f"detector_{VERSION}.joblib")
    val = load("val", model)

    single = choose_threshold(val["scores"], val["labels"], max_missed=MAX_MISSED)
    cuts = (choose_threshold(val["scores"][val["looks"]], val["labels"][val["looks"]], max_missed=MAX_MISSED),
            choose_threshold(val["scores"][~val["looks"]], val["labels"][~val["looks"]], max_missed=MAX_MISSED))
    rows, out = table(val, single, cuts)
    one_all, two_all = out["all windows"]
    one_mov, two_mov = out["hand truly moving"]
    a = two_mov["false_alarms"] < one_mov["false_alarms"]
    b = two_all["missed"] <= MAX_MISSED
    c = two_all["false_alarms"] <= one_all["false_alarms"]
    keep = bool(a and b and c)

    agree = (val["looks"] == val["moving"])
    lines = ["# Movement-aware detector, cheap version: two cut-offs (validation first)", "",
             "Produced by `python evaluation/moving_cutoffs.py%s`. Detector %s, same model and scores; only "
             "the cut-off differs. \"Looks moving\" is a guess from the shaky cursor (0.32 s block averages "
             "travelling faster than 20 px/s for at least half of the window); the rows below use the "
             "tables' own definition of moving, from the intended path." % (" --test" if args.test else "", VERSION), "",
             "## Validation people (%d windows: %d tremor, %d no tremor)" % (
                 len(val["labels"]), val["labels"].sum(), (~val["labels"]).sum()), "",
             "The guess agrees with the true \"moving\" on %s of windows (%s of tremor windows, %s of "
             "no-tremor windows); %s of windows look moving." % (
                 pct(agree.mean()), pct(agree[val["labels"]].mean()), pct(agree[~val["labels"]].mean()),
                 pct(val["looks"].mean())), "",
             "Cut-offs, each the fewest false alarms with at most %d%% missed in its own group: one cut-off "
             "%.3f; two cut-offs %.3f (looks moving) and %.3f (looks still)." % (
                 round(100 * MAX_MISSED), single, cuts[0], cuts[1]), ""] + rows + [
             "", "Rule fixed in advance: keep only if (a) false alarms with the hand truly moving are lower, "
             "(b) missed overall at most %d%%, (c) false alarms overall not higher." % round(100 * MAX_MISSED), "",
             "(a) %s, (b) %s, (c) %s. **Result: %s**" % (
                 "yes" if a else "no", "yes" if b else "no", "yes" if c else "no",
                 "the two cut-offs are kept." if keep else "not kept; the app keeps its single cut-off."), ""]

    if args.test and keep:
        test = load("test", model)
        rows, out = table(test, single, cuts)
        lines += ["## Test people (scored once; %d windows: %d tremor, %d no tremor)" % (
            len(test["labels"]), test["labels"].sum(), (~test["labels"]).sum()), ""] + rows + [""]
        info_file = MODEL_DIR / f"detector_{VERSION}_threshold.json"
        with open(info_file, encoding="utf-8") as f:
            info = json.load(f)
        info.update(threshold_moving=cuts[0], threshold_still=cuts[1],
                    test_missed_cases_rate=round(float(out["all windows"][1]["missed"]), 4),
                    test_false_alarm_rate=round(float(out["all windows"][1]["false_alarms"]), 4))
        with open(info_file, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=1)
    lines += ["This project is a prototype and is not medical advice.", ""]
    RESULT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
