"""
compare_modes.py - how much does each filter mode help ON THE DEMO PAGE? (leader's request)

Runs the server's real per-connection code (server.main.CursorSession) in-process, so the
numbers are what the demo page gets. For each kind of intended movement it adds the demo
tremor (the 8 test-people recordings the page replays) and measures the average distance
between the shown cursor and the intended path, after a 3 s warm-up.

Kinds of intended movement:
  reaches   - the step 4 generator (reaches, pauses, look-alikes): like the training data
  glide     - one slow, smooth, continuous curve (like the leader's test path)
  still     - a hand holding still
Extra rows help find WHY the demo gain can be small:
  "gate forced open" runs the corrector without the detector gate;
  "away from seams" ignores 0.3 s after each switch to the next demo recording (every 10.24 s);
  "60 Hz, uneven" sends samples like a browser does (about 60 per second, uneven timing).

Run from the repository folder (about a minute):
    python evaluation/compare_modes.py
Writes evaluation/results/demo_modes.md. No dataset needed (uses server/demo_tremor.npz).
"""

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "data_pipeline"))
import server.main as server  # noqa: E402
from models.corrector.live import LiveCorrector  # noqa: E402
from synthetic_paths import generate_path  # noqa: E402

RESULT = ROOT / "evaluation" / "results" / "demo_modes.md"
SECONDS = 41          # 4 demo recordings per strength level x 10.24 s: each plays once
WARMUP = 3.0


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


def run(mode, t, path, demo=True, forced_open=False, level="medium"):
    """Feed one path through a fresh demo-page session; return shown cursor and gate."""
    server.settings.update(mode=mode, strength=1.0, demo_tremor=demo, demo_level=level)
    server.settings_version[0] += 1
    session = server.CursorSession(server.SessionStats())
    session.detector.pool = None           # run the detector in line, so results are repeatable
    if forced_open:
        session.filter = LiveCorrector(use_gate=False, model=server.CORRECTOR_MODEL)
        session.filter.reset()
    shown, gates = [], []
    for ti, (x, y) in zip(t, path):
        reply = session.update(float(ti), float(x), float(y))
        shown.append((reply["x"], reply["y"]))
        gates.append(reply["gate"] if reply["gate"] is not None else np.nan)
    return np.array(shown), np.array(gates)


def distance(shown, path, t, away_from_seams=False):
    keep = t >= WARMUP
    if away_from_seams:
        keep &= (t % 10.24) > 0.3
    return float(np.linalg.norm(shown[keep] - path[keep], axis=1).mean())


def main():
    lines = ["# Filter modes on the demo page (demo tremor ON unless stated)", "",
             "Produced by `python evaluation/compare_modes.py`. Average distance (px) between the shown "
             "cursor and the intended path after a 3 s warm-up, over %d s so all 4 demo recordings of "
             "a strength level play once. Uses the server's own session code. First table: medium "
             "demo tremor (the page's default)." % SECONDS, "",
             "| Intended movement | No filter | One Euro | Our model | Our model, gate forced open "
             "| Our model, away from seams | Gate above 0.5 |", "|---|---|---|---|---|---|---|"]
    for label, rate, uneven in [("100 Hz", 100, False), ("60 Hz, uneven", 60, True)]:
        t, paths = intended_paths(rate, uneven)
        for name, path in paths.items():
            if uneven and name == "still":
                continue
            none, _ = run("none", t, path)
            euro, _ = run("one_euro", t, path)
            ours, gate = run("learned", t, path)
            forced, _ = run("learned", t, path, forced_open=True)
            open_share = np.nanmean(gate[t >= WARMUP] > 0.5)
            row = "| %s (%s) | %.2f | %.2f | %.2f | %.2f | %.2f | %.0f%% |" % (
                name, label, distance(none, path, t), distance(euro, path, t), distance(ours, path, t),
                distance(forced, path, t), distance(ours, path, t, away_from_seams=True), 100 * open_share)
            lines.append(row)
            print(row)
    lines += ["", "## By demo tremor strength (reaches and still hand, 100 Hz)", "",
              "| Demo tremor | Movement | No filter | One Euro | Our model | Our model vs no filter |",
              "|---|---|---|---|---|---|"]
    t, paths = intended_paths()
    for level in ["mild", "medium", "strong"]:
        for name in ["reaches", "still"]:
            none, _ = run("none", t, paths[name], level=level)
            euro, _ = run("one_euro", t, paths[name], level=level)
            ours, _ = run("learned", t, paths[name], level=level)
            d0, d1, d2 = (distance(o, paths[name], t) for o in (none, euro, ours))
            row = "| %s | %s | %.2f | %.2f | %.2f | %.0f%% closer |" % (level, name, d0, d1, d2, 100 * (1 - d2 / d0))
            lines.append(row)
            print(row)
    ours, gate = run("learned", t, paths["reaches"], demo=False)
    lines += ["", "Demo tremor OFF, reaches at 100 Hz: our model %.2f px from the path (no filter 0.00 px); "
              "gate above 0.5 for %.0f%% of the time." % (distance(ours, paths["reaches"], t),
                                                           100 * np.nanmean(gate[t >= WARMUP] > 0.5)), "",
              "This project is a prototype and is not medical advice.", ""]
    RESULT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[-4:]))


if __name__ == "__main__":
    main()
