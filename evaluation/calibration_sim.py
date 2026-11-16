"""
calibration_sim.py - does a 10-second calibration test pick a better filter for each person?
(A simulation with recorded tremor, no live people.)

The calibration test on the demo page: hold the pointer on a dot for 4 s, then follow the dot as
it moves slowly for about 6 s. Because the app knows where the dot was, it can replay the
person's own test through each candidate filter and keep the one that stayed closest to the dot.

Why not "measure the mouse's speed setting"? The cursor alone cannot tell strong tremor on a slow
mouse from mild tremor on a fast one, so the device setting itself cannot be measured. What we
can measure is how each filter does on THIS person's shaking on THIS device.

The simulation, for each person:
  - one of their 10.24 s tremor recordings is the calibration test (still dot, then moving dot);
  - two OTHER recordings of the same person are "later use" (computer-generated reaches);
  - the tremor is used at 0.5x, 1x and 2x size (like different mouse speed settings);
  - every candidate filter runs through the server's own code (server.main.CursorSession).
We compare the later-use distance from the intended path for: always our model (the app's
default), always One Euro, the calibration's choice, and the best choice in hindsight.

Whose recordings (--people): val (default, development) or test (the final figure, once).

Run from the repository folder (needs data/derived/tremor_library.npz; a few minutes):
    python evaluation/calibration_sim.py
    python evaluation/calibration_sim.py --people test
Writes evaluation/results/calibration_<people>.md.

Outcome (validation): the calibration's choice was WORSE than always using our
model at every size, and even the best choice in hindsight gained under 0.1 px. So the app's
test only reports the distances and never switches the filter; the test-people run was not
done, because the method was not kept.
"""

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "data_pipeline"))

LIBRARY = ROOT / "data" / "derived" / "tremor_library.npz"
SPLIT_FILE = ROOT / "data_pipeline" / "split.json"
SCALES = [0.5, 1.0, 2.0]
SKIP = 256                    # score after the detector's first full 2.56 s window
USE_RECORDINGS = 2            # "later use" recordings per person
SEED = 0


def calibration_path(n=1024):
    """Where the dot is during the test: still for 4 s, then a slow circle (radius 120 px, one
    turn in 8 s, about 94 px/s). The page draws the same path (web/app.js, calibrationDot)."""
    t = np.arange(n) / 100
    angle = 2 * np.pi * np.clip(t - 4.0, 0, None) / 8.0
    return np.stack([500 + 120 * np.sin(angle), 400 - 120 * (1 - np.cos(angle))], axis=1)


def run(candidate, path, tremor):
    """Feed path + tremor through a fresh session with one candidate filter (the server's own
    replay, the same code the calibration test uses); distance from the path after 2.56 s."""
    from server.main import replay
    shaky = path + tremor
    replies = replay(*candidate, [(i / 100, float(x), float(y)) for i, (x, y) in enumerate(shaky)])
    shown = np.array([[r["x"], r["y"]] for r in replies])
    return float(np.linalg.norm(shown[SKIP:] - path[SKIP:], axis=1).mean())


def one_person(job):
    """Distances for every candidate on the calibration test and on later use, at each scale."""
    from server.main import CANDIDATES
    from synthetic_paths import generate_path
    segments, seed = job
    rng = np.random.default_rng(seed)
    calib = calibration_path()
    uses = [generate_path(rng, 1024)[0] for _ in segments[1:]]
    out = {}
    for scale in SCALES:
        test = [run(c, calib, scale * segments[0]) for c in CANDIDATES]
        later = [np.mean([run(c, use, scale * seg) for use, seg in zip(uses, segments[1:])]) for c in CANDIDATES]
        out[scale] = (test, later)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--people", choices=["val", "test"], default="val")
    args = parser.parse_args()
    from server.main import CANDIDATES, CANDIDATE_NAMES

    lib = np.load(LIBRARY)
    with open(SPLIT_FILE, encoding="utf-8") as f:
        people = json.load(f)[args.people]
    subject, tremor_marked = lib["subject"].astype(str), lib["tremor"]
    rng = np.random.default_rng(SEED)
    jobs, has_tremor = [], []
    for k, person in enumerate(people):
        rows = np.flatnonzero(subject == person)
        if len(rows) < 1 + USE_RECORDINGS:
            continue
        pick = rng.choice(rows, 1 + USE_RECORDINGS, replace=False)
        jobs.append((lib["xy"][pick], SEED + k))
        has_tremor.append(bool(tremor_marked[rows].any()))
    has_tremor = np.array(has_tremor)

    with ProcessPoolExecutor() as pool:
        results = list(pool.map(one_person, jobs))

    default = CANDIDATES.index(("learned", 1.0))
    euro = CANDIDATES.index(("one_euro", 1.0))
    lines = ["# Calibration test: does choosing the filter per person help? (%s people)" % (
                 "validation" if args.people == "val" else "test"), "",
             "Produced by `python evaluation/calibration_sim.py --people %s`. For each of %d people "
             "(%d with any tremor-marked recording): one recording is the 10 s calibration test (still "
             "dot, then slowly moving dot), two other recordings of the same person are later use "
             "(computer-generated reaches). The tremor is used at 0.5x, 1x and 2x size, like different "
             "mouse speed settings. Average distance (px) from the intended path during later use, "
             "after the first 2.56 s." % (args.people, len(jobs), has_tremor.sum()), "",
             "| Tremor size | People | Always our model | Always One Euro | Calibration's choice "
             "| Best in hindsight | Calibration chose |", "|---|---|---|---|---|---|---|"]
    for scale in SCALES:
        test = np.array([r[scale][0] for r in results])
        later = np.array([r[scale][1] for r in results])
        chosen = test.argmin(axis=1)
        for group, mask in [("all", np.ones(len(jobs), bool)), ("with tremor", has_tremor)]:
            got = later[mask, chosen[mask]]
            picks = ", ".join("%s %d" % (CANDIDATE_NAMES[i], (chosen[mask] == i).sum())
                              for i in range(len(CANDIDATES)) if (chosen[mask] == i).any())
            row = "| %.1fx | %s %d | %.2f | %.2f | %.2f | %.2f | %s |" % (
                scale, group, mask.sum(), later[mask, default].mean(), later[mask, euro].mean(),
                got.mean(), later[mask].min(axis=1).mean(), picks)
            lines.append(row)
            print(row)
    lines += ["", "This project is a prototype and is not medical advice.", ""]
    (ROOT / "evaluation" / "results" / f"calibration_{args.people}.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
