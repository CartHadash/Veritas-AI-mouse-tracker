"""
classical_filters.py - standard (non-AI) smoothing filters, used as BASELINES that our model
must beat, and as the "One Euro" choice on the demo page.

Written from scratch during the hackathon (Sat 14 Nov 2026) from the published descriptions
of each method, replacing the pre-hackathon file (team leader's decision; docs/REUSED_CODE.md).

Every filter works the same way, one pointer sample at a time (so it could run live):
    f = OneEuroFilter()
    f.reset()                      -> forget everything (call when starting fresh)
    x_out, y_out = f.update(x, y, t)   -> newest raw position (px) and its time (s);
                                          returns the smoothed position
Each filter only uses the current and earlier samples (rule 11: causal).

The three methods:
  - MovingAverageFilter: the average of the positions in the last `window` seconds. Removes a
    lot of shaking but trails behind a moving hand by about half the window.
  - OneEuroFilter: Casiez, Roussel and Vogel (CHI 2012), "1 Euro Filter: A Simple Speed-based
    Low-pass Filter for Noisy Input in Interactive Systems". It smooths strongly when the
    pointer is slow and less when it is fast, so it lags less during quick movements.
  - KalmanFilter: a constant-velocity Kalman filter (a standard textbook method) for each
    axis: it keeps an estimate of position and speed, predicts the next position, and blends
    the prediction with the new measurement according to how noisy each is believed to be.
"""

import math
from collections import deque


class NoFilter:
    """Returns the input unchanged (the 'no filter' baseline)."""

    def reset(self):
        pass

    def update(self, x, y, t):
        return x, y


class MovingAverageFilter:
    def __init__(self, window=0.2):
        self.window = window                  # seconds of history to average
        self.reset()

    def reset(self):
        self.samples = deque()                # (t, x, y), oldest first

    def update(self, x, y, t):
        self.samples.append((t, x, y))
        # Keep only samples from the last `window` seconds (the newest one always stays). The
        # tiny tolerance stops decimal rounding (0.3 - 0.2 = 0.0999...) from keeping one extra.
        while self.samples[0][0] <= t - self.window + 1e-9:
            self.samples.popleft()
        n = len(self.samples)
        return sum(s[1] for s in self.samples) / n, sum(s[2] for s in self.samples) / n


def smoothing_factor(cutoff_hz, dt):
    """How much of a new sample a simple low-pass filter takes in (0-1), for a cut-off
    frequency and a time step: alpha = 1 / (1 + tau / dt), with tau = 1 / (2 pi cutoff)."""
    tau = 1.0 / (2 * math.pi * cutoff_hz)
    return 1.0 / (1.0 + tau / dt)


class OneEuroFilter:
    """
    min_cutoff (Hz): smoothing when the pointer is still (lower = smoother, more lag).
    beta: how quickly smoothing is reduced as the pointer speeds up (higher = less lag).
    d_cutoff (Hz): smoothing of the speed estimate itself.
    Each axis is filtered on its own, as in the paper's one-dimensional description. As in the
    authors' reference code (github.com/casiez/OneEuroFilter), the speed is measured from the
    previous SMOOTHED position, and the first speed estimate is taken as it is.
    """

    def __init__(self, min_cutoff=1.0, beta=0.004, d_cutoff=1.0):
        self.min_cutoff, self.beta, self.d_cutoff = min_cutoff, beta, d_cutoff
        self.reset()

    def reset(self):
        self.t_prev = None
        self.value = None                     # last smoothed position [x, y]
        self.speed = None                     # last smoothed speed per axis (px/s)

    def update(self, x, y, t):
        if self.value is None:
            self.t_prev, self.value = t, [x, y]
            return x, y
        dt = t - self.t_prev
        if dt <= 0:                           # same timestamp again: nothing new to do
            return self.value[0], self.value[1]
        self.t_prev = t
        for axis, raw in enumerate((x, y)):
            # 1. speed, estimated from the change since the last smoothed value, then smoothed
            raw_speed = (raw - self.value[axis]) / dt
            if self.speed is None:            # first speed estimate: taken as it is
                self.speed = [None, None]
            if self.speed[axis] is None:
                self.speed[axis] = raw_speed
            else:
                a = smoothing_factor(self.d_cutoff, dt)
                self.speed[axis] = a * raw_speed + (1 - a) * self.speed[axis]
            # 2. the faster the pointer, the higher the cut-off (less smoothing, less lag)
            cutoff = self.min_cutoff + self.beta * abs(self.speed[axis])
            a = smoothing_factor(cutoff, dt)
            self.value[axis] = a * raw + (1 - a) * self.value[axis]
        return self.value[0], self.value[1]


class KalmanAxis:
    """Constant-velocity Kalman filter for one axis. State: position p (px) and velocity v
    (px/s), with uncertainty P (a 2x2 table, kept as four numbers so no library is needed)."""

    def __init__(self, accel_std, measurement_std):
        self.q = accel_std ** 2               # how much the velocity may change (random acceleration)
        self.r = measurement_std ** 2         # how noisy each measured position is
        self.reset()

    def reset(self):
        self.p = None

    def update(self, z, dt):
        if self.p is None:                    # first sample: start at the measurement, at rest
            self.p, self.v = z, 0.0
            self.P00, self.P01, self.P11 = self.r, 0.0, self.r
            return z
        # Predict: move on at the current velocity; uncertainty grows (random acceleration).
        self.p += self.v * dt
        P00 = self.P00 + 2 * dt * self.P01 + dt * dt * self.P11 + self.q * dt ** 4 / 4
        P01 = self.P01 + dt * self.P11 + self.q * dt ** 3 / 2
        P11 = self.P11 + self.q * dt ** 2
        # Correct: blend in the measurement, weighted by how uncertain the prediction is.
        k0, k1 = P00 / (P00 + self.r), P01 / (P00 + self.r)
        error = z - self.p
        self.p += k0 * error
        self.v += k1 * error
        self.P00, self.P01, self.P11 = (1 - k0) * P00, (1 - k0) * P01, P11 - k1 * P01
        return self.p


class KalmanFilter:
    def __init__(self, accel_std=1500.0, measurement_std=12.0):
        self.kx = KalmanAxis(accel_std, measurement_std)
        self.ky = KalmanAxis(accel_std, measurement_std)
        self.reset()

    def reset(self):
        self.kx.reset()
        self.ky.reset()
        self.t_prev = None

    def update(self, x, y, t):
        dt = 0.0 if self.t_prev is None else max(t - self.t_prev, 0.0)
        self.t_prev = t
        return self.kx.update(x, dt), self.ky.update(y, dt)


FILTER_NAMES = ["moving_average", "one_euro", "kalman"]


def make_filter(name):
    """A new filter by name (one of FILTER_NAMES), with its default settings."""
    return {"moving_average": MovingAverageFilter, "one_euro": OneEuroFilter, "kalman": KalmanFilter}[name]()
