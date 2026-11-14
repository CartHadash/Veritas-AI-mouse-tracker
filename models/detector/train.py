"""
train.py - step 7: train detector version 1 (DECISION 3, option A).

The model is "gradient boosting" from scikit-learn: many small decision trees, each one
fixing the mistakes of the ones before it, voting together. It reads the ~20 features from
features.py and outputs a tremor score from 0 to 1. A second model of the same kind
estimates the tremor's size in pixels.

Rules we follow here:
  - learn from TRAIN people only;
  - choose settings on VALIDATION people only;
  - never look at TEST people (that is evaluation/evaluate_detector.py, run once at the end).

Run from the repository folder (under a minute):
    python models/detector/train.py                     # normal pixel factor
    python models/detector/train.py --tremor-scale 0.5  # DECISION 1 check (needs the _x0.5 data)
Saves models/detector/detector_v1.joblib (or detector_v1_x0.5.joblib) and writes the
validation trade-off table to evaluation/results/detector_v1_validation.md.
"""

import argparse
import itertools
import sys
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance
from sklearn.metrics import average_precision_score

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from evaluation.metrics import detector_scores  # noqa: E402
from models.detector.features import FEATURE_NAMES, compute_features  # noqa: E402

DERIVED = ROOT / "data" / "derived"
MODEL_DIR = ROOT / "models" / "detector"
RESULTS = ROOT / "evaluation" / "results"

# The settings we try. Each is a reasonable small choice; validation picks the best.
GRID = {"learning_rate": [0.05, 0.1], "max_leaf_nodes": [15, 31], "max_iter": [200, 400]}


def load(name, suffix):
    data = dict(np.load(DERIVED / f"detector_{name}{suffix}.npz"))
    data["features"] = compute_features(data["xy"])
    return data


def tradeoff_table(scores, labels, moving):
    """For several 'missed cases' targets, the cut-off and the false alarms it costs (validation)."""
    rows = ["| Missed cases at most | Cut-off | Missed (all) | False alarms (all) "
            "| Missed (hand moving) | False alarms (hand moving) |", "|---|---|---|---|---|---|"]
    for target in [0.05, 0.10, 0.15, 0.20, 0.30]:
        cut = None
        for c in np.sort(np.unique(scores))[::-1]:           # from strict to lenient
            if detector_scores(labels, scores >= c)["missed"] <= target:
                cut = c
                break
        s = detector_scores(labels, scores >= cut)
        m = detector_scores(labels[moving], scores[moving] >= cut)
        rows.append("| %d%% | %.3f | %.1f%% | %.1f%% | %.1f%% | %.1f%% |" % (
            100 * target, cut, 100 * s["missed"], 100 * s["false_alarms"],
            100 * m["missed"], 100 * m["false_alarms"]))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tremor-scale", type=float, default=1.0)
    args = parser.parse_args()
    suffix = "" if args.tremor_scale == 1.0 else "_x%g" % args.tremor_scale

    train, val = load("train", suffix), load("val", suffix)
    print("Train windows: %d, validation windows: %d" % (len(train["label"]), len(val["label"])))

    # 1) Choose settings on validation by "average precision": how well the score ranks
    #    tremor windows above no-tremor windows, whatever cut-off is chosen later.
    best, best_ap = None, -1
    for values in itertools.product(*GRID.values()):
        params = dict(zip(GRID.keys(), values))
        model = HistGradientBoostingClassifier(random_state=0, **params)
        model.fit(train["features"], train["label"])
        ap = average_precision_score(val["label"], model.predict_proba(val["features"])[:, 1])
        print("  %s -> validation average precision %.3f" % (params, ap))
        if ap > best_ap:
            best, best_ap = params, ap
    print("Chosen settings:", best)

    classifier = HistGradientBoostingClassifier(random_state=0, **best).fit(train["features"], train["label"])
    # 2) Size estimate: predicts the tremor's on-screen size (px) in every window.
    regressor = HistGradientBoostingRegressor(random_state=0, **best).fit(
        train["features"], np.log1p(train["strength_px"]))

    val_scores = classifier.predict_proba(val["features"])[:, 1]
    size_error = np.abs(np.expm1(regressor.predict(val["features"])) - val["strength_px"])

    path = MODEL_DIR / f"detector_v1{suffix}.joblib"
    joblib.dump({"classifier": classifier, "size_regressor": regressor,
                 "feature_names": FEATURE_NAMES, "settings": best}, path, compress=3)
    print("Saved %s (%.2f MB)" % (path.relative_to(ROOT), path.stat().st_size / 1e6))
    np.save(DERIVED / f"detector_v1_val_scores{suffix}.npy", val_scores)

    if suffix:
        return   # the half/double runs only need the saved model

    # 3) Which features mattered: shuffle one feature at a time on validation and see how
    #    much worse the model gets (permutation importance).
    importance = permutation_importance(classifier, val["features"], val["label"],
                                        scoring="average_precision", n_repeats=5, random_state=0)
    order = np.argsort(importance.importances_mean)[::-1]

    lines = ["# Detector v1: validation results (used to choose settings and the cut-off)", "",
             "Produced by `python models/detector/train.py`. Validation people only; test people "
             "are not used here.", "",
             "Chosen settings: `%s`; validation average precision %.3f "
             "(1.0 = perfect ranking; the share of tremor windows, %.3f, = random guessing)." % (
                 best, best_ap, val["label"].mean()), "",
             "## Trade-off between missed cases and false alarms (DECISION 4)", ""]
    lines += tradeoff_table(val_scores, val["label"].astype(bool), val["moving"].astype(bool))
    lines += ["", "Size estimate error on validation tremor windows: median %.2f px "
              "(tremor windows' median size %.2f px)." % (
                  np.median(size_error[val["label"] == 1]),
                  np.median(val["strength_px"][val["label"] == 1])), "",
              "## Which features mattered (drop in average precision when shuffled)", "",
              "| Feature | Importance |", "|---|---|"]
    lines += ["| %s | %.3f |" % (FEATURE_NAMES[i], importance.importances_mean[i]) for i in order]
    lines += ["", "This project is a prototype and is not medical advice.", ""]
    (RESULTS / "detector_v1_validation.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
