"""
time_live.py - how long does one live update take on this computer's processor?

Rule 11 of CLAUDE.md: a model that runs live must take well under 8 ms per sample.
The team leader runs this on the demo Mac too.

Run from the repository folder:
    python models/corrector/time_live.py
"""

import platform
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from models.corrector.live import LiveCorrector  # noqa: E402


def time_updates(corrector, n=3000):
    """Feed n samples of a wobbly movement at 100 per second; return per-update times in ms."""
    t = np.arange(n) / 100
    xs = 500 + 200 * np.sin(t) + 5 * np.sin(2 * np.pi * 5 * t)
    ys = 400 + 100 * np.cos(t) + 5 * np.cos(2 * np.pi * 5 * t)
    times = []
    for x, y, ti in zip(xs, ys, t):
        start = time.perf_counter()
        corrector.update(float(x), float(y), float(ti))
        times.append((time.perf_counter() - start) * 1000)
    return np.array(times[300:])          # ignore the warm-up


def main():
    print("Machine:", platform.machine(), platform.platform())
    for name, corrector in [("corrector only", LiveCorrector(use_gate=False)),
                            ("corrector + detector gate", LiveCorrector())]:
        ms = time_updates(corrector)
        print("%-26s mean %.3f ms, 99th percentile %.3f ms, worst %.3f ms per update" % (
            name, ms.mean(), np.percentile(ms, 99), ms.max()))


if __name__ == "__main__":
    main()
