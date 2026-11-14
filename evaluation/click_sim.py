"""
click_sim.py - does "click freeze" help clicks land? A simulation (no real people).

A click on a button only counts if the button is pressed AND released on it. Tremor while the
button is held can carry the cursor off before the release. Click freeze (an idea from Timofey,
a team member) holds the shown cursor still from press to release (at most 0.3 s).

The simulation: a hand aimed perfectly at the centre of a target of radius 22 px (the demo
page's) holds still while replayed tremor shakes it. Clicks start every 0.4 s and are held
for 80-200 ms (a typical click; our assumption). Using the server's own code for each filter
mode, we count clicks that succeed:
  without freeze - the shown cursor is on the target at the press AND at the release;
  with freeze    - it is on the target at the press (the release happens at the same spot).
Because the aim is perfect, every miss is caused by the shaking alone. Real people also jolt
the mouse when pressing the button; we have no data for that, so it is not simulated.

Whose tremor (--people), as in compare_modes.py:
  val  (default) - validation people's recordings (development)
  test           - the demo page's test-people recordings (final figure, once)

Run from the repository folder:
    python evaluation/click_sim.py
    python evaluation/click_sim.py --people test
Writes evaluation/results/click_freeze_<people>.md.
"""

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import server.main as server  # noqa: E402
from evaluation.compare_modes import DEMO_FILES, SECONDS, WARMUP  # noqa: E402

# Target radii: 22 px is the demo page's target. 10 px (about the size of small real controls
# such as checkboxes or close buttons) was added after seeing that 22 px is easy to hit.
RADII = [22.0, 10.0]
CENTRE = np.array([500.0, 400.0])
MODES = [("none", "No filter"), ("one_euro", "One Euro"), ("learned", "Our model")]


def shown_path(mode, level, t):
    """The shown cursor for a still hand at the target centre with replayed tremor."""
    server.settings.update(mode=mode, strength=1.0, demo_tremor=True, demo_level=level)
    session = server.CursorSession(server.SessionStats())
    session.detector.pool = None          # in line, so results are repeatable
    return np.array([[r["x"], r["y"]] for r in
                     (session.update(float(ti), *CENTRE) for ti in t)])


def click_success(shown, t, rng, radius):
    """Share of simulated clicks that succeed without and with click freeze."""
    on = np.linalg.norm(shown - CENTRE, axis=1) <= radius
    starts = np.arange(WARMUP, t[-1] - 0.3, 0.4)
    durations = rng.uniform(0.08, 0.20, len(starts))
    down = np.searchsorted(t, starts)
    up = np.searchsorted(t, starts + durations)
    plain = on[down] & on[up]
    frozen = on[down]
    return plain.mean(), frozen.mean(), len(starts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--people", choices=["val", "test"], default="val")
    args = parser.parse_args()
    server.DEMO_TREMOR_FILE = DEMO_FILES[args.people]
    t = np.arange(int(SECONDS * 100)) / 100

    lines = ["# Click freeze: simulated clicks (%s people's replayed tremor)" % (
                 "validation" if args.people == "val" else "test"), "",
             "Produced by `python evaluation/click_sim.py --people %s`. Perfect aim, hand still, clicks "
             "held 80-200 ms; misses come only from the shaking. Share of clicks that succeed "
             "(pressed and released on the target)." % args.people, "",
             "The 22 px target is the demo page's; the 10 px target (about a small checkbox) was "
             "added after seeing that 22 px is easy.", "",
             "| Replayed tremor | Filter | Clicks | 22 px: without / with freeze | 10 px: without / with freeze |",
             "|---|---|---|---|---|"]
    for level in ["mild", "medium", "strong"]:
        for mode, name in MODES:
            shown = shown_path(mode, level, t)
            cells = []
            for radius in RADII:
                plain, frozen, n = click_success(shown, t, np.random.default_rng(0), radius)
                cells.append("%.0f%% / %.0f%%" % (100 * plain, 100 * frozen))
            row = "| %s | %s | %d | %s | %s |" % (level, name, n, *cells)
            lines.append(row)
            print(row)
    lines += ["", "This project is a prototype and is not medical advice.", ""]
    (ROOT / "evaluation" / "results" / f"click_freeze_{args.people}.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
