"""
steady.py - B3: the logic of correcting the REAL cursor everywhere, kept apart from macOS so it
can be tested on any computer (systemwide/test_steady.py). The macOS part is systemwide/run.py.

Written fresh during the hackathon (Sat 14 Nov); nothing from the pre-hackathon experiment.

The idea. macOS moves the cursor by the pointer device's movement, starting from where the
cursor is now. We keep our own running total of that movement: the "hand" position. The hand
position (plus replayed demo tremor, if switched on) goes through the same filter the demo page
uses, and the cursor is shown at the filter's output. Because macOS applies the next movement
to the SHOWN position, the hand's movement is "new position - last shown position".

Safety: if the filter fails for any reason, the cursor simply follows the hand (no correction),
and it never leaves the screen.
"""

import math
import sys
from collections import deque
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from baselines.classical_filters import OneEuroFilter  # noqa: E402
from models.corrector.live import RESPONSE_LEVELS, LiveCorrector, load_corrector  # noqa: E402
from models.detector.predict import Detector, LiveDetector  # noqa: E402

DEMO_FILE = ROOT / "server" / "demo_tremor.npz"     # the demo page's replayed tremor (test people)
RATE = 100
MODES = ["learned", "one_euro", "none"]
DEMO_LEVELS = ["mild", "medium", "strong"]
FREEZE_SECONDS = 0.3      # click freeze never holds the cursor longer than this (as on the page)
AIM_HISTORY = 0.5         # s of shown positions kept for "click where you aimed"
DEFAULT_AIM_SECONDS = 0.1 # chosen on validation by evaluation/systemwide_clicks.py's rule (0 = off)


class ReplayedTremor:
    """Recorded tremor of test people, played back by the clock (one recording after another),
    blended between neighbouring samples so playback is smooth at any event rate."""

    def __init__(self, level):
        data = np.load(DEMO_FILE)
        self.samples = data["xy"][data["level"] == level].reshape(-1, 2)
        self.start = None

    def offset(self, t):
        if self.start is None:
            self.start = t
        position = (t - self.start) * RATE
        i = int(math.floor(position + 1e-6))          # whole sample, robust to rounding
        share = min(max(position - i, 0.0), 1.0)
        n = len(self.samples)
        a, b = self.samples[i % n], self.samples[(i + 1) % n]
        return a + share * (b - a)


class SteadyCursor:
    """
    start:  where the cursor is when correction starts (x, y), in screen points
    bounds: (left, top, right, bottom) of the screen area the cursor may be in
    mode:   "learned" (our detector + corrector), "one_euro" or "none"
    demo_level: None, or "mild" / "medium" / "strong" replayed tremor added to the hand
    response: "steadiest" / "balanced" / "responsive" smoothing of our model (the page's choice)
    freeze: click freeze, as on the page: from a button press the shown cursor stays where it
        was pressed until the release, at most 0.3 s, so shaking while the button is down
        cannot carry the click off a button. The hand keeps being followed underneath.
    aim_seconds: "click where you aimed" (team leader's idea, Sun 15 Nov). At the press the
        cursor still carries some leftover shake, so the click is placed at the AVERAGE of
        where the cursor was shown over the last aim_seconds (tremor is 4-6 shakes a second,
        so about one shake averages out). Only while our model is correcting tremor (gate
        over half open); a steady hand's click is never moved. 0 switches it off.
    """

    def __init__(self, start, bounds, mode="learned", demo_level=None, strength=1.0,
                 response="steadiest", freeze=True, aim_seconds=DEFAULT_AIM_SECONDS):
        self.bounds = bounds
        self.hand = self.clamp(*start)
        self.shown = self.hand
        self.mode = mode
        self.demo = ReplayedTremor(demo_level) if demo_level else None
        self.detector = None
        if mode == "learned":
            self.detector = LiveDetector(Detector())
            self.filter = LiveCorrector(live_detector=self.detector, strength=strength, model=load_corrector(),
                                        smoothing=RESPONSE_LEVELS[response])
        elif mode == "one_euro":
            self.filter = OneEuroFilter()
        else:
            self.filter = None
        self.freeze = freeze
        self.frozen_until = None      # while a click freeze holds the cursor: the time it ends
        self.aim_seconds = aim_seconds
        self.recent = deque()         # (t, x, y) of the shown cursor over the last AIM_HISTORY s
        self.updates = 0
        self.failures = 0

    def press(self, t):
        """A mouse button went down at time t. Returns where the click lands: normally where
        the cursor is shown; while tremor is being corrected, the average of where it was
        shown over the last aim_seconds. Then the click freeze starts there."""
        correcting = self.mode == "learned" and self.filter.gate > 0.5
        if self.aim_seconds > 0 and correcting:
            points = [(x, y) for (when, x, y) in self.recent if t - when <= self.aim_seconds]
            if points:
                self.shown = self.clamp(sum(p[0] for p in points) / len(points),
                                        sum(p[1] for p in points) / len(points))
        if self.freeze:
            self.frozen_until = t + FREEZE_SECONDS
        return self.shown

    def release(self):
        """The button came up: the freeze ends (the click lands where the cursor is shown)."""
        self.frozen_until = None

    def clamp(self, x, y):
        left, top, right, bottom = self.bounds
        return (min(max(x, left), right - 1), min(max(y, top), bottom - 1))

    def move_to(self, x, y, t):
        """macOS wants to put the cursor at (x, y) at time t (seconds). Returns where to show it."""
        self.hand = self.clamp(self.hand[0] + x - self.shown[0], self.hand[1] + y - self.shown[1])
        try:
            hx, hy = self.hand
            if self.demo is not None:
                ox, oy = self.demo.offset(t)
                hx, hy = hx + float(ox), hy + float(oy)
            if self.filter is None:
                cx, cy = hx, hy
            else:
                cx, cy = self.filter.update(hx, hy, t)
            if not (math.isfinite(cx) and math.isfinite(cy)):
                raise ValueError("filter gave a non-number")
        except Exception:                       # never let a filter problem take the cursor away
            self.failures += 1
            cx, cy = self.hand
        self.updates += 1
        if self.frozen_until is not None and t < self.frozen_until:
            return self.shown                   # click freeze: stay at the press point
        self.frozen_until = None
        self.shown = self.clamp(cx, cy)
        self.recent.append((t, self.shown[0], self.shown[1]))
        while t - self.recent[0][0] > AIM_HISTORY:
            self.recent.popleft()
        return self.shown

    def stop(self):
        if self.detector is not None and self.detector.pool is not None:
            self.detector.pool.shutdown(wait=False)
