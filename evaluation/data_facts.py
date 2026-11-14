"""
data_facts.py - step 14: the dataset facts the write-up needs, counted from the built data.

Writes evaluation/results/dataset_facts.md with: people per dataset and split, test people per
group (diagnosis, age band, sex), tremor library size and tremor-marked counts, detector windows
and corrector sequences per split, the pixel factors, and the demo recordings.

Run from the repository folder (needs data/derived, built by the data_pipeline scripts):
    python evaluation/data_facts.py
"""

import json
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULT = ROOT / "evaluation" / "results" / "dataset_facts.md"
SPLITS = ["train", "val", "test"]


def counts(values):
    return ", ".join("%s %d" % (k, v) for k, v in sorted(Counter(values).items()))


def main():
    lib = np.load(DERIVED / "tremor_library.npz")
    with open(ROOT / "data_pipeline" / "split.json", encoding="utf-8") as f:
        split = json.load(f)

    # One row per person (the library has many segments per person).
    people = {}
    for s, d, c, a, x in zip(lib["subject"], lib["dataset"], lib["condition"], lib["age_band"], lib["sex"]):
        people[str(s)] = (str(d), str(c), str(a), str(x))

    lines = ["# Dataset facts", "", "Produced by `python evaluation/data_facts.py` from the built data.", "",
             "## People", "",
             "- People with recordings: %d (%s)." % (len(people), counts(p[0] for p in people.values())),
             "- Split by person (seed 42): %s." % ", ".join("%s %d" % (n, len(split[n])) for n in SPLITS),
             "- Test people by diagnosis: %s." % counts(people[s][1] for s in split["test"]),
             "- Test people by age band: %s." % counts(people[s][2] for s in split["test"]),
             "- Test people by sex: %s." % counts(people[s][3] for s in split["test"]),
             "", "## Tremor library (10.24 s segments)", "",
             "- Segments: %d; tremor-marked: %d." % (len(lib["tremor"]), lib["tremor"].sum()),
             "- Tremor-marked segments by diagnosis: %s." % counts(
                 "%s (%s)" % (c, d) for c, d, t in zip(lib["condition"], lib["dataset"], lib["tremor"]) if t),
             "- Pixel factor: PADS %.1f px per radian; TremorDB %.1f px per unit." % (
                 float(lib["pixel_factor_pads"]), float(lib["pixel_factor_tremordb"])),
             "- On-screen size of tremor-marked segments: median %.1f px, 10th-90th percentile %.1f-%.1f px." % (
                 np.median(lib["strength_px"][lib["tremor"]]), *np.percentile(lib["strength_px"][lib["tremor"]], [10, 90])),
             "", "## Examples per split", "",
             "| Split | Detector windows (2.56 s) | of which tremor | Pause-free windows (step 12) "
             "| Corrector sequences (5.12 s) | of which marked tremor |", "|---|---|---|---|---|---|"]
    for name in SPLITS:
        det = np.load(DERIVED / f"detector_{name}.npz")
        cont = np.load(DERIVED / f"detector_{name}_continuous.npz")
        cor = np.load(DERIVED / f"corrector_{name}.npz")
        lines.append("| %s | %d | %d | %d | %d | %d |" % (
            name, len(det["label"]), det["label"].sum(), len(cont["label"]), len(cor["tremor"]), cor["tremor"].sum()))

    demo = np.load(ROOT / "server" / "demo_tremor.npz")
    lines += ["", "## Demo page recordings (test people only)", "",
              "- %d recordings: %s." % (len(demo["level"]), counts(demo["level"])), "",
              "This project is a prototype and is not medical advice.", ""]
    RESULT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
