"""
predict.py - use the trained detector: on stored windows, or live, sample by sample.

    from models.detector.predict import Detector
    detector = Detector()
    result = detector.predict(window)        # window: (256, 2) positions in px
    # -> {"score": 0.83, "tremor": True, "size_px": 5.9, "frequency_hz": 4.7}

    live = LiveDetector()                    # keeps the last 2.56 s itself
    result = live.update(x, y, t)            # call for every pointer sample; None until full

The score is 0-1 (how tremor-like the last 2.56 s were). "tremor" applies the cut-off chosen
in DECISION 4 (models/detector/detector_v1_threshold.json). It flags tremor-LIKE movement;
it does not diagnose anything.
"""

import json
import sys
from collections import deque
from pathlib import Path

import joblib
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from models.detector.features import FEATURE_NAMES, compute_features  # noqa: E402

MODEL_FILE = ROOT / "models" / "detector" / "detector_v1.joblib"
THRESHOLD_FILE = ROOT / "models" / "detector" / "detector_v1_threshold.json"
WINDOW = 256
RATE = 100


class Detector:
    def __init__(self, model_file=MODEL_FILE, threshold_file=THRESHOLD_FILE):
        model = joblib.load(model_file)
        self.classifier = model["classifier"]
        self.size_regressor = model["size_regressor"]
        self.threshold = 0.5
        if Path(threshold_file).exists():
            with open(threshold_file, encoding="utf-8") as f:
                self.threshold = json.load(f)["threshold"]
        self.peak_column = FEATURE_NAMES.index("peak frequency in 3-12 Hz")

    def predict(self, window):
        features = compute_features(np.asarray(window, dtype=np.float32)[None])
        score = float(self.classifier.predict_proba(features)[0, 1])
        return {"score": score, "tremor": score >= self.threshold,
                "size_px": float(np.expm1(self.size_regressor.predict(features)[0])),
                "frequency_hz": float(features[0, self.peak_column])}


class LiveDetector:
    """Feeds pointer samples (any rate) into the detector at 100 samples per second."""

    def __init__(self, detector=None, every=10):
        self.detector = detector or Detector()
        self.every = every                  # re-run the model every 10 samples (0.1 s)
        self.reset()

    def reset(self):
        self.samples = deque(maxlen=WINDOW)
        self.next_t = None
        self.last = None
        self.count = 0
        self.result = None

    def update(self, x, y, t):
        # Resample to exactly 100 per second by taking the latest position at each tick.
        if self.next_t is None:
            self.next_t = t
        while t >= self.next_t:
            self.samples.append((x, y))
            self.next_t += 1.0 / RATE
            self.count += 1
        if len(self.samples) == WINDOW and self.count >= self.every:
            self.count = 0
            self.result = self.detector.predict(np.array(self.samples))
        return self.result
