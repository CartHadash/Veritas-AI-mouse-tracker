"""
predict.py - use the trained detector: on stored windows, or live, sample by sample.

    from models.detector.predict import Detector
    detector = Detector()
    result = detector.predict(window)        # window: (256, 2) positions in px
    # -> {"score": 0.83, "tremor": True, "size_px": 5.9, "frequency_hz": 4.7}

    live = LiveDetector()                    # keeps the last 2.56 s itself
    result = live.update(x, y, t)            # call for every pointer sample; None until full

The score is 0-1 (how tremor-like the last 2.56 s were). "tremor" applies the cut-off chosen
in DECISION 4 (models/detector/detector_<version>_threshold.json). It flags tremor-LIKE movement;
it does not diagnose anything.
"""

import json
import sys
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import joblib
import numpy as np
from threadpoolctl import ThreadpoolController

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from models.detector.features import FEATURE_NAMES, compute_features  # noqa: E402

# The version the app uses. Step 12 kept v2 (better on pause-free movement); see
# evaluation/results/improvements.md.
VERSION = "v2"
MODEL_FILE = ROOT / "models" / "detector" / f"detector_{VERSION}.joblib"
THRESHOLD_FILE = ROOT / "models" / "detector" / f"detector_{VERSION}_threshold.json"
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
        # For ONE window, scikit-learn's parallel worker threads cost far more than they save
        # (about 20 ms instead of 2 ms on the builder's Mac), so live calls use one thread.
        self.threads = ThreadpoolController()

    def predict(self, window):
        features = compute_features(np.asarray(window, dtype=np.float32)[None])
        with self.threads.limit(limits=1, user_api="openmp"):
            score = float(self.classifier.predict_proba(features)[0, 1])
            size = float(np.expm1(self.size_regressor.predict(features)[0]))
        return {"score": score, "tremor": score >= self.threshold, "size_px": size,
                "frequency_hz": float(features[0, self.peak_column])}


class LiveDetector:
    """
    Feeds pointer samples (any rate) into the detector at 100 samples per second.

    background=True (the default for live use): the detector runs on a separate thread, so a
    pointer update NEVER waits for it. One detector call usually takes about 4 ms but can
    spike to 15+ ms when the computer is busy; the cursor keeps using the latest finished
    result meanwhile (at most a few ms old). background=False runs it in line (for tests).
    """

    def __init__(self, detector=None, every=10, background=True):
        self.detector = detector or Detector()
        self.every = every                  # re-run the model every 10 samples (0.1 s)
        self.pool = ThreadPoolExecutor(max_workers=1) if background else None
        self.reset()

    def reset(self):
        self.samples = deque(maxlen=WINDOW)
        self.next_t = None
        self.last = None
        self.count = 0
        self.result = None
        self.pending = None

    def update(self, x, y, t):
        # Pick up a finished background result, if there is one.
        if self.pending is not None and self.pending.done():
            self.result = self.pending.result()
            self.pending = None
        # Resample to exactly 100 per second by taking the latest position at each tick.
        if self.next_t is None:
            self.next_t = t
        while t >= self.next_t:
            self.samples.append((x, y))
            self.next_t += 1.0 / RATE
            self.count += 1
        if len(self.samples) == WINDOW and self.count >= self.every:
            window = np.array(self.samples)
            if self.pool is None:
                self.count = 0
                self.result = self.detector.predict(window)
            elif self.pending is None:          # never queue up more than one job
                self.count = 0
                self.pending = self.pool.submit(self.detector.predict, window)
        return self.result
