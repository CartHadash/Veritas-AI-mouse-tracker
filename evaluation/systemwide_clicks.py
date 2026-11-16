"""
systemwide_clicks.py - reach for a button, stop, click: how often does the click land when the
REAL cursor is corrected (B3, systemwide/)? A simulation (no real people).

Why (a hand check on a Mac): with our model the real cursor was
visibly steadier, but clicking real buttons was still hard. Two suspects this script measures:
the cursor trails the hand (lag) and is still catching up when the click comes, and shaking
while the button is held carries the click off the button (no click freeze in B3 until now).

The simulation drives systemwide.steady.SteadyCursor exactly as macOS does (each step the
device moves the cursor from where it is SHOWN). The hand reaches 300 px to a button in 0.6 s
(a smooth "minimum jerk" reach), stops exactly on its centre, presses 0.2-0.6 s after arriving
and holds for 80-200 ms (our assumptions), then reaches for the next button. Replayed tremor
shakes the hand all the time. A click succeeds if the shown cursor is on the button at the
press AND at the release. Because the aim is perfect, every miss comes from shaking or lag.

Compared: no filter, One Euro, and our model at each smoothing level (Steadiest / Balanced /
Faster), each without and with click freeze, for a 22 px button (the demo page's target) and a
10 px one (a small checkbox).

"Click where you aimed": the click
is placed at the average of where the cursor was shown over the last 0.1 / 0.2 / 0.3 s, while
tremor is being corrected. Its rule, also fixed before running, is printed with its table.

THE RULE for B3's default smoothing level (fixed before running): the level with the most
successful clicks on the 10 px button with click freeze on and strong tremor, on VALIDATION
people's tremor; an exact tie goes to the steadier level. With --people test the same table is
made once from test people's tremor (nothing is chosen from it).

Run from the repository folder (a few minutes):
    python evaluation/systemwide_clicks.py
    python evaluation/systemwide_clicks.py --people test
Writes evaluation/results/systemwide_clicks_<people>.md.
"""

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import systemwide.steady as sw  # noqa: E402
from evaluation.compare_modes import DEMO_FILES  # noqa: E402
from models.corrector.live import RESPONSE_LEVELS  # noqa: E402

RATE = 100
BOUNDS = (0, 0, 1440, 900)
BUTTONS = [(570.0, 300.0), (870.0, 300.0), (870.0, 600.0), (570.0, 600.0)]   # 300 px apart
REACHES = 80
WARMUP = 3.0              # s of holding still before the first reach (the detector needs 2.56 s)
REACH_SECONDS = 0.6
CYCLE_SECONDS = 2.5       # one reach, the click, and a rest
RADII = [22.0, 10.0]
METHODS = [("No filter", "none", "steadiest"), ("One Euro", "one_euro", "steadiest"),
           ("Our model, Steadiest", "learned", "steadiest"), ("Our model, Balanced", "learned", "balanced"),
           ("Our model, Faster", "learned", "responsive")]
ORDER = list(RESPONSE_LEVELS)        # steadiest first: used to break ties
AIM_WINDOWS = [0.0, 0.1, 0.2, 0.3]   # s; "click where you aimed" candidates (0 = off)


def hand_path():
    """Where the hand intends to be at every 10 ms step, and each click's button and times."""
    rng = np.random.default_rng(0)
    steps = int((WARMUP + REACHES * CYCLE_SECONDS) * RATE)
    path = np.tile(np.array(BUTTONS[0]), (steps, 1))
    clicks = []
    for k in range(REACHES):
        start, end = np.array(BUTTONS[k % 4]), np.array(BUTTONS[(k + 1) % 4])
        first = int((WARMUP + k * CYCLE_SECONDS) * RATE)
        n = int(REACH_SECONDS * RATE)
        s = np.arange(1, n + 1) / n
        ease = 10 * s ** 3 - 15 * s ** 4 + 6 * s ** 5              # smooth start and stop
        path[first:first + n] = start + ease[:, None] * (end - start)
        path[first + n:] = end
        press = first + n + int(rng.uniform(0.2, 0.6) * RATE)
        clicks.append((end, press, press + int(rng.uniform(0.08, 0.20) * RATE)))
    return path, clicks


def run(mode, response, level, freeze, path, clicks, aim=0.0):
    """Share of clicks that land for each button size, driving the real B3 logic.
    aim: seconds of "click where you aimed" averaging at the press (0 = off)."""
    steady = sw.SteadyCursor(tuple(path[0]), BOUNDS, mode=mode, demo_level=level, response=response,
                             freeze=freeze, aim_seconds=aim)
    if steady.detector is not None:
        steady.detector.pool = None                 # in line, so results are repeatable
    presses = {p: i for i, (_, p, _) in enumerate(clicks)}
    releases = {r: i for i, (_, _, r) in enumerate(clicks)}
    at_press, at_release = {}, {}
    previous = path[0]
    for k, hand in enumerate(path):
        t = k / RATE
        dx, dy = hand - previous                    # the device's movement this step
        previous = hand
        shown = steady.move_to(steady.shown[0] + dx, steady.shown[1] + dy, t)
        if k in presses:
            at_press[presses[k]] = steady.press(t)    # where the click lands
        if k in releases:
            at_release[releases[k]] = shown
            steady.release()
    steady.stop()
    result = []
    for radius in RADII:
        ok = [np.hypot(*(np.array(at_press[i]) - b)) <= radius and np.hypot(*(np.array(at_release[i]) - b)) <= radius
              for i, (b, _, _) in enumerate(clicks)]
        result.append(float(np.mean(ok)))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--people", choices=["val", "test"], default="val")
    args = parser.parse_args()
    sw.DEMO_FILE = DEMO_FILES[args.people]
    path, clicks = hand_path()

    lines = ["# Clicking real buttons with the system-wide corrector: simulated (%s people's replayed tremor)" % (
                 "validation" if args.people == "val" else "test"), "",
             "Produced by `python evaluation/systemwide_clicks.py --people %s`. The hand reaches 300 px in "
             "%.1f s, stops exactly on the button, presses 0.2-0.6 s later and holds 80-200 ms; %d clicks per "
             "row. Share of clicks that land (on the button at the press and at the release)." % (
                 args.people, REACH_SECONDS, REACHES), "",
             "| Replayed tremor | Method | 22 px: without / with freeze | 10 px: without / with freeze |",
             "|---|---|---|---|"]
    score = {}
    for level in ["medium", "strong"]:
        for name, mode, response in METHODS:
            plain = run(mode, response, level, False, path, clicks)
            frozen = run(mode, response, level, True, path, clicks)
            if level == "strong" and mode == "learned":
                score[response] = frozen[1]
            row = "| %s | %s | %.0f%% / %.0f%% | %.0f%% / %.0f%% |" % (
                level, name, 100 * plain[0], 100 * frozen[0], 100 * plain[1], 100 * frozen[1])
            lines.append(row)
            print(row)
    if args.people == "val":
        best = max(ORDER, key=lambda r: (score[r], -ORDER.index(r)))
        lines += ["", "Rule fixed in advance: B3's default smoothing level is the one with the most clicks landing "
                  "on the 10 px button with click freeze and strong tremor; a tie goes to the steadier level.", "",
                  "**Chosen: %s.**" % best]
        print("Chosen:", best)

    # ---- "Click where you aimed": the click lands at the average shown position of the last moments.
    windows = AIM_WINDOWS if args.people == "val" else sorted({0.0, sw.DEFAULT_AIM_SECONDS})
    lines += ["", "## Click where you aimed (our model, Steadiest, click freeze on)", "",
              "At the press, the click is placed at the average of where the cursor was shown over the last "
              "moments (only while tremor is being corrected). Share of clicks that land.", "",
              "| Averaged over | No tremor: 22 px / 10 px | Medium: 22 px / 10 px | Strong: 22 px / 10 px |", "|---|---|---|---|"]
    aim = {}
    for w in windows:
        aim[w] = {level: run("learned", "steadiest", level, True, path, clicks, aim=w) for level in [None, "medium", "strong"]}
        row = "| %s | %s |" % ("off (click where the cursor is)" if w == 0 else "%.1f s" % w, " | ".join(
            "%.0f%% / %.0f%%" % (100 * aim[w][level][0], 100 * aim[w][level][1]) for level in [None, "medium", "strong"]))
        lines.append(row)
        print(row)
    if args.people == "val":
        off = aim[0.0]
        allowed = [w for w in windows if w > 0 and aim[w]["strong"][1] > off["strong"][1]
                   and all(aim[w][level][k] >= off[level][k] for level in [None, "medium"] for k in (0, 1))]
        chosen = max(allowed, key=lambda w: (aim[w]["strong"][1], -w)) if allowed else 0.0
        lines += ["", "Rule fixed in advance (team leader): choose the window with the most clicks landing on the "
                  "10 px button with strong tremor, if that is more than with it off and no worse with medium "
                  "tremor or no tremor (both button sizes); a tie goes to the shorter window; otherwise it stays off.",
                  "", "**Chosen: %s.**" % ("%.1f s" % chosen if chosen else "off")]
        print("Aim chosen:", chosen)
    lines += ["", "This project is a prototype and is not medical advice.", ""]
    (ROOT / "evaluation" / "results" / f"systemwide_clicks_{args.people}.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
