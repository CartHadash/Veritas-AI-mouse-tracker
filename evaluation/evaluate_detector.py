"""
evaluate_detector.py - score detector v1 ONCE on the locked-away TEST people.

The cut-off is chosen on VALIDATION: the strictest cut-off whose missed-case
rate on validation is at most --missed-target. The same rule picks the frequency-rule
baseline's cut-off, so the comparison is fair. Then everything is scored on test, overall
and per group (age band, sex, diagnosis, tremor size, task type, moving vs still), and the
headline is repeated at half and double the pixel factor (pixel-factor check).

Run from the repository folder (after models/detector/train.py, also with --tremor-scale
0.5 and 2):
    python evaluation/evaluate_detector.py --missed-target 0.20
    python evaluation/evaluate_detector.py --missed-target 0.20 --version v2
Writes evaluation/results/detector_<version>.md and models/detector/detector_<version>_threshold.json.
(The cut-off is always chosen on the NORMAL validation windows, for every version.)
"""

import argparse
import json
import sys
from pathlib import Path

import joblib
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evaluation.metrics import SIZE_CLASSES, choose_threshold, detector_scores  # noqa: E402
from evaluation.run_baselines import band_share  # noqa: E402
from models.detector.features import compute_features  # noqa: E402

DERIVED = ROOT / "data" / "derived"
MODEL_DIR = ROOT / "models" / "detector"
RESULTS = ROOT / "evaluation" / "results"




def score_split(model, data):
    features = compute_features(data["xy"])
    scores = model["classifier"].predict_proba(features)[:, 1]
    sizes = np.expm1(model["size_regressor"].predict(features))
    return scores, sizes


def pct(x):
    return "-" if np.isnan(x) else "%.1f%%" % (100 * x)


def group_rows(title, groups, labels, predictions, subjects):
    """One table row per group: windows, people, missed cases, false alarms."""
    rows = ["### By %s" % title, "",
            "| Group | Windows (tremor / no tremor) | People | Missed cases | False alarms |",
            "|---|---|---|---|---|"]
    for name, mask in groups:
        if mask.sum() == 0:
            continue
        s = detector_scores(labels[mask], predictions[mask])
        people = len(set(subjects[mask]) - {"synthetic"})
        rows.append("| %s | %d / %d | %d%s | %s | %s |" % (
            name, s["n_tremor"], s["n_no_tremor"], people, " (few!)" if people < 10 else "",
            pct(s["missed"]), pct(s["false_alarms"])))
    return rows + [""]


def evaluate_scale(scale, target, version):
    """Headline numbers (model and frequency rule) at one pixel-factor scale."""
    suffix = "" if scale == 1.0 else "_x%g" % scale
    path = MODEL_DIR / f"detector_{version}{suffix}.joblib"
    if not path.exists():
        return None
    model = joblib.load(path)
    val = dict(np.load(DERIVED / f"detector_val{suffix}.npz"))
    test = dict(np.load(DERIVED / f"detector_test{suffix}.npz"))
    val_scores, _ = score_split(model, val)
    cut = choose_threshold(val_scores, val["label"], max_missed=target)
    rule_cut = choose_threshold(band_share(val["xy"]), val["label"], max_missed=target)
    scores, sizes = score_split(model, test)
    return dict(cut=cut, rule_cut=rule_cut, test=test, scores=scores, sizes=sizes,
                model=detector_scores(test["label"], scores >= cut),
                rule=detector_scores(test["label"], band_share(test["xy"]) >= rule_cut))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--missed-target", type=float, required=True,
                        help="highest missed-case rate allowed on validation, e.g. 0.20")
    parser.add_argument("--version", default="v1")
    args = parser.parse_args()
    target, version = args.missed_target, args.version

    main_run = evaluate_scale(1.0, target, version)
    with open(MODEL_DIR / f"detector_{version}_threshold.json", "w", encoding="utf-8") as f:
        json.dump({"threshold": main_run["cut"], "missed_target_on_validation": target,
                   "test_missed_cases_rate": round(float(main_run["model"]["missed"]), 4),
                   "test_false_alarm_rate": round(float(main_run["model"]["false_alarms"]), 4)},
                  f, indent=1)

    test, scores, sizes = main_run["test"], main_run["scores"], main_run["sizes"]
    labels = test["label"].astype(bool)
    pred = scores >= main_run["cut"]
    m, r = main_run["model"], main_run["rule"]

    lines = ["# Detector %s: results on TEST people" % version, "",
             "Produced by `python evaluation/evaluate_detector.py --missed-target %g%s`. Test people "
             "(%d windows: %d tremor, %d no tremor) were used once, after every setting was "
             "chosen on validation." % (target, "" if version == "v1" else " --version " + version,
                                         len(labels), labels.sum(), (~labels).sum()), "",
             "DECISION 4: cut-off chosen on validation so that missed cases are at most %d%% there "
             "(model cut-off %.3f; frequency-rule cut-off %.3f, chosen the same way)." % (
                 round(100 * target), main_run["cut"], main_run["rule_cut"]), "",
             "## Headline", "",
             "| Detector | Missed cases | False alarms | Accuracy |", "|---|---|---|---|",
             "| Always \"no tremor\" | 100.0%% | 0.0%% | %s |" % pct((~labels).mean()),
             "| Frequency rule | %s | %s | %s |" % (pct(r["missed"]), pct(r["false_alarms"]), pct(r["accuracy"])),
             "| **Detector %s (our model)** | **%%s** | **%%s** | **%%s** |" % version % (
                 pct(m["missed"]), pct(m["false_alarms"]), pct(m["accuracy"])), ""]

    moving = test["moving"].astype(bool)
    rule_pred = band_share(test["xy"]) >= main_run["rule_cut"]
    lines += ["## Moving vs still (model, with the frequency rule in brackets)", "",
              "| Hand | Missed cases | False alarms |", "|---|---|---|"]
    for name, mask in [("moving", moving), ("still", ~moving)]:
        s, b = detector_scores(labels[mask], pred[mask]), detector_scores(labels[mask], rule_pred[mask])
        lines.append("| %s | %s (%s) | %s (%s) |" % (name, pct(s["missed"]), pct(b["missed"]),
                                                     pct(s["false_alarms"]), pct(b["false_alarms"])))
    lines.append("")

    subjects = test["subject"]
    def by(column, values):
        return [(v, test[column] == v) for v in values]
    lines += ["## Per group (judges check that it works equally well across groups)", "",
              "Groups with fewer than 10 people are marked \"few!\": their numbers are unreliable.",
              "Missed cases only exist for groups with tremor windows; healthy people and "
              "synthetic-only windows can only produce false alarms.", ""]
    lines += group_rows("age band", by("age_band", ["under 60", "60-69", "70 and over"]), labels, pred, subjects)
    lines += group_rows("sex", by("sex", ["female", "male"]), labels, pred, subjects)
    lines += group_rows("diagnosis", by("condition", sorted(set(test["condition"]))), labels, pred, subjects)
    lines += group_rows("task type", by("task_type", ["rest", "postural", "action"]), labels, pred, subjects)
    lines += group_rows("source of the window", by("source", ["tremor", "patient, no tremor", "healthy",
                                                              "synthetic only"]), labels, pred, subjects)
    size_groups = [(name, labels & (test["strength_px"] >= lo) & (test["strength_px"] < hi))
                   for name, lo, hi in SIZE_CLASSES]
    lines += group_rows("tremor size (tremor windows only)", size_groups, labels, pred, subjects)

    error = np.abs(sizes - test["strength_px"])
    lines += ["## Size estimate (tremor windows)", "",
              "| Tremor size | Windows | Median error (px) | Median true size (px) |", "|---|---|---|---|"]
    for name, mask in size_groups:
        if mask.sum():
            lines.append("| %s | %d | %.2f | %.2f |" % (name, mask.sum(), np.median(error[mask]),
                                                      np.median(test["strength_px"][mask])))
    lines.append("")

    lines += ["## Does the pixel factor (DECISION 1) decide the result?", "",
              "Everything rebuilt and retrained with every tremor at half and double size; "
              "cut-offs chosen on validation the same way.", "",
              "| Pixel factor | Model: missed | Model: false alarms | Rule: missed | Rule: false alarms |",
              "|---|---|---|---|---|"]
    for scale in (0.5, 1.0, 2.0):
        run = main_run if scale == 1.0 else evaluate_scale(scale, target, version)
        if run is None:
            lines.append("| x%g | not trained for this version | | | |" % scale)
            continue
        lines.append("| x%g | %s | %s | %s | %s |" % (scale, pct(run["model"]["missed"]),
                     pct(run["model"]["false_alarms"]), pct(run["rule"]["missed"]),
                     pct(run["rule"]["false_alarms"])))
    lines += ["", "This project is a prototype and is not medical advice.", ""]
    (RESULTS / f"detector_{version}.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
