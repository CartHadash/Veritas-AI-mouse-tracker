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


def test_click_freeze_holds_the_cursor_until_release_or_300_ms():
    steady = make("none", demo="strong")
    drive(steady, 50)
    steady.press(0.5)
    pressed_at = steady.shown
    for k in range(50, 70):                                # 0.2 s with the button down
        steady.move_to(steady.shown[0] + 1.0, steady.shown[1], k / 100)
        assert steady.shown == pressed_at
    steady.release()
    steady.move_to(steady.shown[0] + 1.0, steady.shown[1], 0.70)
    assert steady.shown != pressed_at                      # released: follows again
    assert abs(steady.hand[0] - (700 + 21)) < 1e-6         # the hand was followed underneath

    steady.press(1.0)
    pressed_at = steady.shown
    steady.move_to(steady.shown[0] + 5.0, steady.shown[1], 1.31)   # held longer than 0.3 s (a drag)
    assert steady.shown != pressed_at


def test_click_freeze_can_be_switched_off():
    steady = SteadyCursor((700, 450), BOUNDS, mode="none", freeze=False)
    steady.press(0.0)
    assert steady.move_to(710, 450, 0.01) == (710, 450)


def test_response_level_sets_the_smoothing():
    steady = SteadyCursor((700, 450), BOUNDS, mode="learned", response="balanced")
    assert steady.filter.smoothing == {"min_cutoff": 1.0, "beta": 0.02}
    steady.stop()


def test_idle_updates_keep_the_detector_warm_through_a_pause():
    # run.py feeds the filter every 10 ms while the mouse is still. Imitate a 3 s pause that way:
    # the detector must still have a result afterwards (no new 2.56 s warm-up).
    steady = make("learned")
    drive(steady, 300, dx=1.0)                             # 3 s of movement
    for k in range(300, 600):                              # 3 s still, fed every 10 ms
        steady.move_to(steady.shown[0], steady.shown[1], k / 100)
    assert steady.detector.result is not None
    steady.stop()


def test_click_lands_at_the_average_of_recent_positions_only_while_correcting():
    # "Click where you aimed": with strong tremor being corrected, the click is the average of
    # the shown positions of the last 0.1 s, so it is closer to the hold point than a single
    # shaky position is on average.
    steady = make("learned", demo="strong")
    drive(steady, 600)                                     # 6 s: the gate is open by now
    assert steady.filter.gate > 0.5
    recent = [(x, y) for (when, x, y) in steady.recent if 5.99 - when <= 0.1]
    expected = np.mean(recent, axis=0)
    landed = steady.press(5.99)
    assert np.allclose(landed, expected) and len(recent) >= 5
    steady.stop()

    # A steady hand (no tremor, gate closed): the click is exactly where the cursor is.
    steady = make("learned")
    drive(steady, 400, dx=2.0)
    here = steady.shown
    assert steady.filter.gate < 0.5 and steady.press(3.99) == here
    steady.stop()

    # Switched off: never moved.
    steady = SteadyCursor((700, 450), BOUNDS, mode="none", demo_level="strong", aim_seconds=0.0)
    drive(steady, 100)
    here = steady.shown
    assert steady.press(0.99) == here
