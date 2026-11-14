"""
notch.py - a tremor canceller tuned to the person's own tremor rhythm (Oleksandr's idea,
Sat 14 Nov): remove one narrow band of frequencies around the rhythm the detector measures,
and let everything else (slow, deliberate movement) through.

A "notch" filter is a standard tool from signal processing. This one is the usual second-order
("biquad") notch from the Audio EQ Cookbook (R. Bristow-Johnson), recomputed whenever the
measured rhythm changes. It only uses the current and earlier samples (causal). Q sets the
width: the notch removes roughly the band  rhythm +- rhythm / (2 Q).

    notch = TremorNotch(q=2.0)
    x_out, y_out = notch.update(x, y, rhythm_hz)     # one call per 10 ms sample
"""

import math

RATE = 100


class TremorNotch:
    def __init__(self, q=2.0, rate=RATE):
        self.q, self.rate = q, rate
        self.reset()

    def reset(self):
        self.inputs = [[0.0, 0.0], [0.0, 0.0]]     # per axis: the last two inputs
        self.outputs = [[0.0, 0.0], [0.0, 0.0]]    # per axis: the last two outputs
        self.started = False

    def coefficients(self, rhythm_hz):
        w0 = 2 * math.pi * rhythm_hz / self.rate
        alpha = math.sin(w0) / (2 * self.q)
        a0 = 1 + alpha
        b = (1 / a0, -2 * math.cos(w0) / a0, 1 / a0)
        a = (-2 * math.cos(w0) / a0, (1 - alpha) / a0)
        return b, a

    def update(self, x, y, rhythm_hz):
        if not self.started:                        # start from rest at the first position
            self.inputs = [[x, x], [y, y]]
            self.outputs = [[x, x], [y, y]]
            self.started = True
        if rhythm_hz is None or not (1.0 < rhythm_hz < self.rate / 2):
            out = (x, y)                            # no rhythm measured yet: pass through
        else:
            b, a = self.coefficients(rhythm_hz)
            out = []
            for axis, value in enumerate((x, y)):
                i1, i2 = self.inputs[axis]
                o1, o2 = self.outputs[axis]
                out.append(b[0] * value + b[1] * i1 + b[2] * i2 - a[0] * o1 - a[1] * o2)
            out = tuple(out)
        for axis, value in enumerate((x, y)):
            self.inputs[axis] = [value, self.inputs[axis][0]]
            self.outputs[axis] = [out[axis], self.outputs[axis][0]]
        return out
