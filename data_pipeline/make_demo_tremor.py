"""
make_demo_tremor.py - save a few real tremor recordings for the app's "demo tremor" switch.

None of us has a tremor, so the demo page can add a real patient's recorded tremor on top of
the user's live movement. The full library lives in data/ (not in git), so this script copies
a handful of segments into a small file that IS in git: server/demo_tremor.npz (about 70 KB).

Only TEST people are used, so the demo never replays tremor the models were trained on.
Chosen: tremor-marked segments of 4-15 px on screen (clearly visible but not absurd), at most
one per person, from different diagnoses where possible.

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
COUNT = 8


def main():
    lib = np.load(LIBRARY)
    with open(SPLIT, encoding="utf-8") as f:
        test_people = set(json.load(f)["test"])
    ok = (np.isin(lib["subject"], list(test_people)) & lib["tremor"]
          & (lib["strength_px"] >= 4) & (lib["strength_px"] <= 15) & (lib["condition"] != "Healthy"))
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

    np.savez_compressed(
        OUT, xy=lib["xy"][chosen].astype(np.float32), subject=lib["subject"][chosen],
        condition=lib["condition"][chosen], dataset=lib["dataset"][chosen],
        strength_px=lib["strength_px"][chosen], peak_hz=lib["peak_hz"][chosen])
    print("Saved %d demo tremor segments (10.24 s each) -> %s (%.0f KB)" % (
        len(chosen), OUT.relative_to(ROOT), OUT.stat().st_size / 1000))
    for i in chosen:
        print("  %-10s %-26s %5.1f px  %.1f Hz" % (lib["subject"][i], lib["condition"][i],
                                                  lib["strength_px"][i], lib["peak_hz"][i]))


if __name__ == "__main__":
    main()
