"""
resample.py - turn pointer samples that arrive at any rate into exactly 100 per second.

Browsers send pointer positions about 60-120 times a second at uneven times; our models were
trained on exactly 100 per second. At every 10 ms "tick" between the previous sample and the
new one, we draw a straight line between those two samples and take the point on it
(linear interpolation). This only uses samples that have already arrived, so it is causal.

Why not simply repeat the latest position at each tick? Because at 60 samples a second that
turns smooth movement into a staircase (some ticks move twice as far, others not at all), and
the corrector mistook the stairs for shaking: on the demo page it made the cursor worse than
no filter (found with evaluation/compare_modes.py).

After a gap of more than 1 second (the pointer stopped, or the tracker paused), it starts
again at the new position instead of drawing a slow line across the gap, and sets
`restarted` so the caller can forget its old history (otherwise the models would see one
huge jump between the old and the new position).
"""

RATE = 100
MAX_GAP = 1.0
EPSILON = 1e-9    # tolerance for rounding in times (a tick at 0.07 s must count at t = 0.07)


class Resampler:
    def __init__(self):
        self.reset()

    def reset(self):
        self.prev = None          # (t, x, y) of the previous sample
        self.start_t = None       # time of tick number 0
        self.next_k = None        # number of the next tick; its time is start_t + next_k / RATE
        self.restarted = False    # True right after a fresh start (first sample, or after a gap)

    def feed(self, x, y, t):
        """Give one sample; returns the list of (x, y) positions at the ticks it completes."""
        ticks = []
        self.restarted = self.prev is None or t - self.prev[0] > MAX_GAP
        if self.restarted:
            self.prev = (t, x, y)
            self.start_t, self.next_k = t, 1
            return [(x, y)]
        t0, x0, y0 = self.prev
        # Tick times are computed from a whole-number tick count, not by adding 0.01 again and
        # again: repeated adding drifts, and then most ticks landed a hair AFTER their own
        # sample, so the corrected cursor trailed by 10 ms (found on the demo page).
        while self.start_t + self.next_k / RATE <= t + EPSILON:
            tick_t = self.start_t + self.next_k / RATE
            share = min(1.0, (tick_t - t0) / (t - t0)) if t > t0 else 1.0
            ticks.append((x0 + share * (x - x0), y0 + share * (y - y0)))
            self.next_k += 1
        self.prev = (t, x, y)
        return ticks
