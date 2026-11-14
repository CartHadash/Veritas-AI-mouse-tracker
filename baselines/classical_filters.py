# ---------------------------------------------------------------------------
# PRE-HACKATHON CODE - DISCLOSED.
# This file was written by our team on 12-13 Nov 2026, before the hackathon
# started, during a feasibility test. It is reused here unchanged except for
# this notice. See docs/REUSED_CODE.md. Everything else in this repository was
# written during the hackathon weekend (14-15 Nov 2026).
# ---------------------------------------------------------------------------
"""
classical_filters.py - standard (non-AI) smoothing filters, used as BASELINES.

Every filter has the same two methods, so the rest of the code can swap them freely:

    filter.reset()                 -> forget all history (call when starting fresh)
    filter.update(x, y, t)         -> give it the newest raw position (pixels) and the
                                      time in seconds; it returns the smoothed (x, y)

All filters are "time aware": they use the real timestamp `t` instead of assuming a
fixed sample rate, because mouse events arrive at irregular intervals.
"""

import math
from collections import deque

import numpy as np


class NoFilter:
    """Does nothing. Used as the 'no filter' baseline."""

    def reset(self):
        pass

    def update(self, x, y, t):
        return x, y


class MovingAverageFilter:
    """
    Simple moving average: the output is the mean of all positions seen in the
    last `window` seconds.

    Trick: if the window is exactly one tremor period (0.2 s for a 5 Hz tremor),
    each full shake cancels itself out in the average. The cost is lag: the
    output trails the hand by about half the window (~0.1 s).
    """

    def __init__(self, window=0.2):
        self.window = window
        self.samples = deque()  # each entry is (t, x, y)

    def reset(self):
        self.samples.clear()

    def update(self, x, y, t):
        self.samples.append((t, x, y))
        # Drop samples that are older than the window.
        while self.samples and t - self.samples[0][0] > self.window:
            self.samples.popleft()
        n = len(self.samples)
        mean_x = sum(s[1] for s in self.samples) / n
        mean_y = sum(s[2] for s in self.samples) / n
        return mean_x, mean_y


class OneEuroFilter:
    """
    One Euro filter (Casiez et al., 2012) - a low-pass filter whose strength adapts
    to how fast you are moving:

      * moving slowly (aiming at a target)  -> heavy smoothing, removes tremor
      * moving fast (travelling to a target) -> light smoothing, so little lag

    Parameters:
      min_cutoff : smoothing strength at rest, in Hz. LOWER = smoother but laggier.
                   It must sit well below the tremor frequency (4-6 Hz).
      beta       : how quickly smoothing is relaxed as speed rises. HIGHER = less
                   lag in fast movements, but if it is too high the tremor's own
                   speed "opens" the filter and the shake leaks through.
      d_cutoff   : smoothing applied to the speed estimate itself (Hz).
    """

    def __init__(self, min_cutoff=1.0, beta=0.004, d_cutoff=1.0):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.reset()

    def reset(self):
        self.last_t = None
        self.last_raw = None      # previous raw position (x, y)
        self.velocity = (0.0, 0.0)  # smoothed velocity estimate (px/s)
        self.smoothed = None      # previous output (x, y)

    @staticmethod
    def _alpha(cutoff, dt):
        """Blend factor of a first-order low-pass filter (0 = frozen, 1 = no smoothing)."""
        tau = 1.0 / (2.0 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)

    def update(self, x, y, t):
        if self.last_t is None:  # first sample: nothing to smooth yet
            self.last_t, self.last_raw, self.smoothed = t, (x, y), (x, y)
            return x, y

        dt = max(t - self.last_t, 1e-4)  # avoid dividing by zero

        # 1) Estimate how fast the hand is moving, and smooth that estimate.
        raw_vx = (x - self.last_raw[0]) / dt
        raw_vy = (y - self.last_raw[1]) / dt
        a_d = self._alpha(self.d_cutoff, dt)
        vx = self.velocity[0] + a_d * (raw_vx - self.velocity[0])
        vy = self.velocity[1] + a_d * (raw_vy - self.velocity[1])
        speed = math.hypot(vx, vy)

        # 2) Faster movement -> higher cutoff -> less smoothing (less lag).
        cutoff = self.min_cutoff + self.beta * speed

        # 3) Low-pass the position with that cutoff.
        a = self._alpha(cutoff, dt)
        sx = self.smoothed[0] + a * (x - self.smoothed[0])
        sy = self.smoothed[1] + a * (y - self.smoothed[1])

        self.last_t, self.last_raw = t, (x, y)
        self.velocity, self.smoothed = (vx, vy), (sx, sy)
        return sx, sy


class _Kalman1D:
    """
    Kalman filter for ONE axis with a 'constant velocity' model.

    It keeps a belief about two hidden numbers: [position, velocity].
    Each step it (a) predicts where the cursor should be if it kept moving at
    the same velocity, then (b) corrects that prediction part-way towards the
    new measurement. How far it moves towards the measurement depends on how
    much it trusts the model versus the measurement.
    """

    def __init__(self, accel_std, measurement_std):
        self.accel_std = accel_std              # how violently intended motion can change (px/s^2)
        self.R = measurement_std ** 2           # measurement noise variance (the tremor)
        self.H = np.array([[1.0, 0.0]])         # we only measure position, not velocity
        self.state = None                       # [position, velocity]
        self.P = None                           # uncertainty of the state (2x2)

    def reset(self):
        self.state = None

    def update(self, z, dt):
        if self.state is None:
            self.state = np.array([z, 0.0])
            self.P = np.eye(2) * 100.0
            return z

        # --- Predict ---
        F = np.array([[1.0, dt], [0.0, 1.0]])   # position += velocity * dt
        q = self.accel_std ** 2
        Q = q * np.array([[dt ** 4 / 4, dt ** 3 / 2],
                          [dt ** 3 / 2, dt ** 2]])  # uncertainty added by unknown acceleration
        self.state = F @ self.state
        self.P = F @ self.P @ F.T + Q

        # --- Correct with the measurement z ---
        innovation = z - (self.H @ self.state)[0]       # how wrong the prediction was
        S = (self.H @ self.P @ self.H.T)[0, 0] + self.R
        K = (self.P @ self.H.T)[:, 0] / S               # Kalman gain: how much to trust z
        self.state = self.state + K * innovation
        self.P = (np.eye(2) - np.outer(K, self.H[0])) @ self.P
        return float(self.state[0])


class KalmanFilter:
    """
    2D Kalman filter = two independent 1D filters (one for x, one for y).

    Parameters:
      accel_std       : expected size of *intended* acceleration (px/s^2).
                        HIGHER = follows the hand more eagerly (less lag, more shake).
      measurement_std : expected size of the tremor/noise (px).
                        HIGHER = trusts measurements less (smoother, more lag).
    """

    def __init__(self, accel_std=1500.0, measurement_std=12.0):
        self.kx = _Kalman1D(accel_std, measurement_std)
        self.ky = _Kalman1D(accel_std, measurement_std)
        self.last_t = None

    def reset(self):
        self.kx.reset()
        self.ky.reset()
        self.last_t = None

    def update(self, x, y, t):
        dt = 1.0 / 120.0 if self.last_t is None else max(t - self.last_t, 1e-4)
        self.last_t = t
        return self.kx.update(x, dt), self.ky.update(y, dt)


# Names used everywhere (CSV files, command line, charts).
FILTER_NAMES = ["moving_average", "one_euro", "kalman"]


def make_filter(name):
    """Create a fresh filter by name, with the default (tuned) parameters."""
    if name == "none":
        return NoFilter()
    if name == "moving_average":
        return MovingAverageFilter()
    if name == "one_euro":
        return OneEuroFilter()
    if name == "kalman":
        return KalmanFilter()
    raise ValueError("Unknown filter: %r (choose from none, %s)" % (name, ", ".join(FILTER_NAMES)))
