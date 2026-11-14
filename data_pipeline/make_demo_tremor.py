"""
make_demo_tremor.py - save a few real tremor recordings for the app's "demo tremor" switch.

None of us has a tremor, so the demo page can add a real patient's recorded tremor on top of
the user's live movement. The full library lives in data/ (not in git), so this script copies
a handful of segments into a small file that IS in git: server/demo_tremor.npz (about 70 KB).

Only TEST people are used, so the demo never replays tremor the models were trained on.
Three strength levels the demo page can choose between (4 recordings each, at most one per
person per level, different diagnoses where possible), because our models work very
differently by size (see evaluation/results/improvements.md):
  mild 1.5-3 px, medium 4-10 px, strong 10-25 px on screen.

Source data: PADS and TremorDB (credited in docs/SOURCES.md; PADS is CC BY-NC-SA 4.0).

Run from the repository folder:
    python data_pipeline/make_demo_tremor.py
"""

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "data" / "derived" / "tremor_library.npz"
SPLIT = ROOT / "data_pipeline" / "split.json"
OUT = ROOT / "server" / "demo_tremor.npz"
COUNT = 4
LEVELS = [("mild", 1.5, 3), ("medium", 4, 10), ("strong", 10, 25)]


def pick(lib, test_people, low, high):
    ok = (np.isin(lib["subject"], list(test_people)) & lib["tremor"]
          & (lib["strength_px"] >= low) & (lib["strength_px"] <= high) & (lib["condition"] != "Healthy"))
    candidates = np.flatnonzero(ok)
    rng = np.random.default_rng(0)
    rng.shuffle(candidates)

    # Prefer variety: first one segment per diagnosis, then fill up with other people.
    chosen, people, conditions = [], set(), set()
    for prefer_new_condition in (True, False):
        for i in candidates:
            if len(chosen) == COUNT:
                break
            subject, condition = str(lib["subject"][i]), str(lib["condition"][i])
            if subject in people or (prefer_new_condition and condition in conditions):
                continue
            chosen.append(i)
            people.add(subject)
            conditions.add(condition)
    return chosen


def main():
    lib = np.load(LIBRARY)
    with open(SPLIT, encoding="utf-8") as f:
        test_people = set(json.load(f)["test"])
    chosen, levels = [], []
    for level, low, high in LEVELS:
        picked = pick(lib, test_people, low, high)
        chosen += picked
        levels += [level] * len(picked)

    np.savez_compressed(
        OUT, xy=lib["xy"][chosen].astype(np.float32), subject=lib["subject"][chosen],
        condition=lib["condition"][chosen], dataset=lib["dataset"][chosen],
        strength_px=lib["strength_px"][chosen], peak_hz=lib["peak_hz"][chosen], level=np.array(levels))
    print("Saved %d demo tremor segments (10.24 s each) -> %s (%.0f KB)" % (
        len(chosen), OUT.relative_to(ROOT), OUT.stat().st_size / 1000))
    for i, level in zip(chosen, levels):
        print("  %-7s %-10s %-26s %5.1f px  %.1f Hz" % (level, lib["subject"][i], lib["condition"][i],
                                                       lib["strength_px"][i], lib["peak_hz"][i]))


if __name__ == "__main__":
    main()
