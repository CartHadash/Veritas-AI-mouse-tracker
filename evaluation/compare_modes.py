"""
compare_modes.py - how much does each filter mode help ON THE DEMO PAGE? (leader's request)

Runs the server's real per-connection code (server.main.CursorSession) in-process, so the
numbers are what the demo page gets. It adds replayed tremor to an intended movement and
measures how far the shown cursor is from the intended path (after a 3 s warm-up) and how
jumpy it is.

Whose tremor (--people):
  val  (default) - 12 recordings of VALIDATION people, built by
                   `python data_pipeline/make_demo_tremor.py --people val` into data/derived/.
                   Use this while developing, so design choices never look at test people.
  test           - the 12 test-people recordings the demo page really replays
                   (server/demo_tremor.npz). Use once, for the final reported figure.

Kinds of intended movement:
  reaches   - the step 4 generator (reaches, pauses, look-alikes): like the training data
  glide     - one slow, smooth, continuous curve (like the leader's test path)
  still     - a hand holding still
"60 Hz, uneven" sends samples like a browser does (about 60 per second, uneven timing).

Jerkiness (how much the shown cursor's velocity changes from one 10 ms step to the next; the
cursor is first placed on an even 100 Hz time grid so uneven timing does not count as
jerkiness) is reported next to distance, because distance alone hid a jumpy cursor.

Run from the repository folder (about two minutes):
    python evaluation/compare_modes.py                 # validation people (development)
    python evaluation/compare_modes.py --people test   # test people (final figure)
Writes evaluation/results/demo_modes_<people>.md.
"""

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "data_pipeline"))
import server.main as server  # noqa: E402
from evaluation.metrics import jerkiness  # noqa: E402
from synthetic_paths import generate_path  # noqa: E402

SECONDS = 41          # 4 demo recordings per strength level x 10.24 s: each plays once
WARMUP = 3.0
DEMO_FILES = {"val": ROOT / "data" / "derived" / "demo_tremor_val.npz",
              "test": ROOT / "server" / "demo_tremor.npz"}


def intended_paths(rate=100, uneven=False, seed=0):
    rng = np.random.default_rng(seed)
    n = int(SECONDS * rate)
    if uneven:
        t = np.cumsum(rng.uniform(0.6, 1.4, n) / rate)       # browser-like uneven timing
    else:
        t = np.arange(n) / rate
    reaches_100, _ = generate_path(rng, int(SECONDS * 100) + 200)
    # Resample the 100 Hz generated path to the chosen sample times.
    grid = np.arange(len(reaches_100)) / 100
    reaches = np.stack([np.interp(t, grid, reaches_100[:, k]) for k in range(2)], axis=1)
    glide = np.stack([600 + 200 * np.sin(t / 3), 400 + 100 * np.sin(t / 5)], axis=1)
    still = np.tile([[500.0, 400.0]], (n, 1))
    return t, {"reaches": reaches, "glide": glide, "still": still}


def run(mode, t, path, demo=True, level="medium"):
    """Feed one path through a fresh demo-page session; return shown cursor and gate."""
    server.settings.update(mode=mode, strength=1.0, demo_tremor=demo, demo_level=level)
    session = server.CursorSession(server.SessionStats())
    session.detector.pool = None           # run the detector in line, so results are repeatable
    shown, gates = [], []
    for ti, (x, y) in zip(t, path):
        reply = session.update(float(ti), float(x), float(y))
        shown.append((reply["x"], reply["y"]))
        gates.append(reply["gate"] if reply["gate"] is not None else np.nan)
    return np.array(shown), np.array(gates)


def distance(shown, path, t):
    keep = t >= WARMUP
    return float(np.linalg.norm(shown[keep] - path[keep], axis=1).mean())


def even_jerkiness(positions, t):
    """Jerkiness after placing the positions on an even 100 Hz grid (after the warm-up)."""
    grid = np.arange(WARMUP, t[-1], 0.01)
    even = np.stack([np.interp(grid, t, positions[:, k]) for k in range(2)], axis=1)
    return jerkiness(even)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--people", choices=["val", "test"], default="val")
    args = parser.parse_args()
    server.DEMO_TREMOR_FILE = DEMO_FILES[args.people]      # whose tremor is replayed
    who = "VALIDATION people (development)" if args.people == "val" else "TEST people (final figure)"

    lines = ["# Filter modes on the demo page: replayed tremor of %s" % who, "",
             "Produced by `python evaluation/compare_modes.py --people %s`. Average distance (px) between "
             "the shown cursor and the intended path after a 3 s warm-up, over %d s so all 4 recordings "
             "of a strength level play once. Uses the server's own session code. First table: medium "
             "replayed tremor (the page's default)." % (args.people, SECONDS), "",
             "Jerkiness = average size of the change in the shown cursor's velocity from one 10 ms step "
             "to the next, on an even 100 Hz time grid (px).", "",
             "| Intended movement | Off the path: no filter / One Euro / our model (px) "
             "| Jerkiness: no filter / One Euro / our model (px) | Intended path jerkiness | Gate above 0.5 |",
             "|---|---|---|---|---|"]
    for label, rate, uneven in [("100 Hz", 100, False), ("60 Hz, uneven", 60, True)]:
        t, paths = intended_paths(rate, uneven)
        for name, path in paths.items():
            if uneven and name == "still":
                continue
            none, _ = run("none", t, path)
            euro, _ = run("one_euro", t, path)
            ours, gate = run("learned", t, path)
            open_share = np.nanmean(gate[t >= WARMUP] > 0.5)
            row = "| %s (%s) | %.2f / %.2f / %.2f | %.2f / %.2f / %.2f | %.2f | %.0f%% |" % (
                name, label, distance(none, path, t), distance(euro, path, t), distance(ours, path, t),
                even_jerkiness(none, t), even_jerkiness(euro, t), even_jerkiness(ours, t),
                even_jerkiness(path, t), 100 * open_share)
            lines.append(row)
            print(row)
    lines += ["", "## By replayed tremor strength (reaches and still hand, 100 Hz)", "",
              "| Replayed tremor | Movement | Off the path: no filter / One Euro / our model (px) "
              "| Our model vs no filter | Jerkiness: no filter / One Euro / our model (px) |",
              "|---|---|---|---|---|"]
    t, paths = intended_paths()
    for level in ["mild", "medium", "strong"]:
        for name in ["reaches", "still"]:
            outs = [run(mode, t, paths[name], level=level)[0] for mode in ("none", "one_euro", "learned")]
            d0, d1, d2 = (distance(o, paths[name], t) for o in outs)
            j0, j1, j2 = (even_jerkiness(o, t) for o in outs)
            row = "| %s | %s | %.2f / %.2f / %.2f | %.0f%% closer | %.2f / %.2f / %.2f |" % (
                level, name, d0, d1, d2, 100 * (1 - d2 / d0), j0, j1, j2)
            lines.append(row)
            print(row)
    ours, gate = run("learned", t, paths["reaches"], demo=False)
    lines += ["", "Replayed tremor OFF, reaches at 100 Hz: our model %.2f px from the path (no filter 0.00 px); "
              "gate above 0.5 for %.0f%% of the time." % (distance(ours, paths["reaches"], t),
                                                           100 * np.nanmean(gate[t >= WARMUP] > 0.5)), "",
              "This project is a prototype and is not medical advice.", ""]
    (ROOT / "evaluation" / "results" / f"demo_modes_{args.people}.md").write_text("\n".join(lines), encoding="utf-8")
    print(lines[-4])


if __name__ == "__main__":
    main()
