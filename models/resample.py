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
again at the new position instead of drawing a slow line across the gap.
"""

RATE = 100
MAX_GAP = 1.0


class Resampler:
    def __init__(self):
        self.reset()

    def reset(self):
        self.prev = None          # (t, x, y) of the previous sample
        self.next_t = None        # time of the next 10 ms tick

    def feed(self, x, y, t):
        """Give one sample; returns the list of (x, y) positions at the ticks it completes."""
        ticks = []
        if self.prev is None or t - self.prev[0] > MAX_GAP:
            self.prev = (t, x, y)
            self.next_t = t + 1.0 / RATE
            return [(x, y)]
        t0, x0, y0 = self.prev
        while self.next_t <= t:
            share = (self.next_t - t0) / (t - t0) if t > t0 else 1.0
            ticks.append((x0 + share * (x - x0), y0 + share * (y - y0)))
            self.next_t += 1.0 / RATE
        self.prev = (t, x, y)
        return ticks
