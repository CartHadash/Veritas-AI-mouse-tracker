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
AIM_WINDOWS = [0.0, 0.1, 0.2, 0.3]   # s; "click where you aimed" candidates for the page (0 = off)
PAGE_AIM_SECONDS = 0.1               # what the page uses (web/app.js AIM_MS), chosen on validation by the rule below


def shown_path(mode, level, t):
    """The shown cursor for a still hand at the target centre with replayed tremor."""
    server.settings.update(mode=mode, strength=1.0, demo_tremor=True, demo_level=level)
    session = server.CursorSession(server.SessionStats())
    session.detector.pool = None          # in line, so results are repeatable
    replies = [session.update(float(ti), *CENTRE) for ti in t]
    gates = np.array([r["gate"] if r["gate"] is not None else 0.0 for r in replies])
    return np.array([[r["x"], r["y"]] for r in replies]), gates


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


def aimed_success(shown, gates, t, rng, radius, window):
    """Share of clicks that land with click freeze when the click is placed at the average of
    the shown positions of the last `window` seconds ("click where you aimed"), which is done
    only while our model is correcting (gate over half open). window 0 = off."""
    starts = np.arange(WARMUP, t[-1] - 0.3, 0.4)
    rng.uniform(0.08, 0.20, len(starts))             # same random draws as click_success (not used: frozen)
    down = np.searchsorted(t, starts)
    landed = []
    for d in down:
        point = shown[d]
        if window > 0 and gates[d] > 0.5:
            point = shown[(t > t[d] - window - 1e-9) & (t <= t[d] + 1e-9)].mean(axis=0)
        landed.append(np.linalg.norm(point - CENTRE) <= radius)
    return float(np.mean(landed))


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
            shown, _ = shown_path(mode, level, t)
            cells = []
            for radius in RADII:
                plain, frozen, n = click_success(shown, t, np.random.default_rng(0), radius)
                cells.append("%.0f%% / %.0f%%" % (100 * plain, 100 * frozen))
            row = "| %s | %s | %d | %s | %s |" % (level, name, n, *cells)
            lines.append(row)
            print(row)
    # ---- "Click where you aimed" on the page (our model, click freeze on).
    windows = AIM_WINDOWS if args.people == "val" else sorted({0.0, PAGE_AIM_SECONDS})
    lines += ["", "## Click where you aimed (our model, click freeze on)", "",
              "At the press the click is placed at the average of where the cursor was shown over the last "
              "moments, only while our model is correcting. Share of clicks that land.", "",
              "| Averaged over | Mild: 22 px / 10 px | Medium: 22 px / 10 px | Strong: 22 px / 10 px |", "|---|---|---|---|"]
    aim = {}
    paths = {level: shown_path("learned", level, t) for level in ["mild", "medium", "strong"]}
    for w in windows:
        aim[w] = {level: [aimed_success(*paths[level], t, np.random.default_rng(0), radius, w) for radius in RADII]
                  for level in paths}
        row = "| %s | %s |" % ("off (click where the cursor is)" if w == 0 else "%.1f s" % w, " | ".join(
            "%.0f%% / %.0f%%" % (100 * aim[w][level][0], 100 * aim[w][level][1]) for level in paths))
        lines.append(row)
        print(row)
    if args.people == "val":
        off = aim[0.0]
        allowed = [w for w in windows if w > 0 and aim[w]["strong"][1] > off["strong"][1]
                   and all(aim[w][level][k] >= off[level][k] for level in ["mild", "medium"] for k in (0, 1))]
        chosen = max(allowed, key=lambda w: (aim[w]["strong"][1], -w)) if allowed else 0.0
        lines += ["", "Rule fixed in advance (the same as for the system-wide corrector): choose the window with the "
                  "most clicks landing on the 10 px target with strong tremor, if that is more than with it off and "
                  "no worse with mild or medium tremor (both sizes); a tie goes to the shorter window; otherwise off.",
                  "", "**Chosen: %s.**" % ("%.1f s" % chosen if chosen else "off")]
        print("Aim chosen:", chosen)
    lines += ["", "This project is a prototype and is not medical advice.", ""]
    (ROOT / "evaluation" / "results" / f"click_freeze_{args.people}.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
