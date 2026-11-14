"""
live.py - run the corrector live, one pointer sample at a time, controlled by the detector.

Same shape as the classical filters, so the server can swap them freely:
    corrector = LiveCorrector()          # loads models/corrector/weights.pt
    corrector.reset()
    cx, cy = corrector.update(x, y, t)   # raw position in px, time in seconds

How the two models work together ("gating"):
  The detector's 0-1 tremor score is turned into a gate between 0 and 1. With gate 0 the raw
  cursor is returned untouched (a steady hand gets no added delay); with gate 1 the full
  correction is applied; in between it blends. The gate changes smoothly (over about 0.3 s)
  so the cursor never jumps.
    gate = 0 when score <= 0.05; 1 when score >= the DECISION 4 cut-off; a straight line between.

Samples can arrive at any rate (browsers send 60-120 per second); they are resampled to 100
per second, the rate the models were trained on, by drawing a straight line between
consecutive samples (models/resample.py).
"""

import math
import sys
from collections import deque
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from models.corrector.model import HISTORY, Corrector  # noqa: E402
from models.resample import Resampler  # noqa: E402

# The version the app uses: v3 (trained on plain distance; better than v1 at every tremor
# size on validation, see evaluation/results/improvements.md). v1 is weights.pt.
VERSION = "v3"
WEIGHTS = ROOT / "models" / "corrector" / f"weights_{VERSION}.pt"
RATE = 100
GATE_LOW = 0.05          # detector score at which the gate starts opening
GATE_SECONDS = 0.3       # how quickly the gate follows the detector


def gate_target(score, threshold):
    """Detector score (0-1) -> how much correction to apply (0-1)."""
    if score is None:
        return 0.0
    return float(np.clip((score - GATE_LOW) / (threshold - GATE_LOW), 0.0, 1.0))


def load_corrector(weights=WEIGHTS):
    model = Corrector()
    model.load_state_dict(torch.load(weights, map_location="cpu"))
    model.eval()
    return model


class LiveCorrector:
    def __init__(self, live_detector=None, use_gate=True, strength=1.0, model=None):
        """
        live_detector: a models.detector.predict.LiveDetector (created if None and use_gate).
        use_gate=False applies the full correction always (used to measure the model alone).
        strength: 0-1 user setting that scales the correction.
        """
        torch.set_num_threads(1)      # one tiny network: a single thread is fastest
        self.model = model or load_corrector()
        if use_gate and live_detector is None:
            from models.detector.predict import LiveDetector
            live_detector = LiveDetector()
        self.detector = live_detector if use_gate else None
        self.strength = strength
        self.reset()

    def reset(self):
        self.positions = deque(maxlen=HISTORY + 1)
        self.resampler = Resampler()
        self.last_t = None
        self.gate = 0.0
        self.offset = (0.0, 0.0)
        self.score = None
        if self.detector is not None:
            self.detector.reset()

    def update(self, x, y, t):
        # 1) Resample to 100 per second (straight line between samples; models/resample.py).
        ticks = self.resampler.feed(x, y, t)
        self.positions.extend(ticks)
        new_tick = bool(ticks)

        # 2) Detector score -> gate (smoothly).
        if self.detector is not None:
            result = self.detector.update(x, y, t)
            self.score = result["score"] if result else None
            target = gate_target(self.score, self.detector.detector.threshold)
            dt = 0.0 if self.last_t is None else max(t - self.last_t, 0.0)
            self.gate += (target - self.gate) * (1 - math.exp(-dt / GATE_SECONDS))
        else:
            self.gate = 1.0
        self.last_t = t

        # 3) Corrector network on the last 64 movement steps (only at new 10 ms ticks).
        if new_tick and len(self.positions) == HISTORY + 1:
            pos = np.array(self.positions, dtype=np.float32)
            steps = torch.from_numpy(np.diff(pos, axis=0))[None]
            with torch.inference_mode():
                self.offset = tuple(self.model(steps)[0].tolist())

        g = self.gate * self.strength
        return x + g * self.offset[0], y + g * self.offset[1]
