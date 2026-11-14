"""
test_steady.py - checks of B3's logic that need no permission and no Mac:
    python -m pytest systemwide/test_steady.py

macOS is imitated: each step the device moves the cursor by (dx, dy) from where it is SHOWN,
as macOS does, and SteadyCursor decides where to show it.
"""

import numpy as np

from systemwide.steady import SteadyCursor

BOUNDS = (0, 0, 1440, 900)


def drive(steady, steps, dx=0.0, dy=0.0, rate=100):
    """Feed `steps` device movements of (dx, dy); return the hand and shown positions."""
    hand, shown = [], []
    for k in range(steps):
        x, y = steady.shown[0] + dx, steady.shown[1] + dy
        steady.move_to(x, y, k / rate)
        hand.append(steady.hand)
        shown.append(steady.shown)
    return np.array(hand), np.array(shown)


def make(mode, demo=None):
    steady = SteadyCursor((700, 450), BOUNDS, mode=mode, demo_level=demo)
    if steady.detector is not None:
        steady.detector.pool = None          # run the detector in line: repeatable
    return steady


def test_still_hand_with_strong_tremor_is_steadier_with_our_model():
    results = {}
    for mode in ["none", "learned"]:
        steady = make(mode, demo="strong")
        hand, shown = drive(steady, 1000)
        results[mode] = np.linalg.norm(shown[300:] - hand[300:], axis=1).mean()   # after 3 s
        steady.stop()
    assert results["learned"] < 0.7 * results["none"], results


def test_steady_hand_is_left_alone():
    steady = make("learned")
    hand, shown = drive(steady, 600, dx=3.0, dy=1.0)       # a smooth glide, no tremor
    assert np.linalg.norm(shown - hand, axis=1).max() < 1.0
    steady.stop()


def test_movement_adds_up_from_the_shown_position():
    steady = make("none")
    hand, shown = drive(steady, 100, dx=2.0)               # 100 steps of 2 px to the right
    assert abs(hand[-1][0] - 900) < 1e-6 and abs(shown[-1][0] - 900) < 1e-6


def test_filter_failure_falls_back_to_the_hand():
    steady = make("one_euro")

    def broken(*args):
        raise RuntimeError("simulated failure")
    steady.filter.update = broken
    x, y = steady.move_to(710, 455, 0.0)
    assert (x, y) == steady.hand == (710, 455) and steady.failures == 1


def test_cursor_never_leaves_the_screen():
    steady = make("none", demo="strong")
    _, shown = drive(steady, 300, dx=-50.0, dy=-50.0)      # push hard into the top-left corner
    assert shown.min() >= 0 and shown[:, 0].max() <= 1439 and shown[:, 1].max() <= 899
