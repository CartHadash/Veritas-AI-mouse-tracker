"""
build_dataset.py - step 5: turn the tremor library (step 3) and synthetic movement (step 4)
into labelled examples, split BY PERSON into train / validation / test.

  1. SPLIT. Every person (469 PADS + 16 TremorDB) goes into exactly one group:
     70% train (to learn from), 15% validation (to tune settings), 15% test (locked away
     for the final score). The split is done separately inside each diagnosis group of each
     dataset, so every group is represented in all three. Fixed seed. Saved to
     data_pipeline/split.json, which is committed (it contains only subject ids).

  2. DETECTOR EXAMPLES: windows of 2.56 s (256 samples) of cursor movement.
     Positive (label 1) = synthetic movement + a window of a tremor-marked patient segment.
     Negative (label 0) = synthetic movement alone, or + a healthy person's segment (their
     tiny natural tremor), or + a patient segment that was NOT tremor-marked.

  3. CORRECTOR EXAMPLES: sequences of 5.12 s (512 samples): shaky input = clean synthetic
     movement + tremor; target = the clean movement. All tremor sizes, plus sequences with
     no tremor at all (the corrector must leave a steady hand alone).

Healthy segments that happen to pass the tremor rule (61 in the library) are left out, so
no "no tremor" example contains rule-passing tremor.

Run from the repository folder:
    python data_pipeline/build_dataset.py                    # normal pixel factor
    python data_pipeline/build_dataset.py --tremor-scale 0.5 # half (DECISION 1 check)
    python data_pipeline/build_dataset.py --tremor-scale 2   # double
    python data_pipeline/build_dataset.py --continuous       # step 12: pause-free movement
Output: data/derived/detector_<split>.npz and corrector_<split>.npz (not in git).
"""

import argparse
import json
from collections import Counter
from pathlib import Path

import sys

import numpy as np

from synthetic_paths import CONTINUOUS_EVENTS, EVENTS, LOOKALIKES, generate_path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evaluation.metrics import window_is_moving  # noqa: E402  (one shared meaning of "moving")

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "data" / "derived" / "tremor_library.npz"
OUT_DIR = ROOT / "data" / "derived"
SPLIT_FILE = ROOT / "data_pipeline" / "split.json"

SPLIT_SEED = 42
SPLITS = ["train", "val", "test"]
WINDOW = 256          # detector window: 2.56 s
SEQUENCE = 512        # corrector sequence: 5.12 s

# How many detector windows to take from each kind of library segment (each is 1024 long).
WINDOWS_PER_MARKED = 4        # all four non-overlapping windows of every tremor-marked segment
WINDOWS_PER_HEALTHY = 2
WINDOWS_PER_UNMARKED = 1      # patients' segments without tremor (there are many)
SYNTHETIC_ONLY_SHARE = 0.2    # extra windows with no tremor at all, as a share of the rest

# Corrector: chance that a library segment is used for one sequence.
USE_FOR_CORRECTOR = {"marked": 1.0, "unmarked": 0.25, "healthy": 0.5}
NO_TREMOR_SEQ_SHARE = 0.2     # extra sequences with no tremor added


def make_split(lib):
    """Assign every person to train / val / test, separately within each diagnosis group."""
    people = {}
    for subject, dataset, condition in zip(lib["subject"], lib["dataset"], lib["condition"]):
        people[str(subject)] = str(dataset) + " / " + str(condition)
    rng = np.random.default_rng(SPLIT_SEED)
    split = {name: [] for name in SPLITS}
    for group in sorted(set(people.values())):
        members = sorted(s for s, g in people.items() if g == group)
        rng.shuffle(members)
        n_test = round(0.15 * len(members))
        n_val = round(0.15 * len(members))
        split["test"] += members[:n_test]
        split["val"] += members[n_test:n_test + n_val]
        split["train"] += members[n_test + n_val:]
    return {name: sorted(ids) for name, ids in split.items()}


def segment_kind(lib, i):
    """Which kind of library segment this is: marked / unmarked / healthy / skip."""
    healthy = lib["condition"][i] == "Healthy"
    if healthy:
        return "skip" if lib["tremor"][i] else "healthy"
    return "marked" if lib["tremor"][i] else "unmarked"


def rms_size(xy):
    """On-screen size of a tremor piece: RMS distance from its centre, in pixels."""
    xy = xy - xy.mean(axis=0)
    return float(np.sqrt((xy ** 2).sum(axis=1).mean()))


def describe(lib, i, tremor_piece):
    """Facts kept with every example (for the per-group results judges ask for)."""
    return dict(subject=str(lib["subject"][i]), dataset=str(lib["dataset"][i]),
                condition=str(lib["condition"][i]), age_band=str(lib["age_band"][i]),
                sex=str(lib["sex"][i]), task_type=str(lib["task_type"][i]),
                peak_hz=float(lib["peak_hz"][i]), strength_px=rms_size(tremor_piece))


NO_SOURCE = dict(subject="synthetic", dataset="none", condition="none", age_band="none",
                 sex="none", task_type="none", peak_hz=float("nan"), strength_px=0.0)


def build_detector(lib, members, rng, scale, events=EVENTS):
    """Detector windows for one split."""
    inputs, tremors, facts = [], [], []

    def add(tremor_piece, label, source, info):
        clean, kind = generate_path(rng, WINDOW, events=events)
        moving = bool(window_is_moving(clean[None])[0])
        inputs.append(clean + tremor_piece)
        tremors.append(tremor_piece)
        facts.append(dict(info, label=label, source=source, moving=moving,
                          lookalike_share=float(np.isin(kind, LOOKALIKES).mean())))

    for i in np.flatnonzero(np.isin(lib["subject"], members)):
        kind = segment_kind(lib, i)
        if kind == "skip":
            continue
        if kind == "marked":
            starts = [0, 256, 512, 768]
        else:
            n = WINDOWS_PER_HEALTHY if kind == "healthy" else WINDOWS_PER_UNMARKED
            starts = rng.choice(1024 - WINDOW + 1, n, replace=False)
        for start in starts:
            piece = lib["xy"][i, start:start + WINDOW] * scale
            label = 1 if kind == "marked" else 0
            source = {"marked": "tremor", "unmarked": "patient, no tremor", "healthy": "healthy"}[kind]
            add(piece, label, source, describe(lib, i, piece))

    for _ in range(round(SYNTHETIC_ONLY_SHARE * len(inputs))):
        add(np.zeros((WINDOW, 2), np.float32), 0, "synthetic only", NO_SOURCE)
    return np.array(inputs, np.float32), np.array(tremors, np.float32), facts


def build_corrector(lib, members, rng, scale):
    """Corrector sequences (shaky input, clean target) for one split."""
    shaky, clean_all, facts = [], [], []
    for i in np.flatnonzero(np.isin(lib["subject"], members)):
        kind = segment_kind(lib, i)
        if kind == "skip" or rng.random() >= USE_FOR_CORRECTOR[kind]:
            continue
        start = rng.integers(0, 1024 - SEQUENCE + 1)
        piece = lib["xy"][i, start:start + SEQUENCE] * scale
        clean, _ = generate_path(rng, SEQUENCE)
        shaky.append(clean + piece)
        clean_all.append(clean)
        facts.append(dict(describe(lib, i, piece), tremor=bool(kind == "marked")))
    for _ in range(round(NO_TREMOR_SEQ_SHARE * len(shaky))):
        clean, _ = generate_path(rng, SEQUENCE)
        shaky.append(clean.copy())
        clean_all.append(clean)
        facts.append(dict(NO_SOURCE, tremor=False))
    return np.array(shaky, np.float32), np.array(clean_all, np.float32), facts


def save(path, arrays, facts):
    columns = {k: np.array([f[k] for f in facts]) for k in facts[0]}
    np.savez_compressed(path, **arrays, **columns)


def print_tables(split, lib, detector, corrector):
    people_info = {}
    for i in range(len(lib["subject"])):
        people_info[str(lib["subject"][i])] = (str(lib["condition"][i]), str(lib["age_band"][i]),
                                               str(lib["sex"][i]), str(lib["dataset"][i]))

    print("\nPeople per split:")
    for name in SPLITS:
        print("  %-5s %3d people" % (name, len(split[name])))

    print("\nDetector windows (2.56 s) per split:")
    print("  %-5s %7s %9s %9s" % ("split", "total", "tremor", "no tremor"))
    for name in SPLITS:
        labels = np.array([f["label"] for f in detector[name]])
        print("  %-5s %7d %9d %9d" % (name, len(labels), labels.sum(), (labels == 0).sum()))

    print("\nDetector windows by source (train / val / test):")
    for source in ["tremor", "patient, no tremor", "healthy", "synthetic only"]:
        counts = [sum(f["source"] == source for f in detector[n]) for n in SPLITS]
        print("  %-20s %s" % (source, " / ".join(str(c) for c in counts)))

    print("\nDetector tremor windows by diagnosis (train / val / test):")
    conditions = sorted({f["condition"] for n in SPLITS for f in detector[n] if f["label"] == 1})
    for c in conditions:
        counts = [sum(f["label"] == 1 and f["condition"] == c for f in detector[n]) for n in SPLITS]
        print("  %-26s %s" % (c, " / ".join(str(x) for x in counts)))

    print("\nDetector windows where the hand is mostly moving (train / val / test): %s" %
          " / ".join(str(sum(f["moving"] for f in detector[n])) for n in SPLITS))

    print("\nCorrector sequences (5.12 s) per split, with tremor / without:")
    for name in SPLITS:
        flags = [f["tremor"] for f in corrector[name]]
        print("  %-5s %6d  (%d / %d)" % (name, len(flags), sum(flags), len(flags) - sum(flags)))

    print("\nTEST people by group (results for groups under about 10 people are unreliable):")
    for title, index in [("diagnosis", 0), ("age band", 1), ("sex", 2), ("dataset", 3)]:
        counts = Counter(people_info[s][index] for s in split["test"])
        text = ", ".join("%s %d%s" % (k, v, " (<10!)" if v < 10 else "") for k, v in sorted(counts.items()))
        print("  by %-9s %s" % (title + ":", text))


def build_continuous():
    """Step 12: detector windows with pause-free synthetic movement (glides, reaches, drifts),
    from the SAME people in the same splits, with new random seeds. Saved as
    detector_<split>_continuous.npz. Used to train detector v2 and to test whether a detector
    wrongly treats uninterrupted movement as tremor."""
    lib = dict(np.load(LIBRARY))
    with open(SPLIT_FILE, encoding="utf-8") as f:
        split = json.load(f)
    for seed, name in enumerate(SPLITS, start=11):
        rng = np.random.default_rng(seed)
        x, tremor, facts = build_detector(lib, split[name], rng, 1.0, events=CONTINUOUS_EVENTS)
        save(OUT_DIR / f"detector_{name}_continuous.npz", dict(xy=x, tremor_xy=tremor), facts)
        labels = np.array([f["label"] for f in facts])
        print("  %-5s %6d continuous windows (%d tremor)" % (name, len(labels), labels.sum()))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tremor-scale", type=float, default=1.0,
                        help="multiply every tremor by this (0.5 / 2 for the DECISION 1 check)")
    parser.add_argument("--continuous", action="store_true",
                        help="step 12: extra detector windows whose movement never pauses")
    args = parser.parse_args()
    if args.continuous:
        build_continuous()
        return

    lib = dict(np.load(LIBRARY))
    split = make_split(lib)
    if args.tremor_scale != 1.0:
        # The half/double sets must use exactly the saved split, never a recomputed one.
        with open(SPLIT_FILE, encoding="utf-8") as f:
            split = json.load(f)
    else:
        with open(SPLIT_FILE, "w", encoding="utf-8") as f:
            json.dump(split, f, indent=1)
        print("Saved", SPLIT_FILE.relative_to(ROOT))

    suffix = "" if args.tremor_scale == 1.0 else "_x%g" % args.tremor_scale
    detector, corrector = {}, {}
    for seed, name in enumerate(SPLITS, start=1):
        rng = np.random.default_rng(seed)       # a different, fixed stream for each split
        x, tremor, facts = build_detector(lib, split[name], rng, args.tremor_scale)
        save(OUT_DIR / f"detector_{name}{suffix}.npz", dict(xy=x, tremor_xy=tremor), facts)
        detector[name] = facts
        shaky, clean, cfacts = build_corrector(lib, split[name], rng, args.tremor_scale)
        save(OUT_DIR / f"corrector_{name}{suffix}.npz", dict(shaky=shaky, clean=clean), cfacts)
        corrector[name] = cfacts
    print("Saved detector_*%s.npz and corrector_*%s.npz to data/derived/" % (suffix, suffix))
    print_tables(split, lib, detector, corrector)


if __name__ == "__main__":
    main()
