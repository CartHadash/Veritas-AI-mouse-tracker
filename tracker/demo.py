"""Check the tracker: run it for 10 seconds and print how fast and how regular it was.

    python -m tracker.demo            # move the pointer around in ANY app while it runs

The rate is measured only while the pointer moves, because the tracker deliberately sends
nothing after the pointer has been still for a few seconds (tracker/reader.py).
"""

import statistics
import time

from tracker import reader

SECONDS = 10


def main():
    samples = []
    print("Tracking for %d seconds. Move the pointer around in any app..." % SECONDS)
    reader.start(samples.append)
    time.sleep(SECONDS)
    reader.stop()

    if len(samples) < 2:
        print("Fewer than 2 samples: the pointer was probably not moved. Try again.")
        return

    # Gaps between samples. Gaps longer than 0.1 s are idle pauses, not timer jitter.
    gaps = [b["t"] - a["t"] for a, b in zip(samples, samples[1:])]
    active = [g for g in gaps if g < 0.1]
    rate = len(active) / sum(active) if active else 0.0
    ms = sorted(g * 1000 for g in active)

    print("Samples received:        %d" % len(samples))
    print("Rate while moving:       %.1f samples per second (target %d)" % (rate, reader.RATE_HZ))
    print("Gap between samples:     median %.2f ms, 95th percentile %.2f ms, longest %.2f ms"
          % (statistics.median(ms), ms[int(0.95 * (len(ms) - 1))], ms[-1]))
    print("Regularity (std of gap): %.2f ms" % statistics.pstdev(ms))
    print("Idle pauses skipped:     %d" % (len(gaps) - len(active)))
    print("First sample:", samples[0])


if __name__ == "__main__":
    main()
