"""
make_path_check.py - the paths for the team's step 4 check (web/path_check.html).

Step 4 is "done" when a human finds the generated movement plausible. This makes that check
blind: 12 paths of 10.24 s, 6 from the generator the models were trained on ("current") and 6
from the realistic version (realistic=True, seen through device_view), shuffled. The page
replays each one at real speed; the tester rates it without knowing which version it is.
Only the clean "intended" movement is shown (no tremor): step 4 is about that movement.

Needs no datasets. Run from the repository folder:
    python data_pipeline/make_path_check.py
Writes web/path_check_paths.json (small, committed, so the page works from a fresh clone).
"""

import json
from pathlib import Path

import numpy as np

from synthetic_paths import KIND_NAMES, RATE, SCREEN_H, SCREEN_W, device_view, generate_path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "web" / "path_check_paths.json"
PER_VERSION = 6
SEED = 2026


def main():
    rng = np.random.default_rng(SEED)
    paths = []
    for version in ["current", "realistic"]:
        for _ in range(PER_VERSION):
            xy, kind = generate_path(rng, 1024, realistic=(version == "realistic"))
            if version == "realistic":
                xy = device_view(xy, rng)
            paths.append({"version": version,
                          "xy": np.round(xy, 1).tolist(),
                          "kind": kind.tolist()})
    order = rng.permutation(len(paths))
    shuffled = [dict(paths[i], id="P%d" % (n + 1)) for n, i in enumerate(order)]
    OUT.write_text(json.dumps({"rate": RATE, "screen": [SCREEN_W, SCREEN_H], "seed": SEED, "kind_names": KIND_NAMES,
                               "paths": shuffled}, separators=(",", ":")), encoding="utf-8")
    print("Saved %s (%d paths, %.0f KB)" % (OUT.relative_to(ROOT), len(shuffled), OUT.stat().st_size / 1024))


if __name__ == "__main__":
    main()
