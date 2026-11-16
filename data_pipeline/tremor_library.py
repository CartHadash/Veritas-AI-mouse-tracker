"""
tremor_library.py - build one tidy file of real tremor segments, in screen pixels.

For every recording in both datasets we:
  1. cut it into segments of 10.24 s (1024 samples at 100 per second);
  2. decide, with a FIXED RULE, whether the segment "contains tremor" (see below);
  3. keep only the shaking part (3-12 Hz band-pass filter), turned into a 2-D on-screen
     movement (x, y) in pixels, using ONE conversion factor per dataset.

Output: data/derived/tremor_library.npz (not in git) and a chart of 8 example segments in
evaluation/results/figures/tremor_library_examples.png.

Run from the repository folder:
    python data_pipeline/tremor_library.py

THE TREMOR-MARKING RULE (fixed before any model was trained; never change it
after seeing model results). It is measured on the ORIGINAL recording segment (not filtered):
  - "band strength" = how much movement there is between 3 and 12 Hz (from the spectrum);
  - "rhythm" = share of that 3-12 Hz movement lying within +-1 Hz of its strongest frequency.
  PADS segment is marked "tremor" when BOTH:
    a) its band strength is above the 95th percentile of HEALTHY controls doing the same
       type of task (rest / postural / action), i.e. stronger than 95% of healthy people;
    b) rhythm >= 0.5 (most of the shaking is one steady beat, not spread-out movement).
  TremorDB has no healthy people to compare with, so (a) becomes: at least half of all the
  movement (above 0.5 Hz) lies in 3-12 Hz. (b) is the same. These are rest recordings, so
  there is no deliberate movement to confuse the check.

THE PIXEL FACTOR: one number per dataset, chosen so that the median
tremor-marked Parkinson's segment has an on-screen size ("strength") of 6 px, where
strength = root-mean-square distance of the cursor from its centre. TremorDB's factor is
chosen so its median tremor-marked segment is also 6 px. Results are later re-checked at half
and double this factor.

TASK TYPES: all PADS tasks, labelled rest / postural / action.
"""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt, welch

ROOT = Path(__file__).resolve().parents[1]
PADS = ROOT / "data" / "pads"
TREMORDB = ROOT / "data" / "tremordb" / "effect-of-deep-brain-stimulation-on-parkinsonian-tremor-1.0.0"
OUT_FILE = ROOT / "data" / "derived" / "tremor_library.npz"
FIGURES = ROOT / "evaluation" / "results" / "figures"

RATE = 100            # samples per second (both datasets)
SEG = 1024            # samples per segment = 10.24 seconds
TARGET_PX = 6.0       # median tremor-marked segment size in pixels
TASK_TYPE = {
    "Relaxed": "rest", "RelaxedTask": "rest",
    "StretchHold": "postural", "LiftHold": "postural", "HoldWeight": "postural", "Entrainment": "postural",
    "PointFinger": "action", "DrinkGlas": "action", "TouchNose": "action", "TouchIndex": "action",
    "CrossArms": "action",
}

# One band-pass filter for 3-12 Hz. filtfilt runs it forwards and backwards, which is fine
# here because this is offline preparation (the live models must not do this).
BAND_B, BAND_A = butter(4, [3, 12], btype="bandpass", fs=RATE)


def age_band(age):
    if age < 60:
        return "under 60"
    if age < 70:
        return "60-69"
    return "70 and over"


def spectrum_measures(signals):
    """signals: (samples, axes). Returns (band strength, rhythm, share in band, peak Hz)."""
    freqs, power = welch(signals, fs=RATE, nperseg=256, axis=0)
    power = power.sum(axis=1)                      # add up the axes
    step = freqs[1] - freqs[0]
    band = (freqs >= 3) & (freqs <= 12)
    band_power = power[band].sum()
    strength = np.sqrt(band_power * step)          # root of the power = a size, in sensor units
    peak = freqs[band][np.argmax(power[band])]
    near_peak = band & (np.abs(freqs - peak) <= 1.0)
    rhythm = power[near_peak].sum() / band_power
    share = band_power / power[freqs >= 0.5].sum()
    return strength, rhythm, share, peak


def to_position_band(signal):
    """Velocity -> position (add up over time), then keep only 3-12 Hz. Works per column."""
    position = np.cumsum(signal, axis=0) / RATE
    return filtfilt(BAND_B, BAND_A, position, axis=0)


def strength_of(xy):
    """On-screen size of a segment: RMS distance from its centre (same units as xy)."""
    xy = xy - xy.mean(axis=0)
    return float(np.sqrt((xy ** 2).sum(axis=1).mean()))


def main_two_directions(xyz):
    """Turn 3-D wrist rotation into 2-D: the two directions it moves most in (PCA)."""
    centred = xyz - xyz.mean(axis=0)
    _, _, directions = np.linalg.svd(centred, full_matrices=False)
    return centred @ directions[:2].T


def load_pads():
    """One row per 1024-sample segment of every PADS recording."""
    rows = []
    for path in sorted((PADS / "patients").glob("patient_*.json")):
        with open(path, encoding="utf-8") as f:
            person = json.load(f)
        sid = person["id"]
        for task, ttype in TASK_TYPE.items():
            for wrist in ("LeftWrist", "RightWrist"):
                file = PADS / "movement" / "timeseries" / f"{sid}_{task}_{wrist}.txt"
                gyro = np.loadtxt(file, delimiter=",")[:, 4:7]   # rotation speed, rad/s
                shake = to_position_band(gyro)                   # wrist angle, 3-12 Hz only
                for start in range(0, len(gyro) - SEG + 1, SEG):
                    raw = gyro[start:start + SEG]
                    strength, rhythm, share, peak = spectrum_measures(raw - raw.mean(axis=0))
                    rows.append(dict(
                        dataset="PADS", subject="pads_" + sid, condition=person["condition"],
                        age=person["age"], sex=person["gender"], task=task, task_type=ttype,
                        side=wrist, band_strength=strength, rhythm=rhythm, share=share,
                        peak_hz=peak, xy=main_two_directions(shake[start:start + SEG])))
    return rows


def tremordb_people():
    """Read age and sex of the 16 TremorDB subjects from subject_description.txt."""
    people, names = {}, None
    with open(TREMORDB / "subject_description.txt", encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if line.startswith("SUBJECT"):
                names = parts[1:]
            elif line.startswith("AGE") and names:
                ages = [int(a) for a in parts[2:]]
            elif line.startswith("GENDER") and names:
                for name, age, sex in zip(names, ages, parts[1:]):
                    people[name] = dict(age=age, sex="male" if sex == "M" else "female")
    return people


def load_tremordb():
    people = tremordb_people()
    rows = []
    for file in sorted(TREMORDB.glob("r*/*")):
        if file.suffix not in (".let", ".rit"):
            continue
        name = file.stem                     # e.g. s6rof
        subject = name[:name.index("r", 1)]  # e.g. s6 (the part before the condition)
        velocity = np.loadtxt(file)
        shake = to_position_band(velocity)
        # One axis only: pair it with itself 3 seconds later to make a second axis.
        shifted = np.roll(shake, 3 * RATE)
        for start in range(0, len(velocity) - SEG + 1, SEG):
            raw = velocity[start:start + SEG, None]
            strength, rhythm, share, peak = spectrum_measures(raw - raw.mean())
            xy = np.stack([shake[start:start + SEG], shifted[start:start + SEG]], axis=1)
            rows.append(dict(
                dataset="TremorDB", subject="tdb_" + subject, condition="Parkinson's",
                age=people[subject]["age"], sex=people[subject]["sex"],
                task=file.parent.name + "/" + file.name, task_type="rest",
                side="left finger" if file.suffix == ".let" else "right finger",
                band_strength=strength, rhythm=rhythm, share=share, peak_hz=peak, xy=xy))
    return rows


def mark_tremor(rows):
    """Apply the fixed rule (see the top of this file). Returns the healthy thresholds used."""
    thresholds = {}
    for ttype in ("rest", "postural", "action"):
        healthy = [r["band_strength"] for r in rows
                   if r["dataset"] == "PADS" and r["condition"] == "Healthy" and r["task_type"] == ttype]
        thresholds[ttype] = float(np.percentile(healthy, 95))
    for r in rows:
        if r["dataset"] == "PADS":
            strong = r["band_strength"] > thresholds[r["task_type"]]
        else:
            strong = r["share"] >= 0.5
        r["tremor"] = bool(strong and r["rhythm"] >= 0.5)
    return thresholds


def apply_pixel_factor(rows):
    """One factor per dataset so the median tremor-marked segment is 6 px."""
    factors = {}
    for dataset, reference in [("PADS", "Parkinson's"), ("TremorDB", "Parkinson's")]:
        sizes = [strength_of(r["xy"]) for r in rows
                 if r["dataset"] == dataset and r["condition"] == reference and r["tremor"]]
        factors[dataset] = TARGET_PX / float(np.median(sizes))
    for r in rows:
        r["xy"] = (r["xy"] * factors[r["dataset"]]).astype(np.float32)
        r["strength_px"] = strength_of(r["xy"])
    return factors


def print_counts(rows):
    print("\nTremor-marked segments by dataset and diagnosis:")
    print("  %-10s %-26s %9s %9s %9s %9s" % ("dataset", "diagnosis", "segments", "marked", "subjects", "marked s"))
    keys = sorted({(r["dataset"], r["condition"]) for r in rows})
    for dataset, condition in keys:
        group = [r for r in rows if r["dataset"] == dataset and r["condition"] == condition]
        marked = [r for r in group if r["tremor"]]
        print("  %-10s %-26s %9d %9d %9d %9.0f" % (
            dataset, condition, len(group), len(marked), len({r["subject"] for r in marked}),
            len(marked) * SEG / RATE))
    print("  (marked = tremor-marked segments; subjects = people with at least one;"
          " marked s = seconds of tremor-marked recording)")

    print("\nTremor-marked PADS segments by task type:")
    for ttype in ("rest", "postural", "action"):
        group = [r for r in rows if r["dataset"] == "PADS" and r["task_type"] == ttype]
        print("  %-9s %5d of %5d" % (ttype, sum(r["tremor"] for r in group), len(group)))

    marked_px = [r["strength_px"] for r in rows if r["tremor"]]
    healthy_px = [r["strength_px"] for r in rows if r["condition"] == "Healthy"]
    print("\nOn-screen size (px), tremor-marked segments: median %.1f, 10th-90th percentile %.1f-%.1f"
          % (np.median(marked_px), np.percentile(marked_px, 10), np.percentile(marked_px, 90)))
    print("On-screen size (px), healthy controls (all):  median %.1f, 10th-90th percentile %.1f-%.1f"
          % (np.median(healthy_px), np.percentile(healthy_px, 10), np.percentile(healthy_px, 90)))


def plot_examples(rows):
    """8 example segments: 4 tremor-marked patients, 4 healthy controls (same y scale)."""
    rng = np.random.default_rng(0)
    marked = [r for r in rows if r["tremor"] and r["condition"] != "Healthy"]
    healthy = [r for r in rows if r["condition"] == "Healthy" and r["task_type"] == "rest"]
    picks = [marked[i] for i in rng.choice(len(marked), 4, replace=False)] + \
            [healthy[i] for i in rng.choice(len(healthy), 4, replace=False)]
    limit = max(np.abs(r["xy"][:300, 0]).max() for r in picks) * 1.1

    fig, axes = plt.subplots(8, 2, figsize=(11, 16), gridspec_kw={"width_ratios": [2, 1]})
    t = np.arange(300) / RATE
    for row, r in zip(axes, picks):
        row[0].plot(t, r["xy"][:300, 0], label="x")
        row[0].plot(t, r["xy"][:300, 1], label="y", alpha=0.7)
        row[0].set_ylim(-limit, limit)
        row[0].set_ylabel("px")
        row[0].set_title("%s %s, %s (%s), %s, size %.1f px" % (
            r["subject"], r["condition"], r["task"], r["task_type"],
            "TREMOR-MARKED" if r["tremor"] else "not marked", r["strength_px"]), fontsize=9)
        freqs, power = welch(r["xy"], fs=RATE, nperseg=256, axis=0)
        row[1].plot(freqs, power.sum(axis=1))
        row[1].set_xlim(0, 20)
        row[1].set_title("spectrum, peak %.1f Hz" % r["peak_hz"], fontsize=9)
    axes[0][0].legend(loc="upper right")
    axes[-1][0].set_xlabel("time (s), first 3 s of the segment")
    axes[-1][1].set_xlabel("frequency (Hz)")
    fig.tight_layout()
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / "tremor_library_examples.png", dpi=90)
    plt.close(fig)


def save(rows, thresholds, factors):
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    columns = ["dataset", "subject", "condition", "sex", "task", "task_type", "side"]
    np.savez_compressed(
        OUT_FILE,
        xy=np.stack([r["xy"] for r in rows]),                       # (segments, 1024, 2) px
        tremor=np.array([r["tremor"] for r in rows]),
        strength_px=np.array([r["strength_px"] for r in rows], dtype=np.float32),
        peak_hz=np.array([r["peak_hz"] for r in rows], dtype=np.float32),
        rhythm=np.array([r["rhythm"] for r in rows], dtype=np.float32),
        age=np.array([r["age"] for r in rows]),
        age_band=np.array([age_band(r["age"]) for r in rows]),
        pixel_factor_pads=factors["PADS"], pixel_factor_tremordb=factors["TremorDB"],
        **{c: np.array([r[c] for r in rows]) for c in columns},
        **{"healthy_threshold_" + k: v for k, v in thresholds.items()},
    )
    print("\nSaved %d segments -> %s (%.0f MB)" % (len(rows), OUT_FILE.relative_to(ROOT),
                                                   OUT_FILE.stat().st_size / 1e6))


def main():
    print("Reading PADS (10,318 files, about a minute)...")
    rows = load_pads()
    print("Reading TremorDB...")
    rows += load_tremordb()
    print("Segments:", len(rows))

    thresholds = mark_tremor(rows)
    print("Healthy 95th-percentile band strength (rad/s):",
          ", ".join("%s %.3f" % kv for kv in thresholds.items()))
    factors = apply_pixel_factor(rows)
    print("Pixel factor: PADS %.1f px per radian; TremorDB %.1f px per unit" % (factors["PADS"], factors["TremorDB"]))

    print_counts(rows)
    plot_examples(rows)
    save(rows, thresholds, factors)


if __name__ == "__main__":
    main()
