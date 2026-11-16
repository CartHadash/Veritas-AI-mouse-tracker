"""
look_at_data.py - look at the data with our own eyes before training anything.

It does two things:
  1. Counts the PADS subjects by diagnosis, age band and sex (to check the download is
     complete, and to know how many people each group has).
  2. Plots two known tremor recordings - PADS subject 060 (right wrist, "Relaxed") and
     TremorDB rofh/s6rof.let - as a signal over time, a 3-second zoom, and a frequency
     spectrum. A tremor shows up as a tall narrow peak between 3 and 12 Hz.

Run from the repository folder:
    python data_pipeline/look_at_data.py
Charts are saved to evaluation/results/figures/.
"""

import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # draw straight to files; no window needed
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import welch

ROOT = Path(__file__).resolve().parents[1]  # the repository folder
PADS = ROOT / "data" / "pads"
TREMORDB = ROOT / "data" / "tremordb" / "effect-of-deep-brain-stimulation-on-parkinsonian-tremor-1.0.0"
FIGURES = ROOT / "evaluation" / "results" / "figures"
RATE = 100  # both datasets are sampled 100 times per second


def age_band(age):
    if age < 60:
        return "under 60"
    if age < 70:
        return "60-69"
    return "70 and over"


def count_pads_subjects():
    """Read every patient file and print counts per diagnosis, age band and sex."""
    patients = []
    for path in sorted((PADS / "patients").glob("patient_*.json")):
        with open(path, encoding="utf-8") as f:
            patients.append(json.load(f))

    print("PADS subjects:", len(patients))
    for title, key in [("diagnosis", lambda p: p["condition"]),
                       ("age band", lambda p: age_band(p["age"])),
                       ("sex", lambda p: p["gender"])]:
        print("\nBy " + title + ":")
        for value, n in Counter(key(p) for p in patients).most_common():
            print("  %-30s %d" % (value, n))
    return patients


def spectrum(signal):
    """Frequency spectrum with Welch's method: how much power is at each frequency."""
    freqs, power = welch(signal, fs=RATE, nperseg=512)
    return freqs, power


def describe_peak(freqs, power):
    """Return the peak frequency in 3-12 Hz and the share of power inside 3-12 Hz."""
    band = (freqs >= 3) & (freqs <= 12)
    peak = freqs[band][np.argmax(power[band])]
    share = power[band].sum() / power[freqs > 0.5].sum()  # ignore the slow drift below 0.5 Hz
    return peak, share


def plot_recording(signal, title, filename, signal_label):
    """Save one chart: whole signal, a 3-second zoom, and the spectrum."""
    t = np.arange(len(signal)) / RATE
    freqs, power = spectrum(signal)
    peak, share = describe_peak(freqs, power)

    fig, axes = plt.subplots(3, 1, figsize=(10, 9))
    axes[0].plot(t, signal, linewidth=0.7)
    axes[0].set(title=title + " - whole recording", xlabel="time (s)", ylabel=signal_label)

    zoom = t < 3
    axes[1].plot(t[zoom], signal[zoom], linewidth=1)
    axes[1].set(title="First 3 seconds", xlabel="time (s)", ylabel=signal_label)

    axes[2].semilogy(freqs, power)
    axes[2].axvspan(3, 12, color="orange", alpha=0.2, label="tremor band 3-12 Hz")
    axes[2].axvline(peak, color="red", linestyle="--", label="peak %.2f Hz" % peak)
    axes[2].set(title="Frequency spectrum (%.0f%% of power in 3-12 Hz)" % (100 * share),
                xlabel="frequency (Hz)", ylabel="power", xlim=(0, 25))
    axes[2].legend()

    fig.tight_layout()
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / filename, dpi=110)
    plt.close(fig)
    print("%s: %d samples (%.1f s), peak %.2f Hz, %.0f%% of power in 3-12 Hz -> %s"
          % (title, len(signal), len(signal) / RATE, peak, 100 * share, filename))


def main():
    count_pads_subjects()
    print()

    # PADS: 7 columns = time, accelerometer x/y/z, gyroscope x/y/z. We plot the gyroscope
    # (rotation speed), which gravity does not disturb.
    pads_file = PADS / "movement" / "timeseries" / "060_Relaxed_RightWrist.txt"
    gyro = np.loadtxt(pads_file, delimiter=",")[:, 4:7]
    gyro = gyro - gyro.mean(axis=0)  # remove the constant offset
    # For one combined line, use the axis with the most movement.
    main_axis = gyro[:, np.argmax(gyro.std(axis=0))]
    plot_recording(main_axis, "PADS subject 060, right wrist, Relaxed",
                   "pads_060_relaxed_right.png", "rotation speed (rad/s)")

    # TremorDB: one number per line = fingertip velocity (units unreliable).
    tremor_file = TREMORDB / "rofh" / "s6rof.let"
    velocity = np.loadtxt(tremor_file)
    velocity = velocity - velocity.mean()
    plot_recording(velocity, "TremorDB rofh/s6rof.let",
                   "tremordb_s6rof_let.png", "fingertip velocity (arbitrary units)")


if __name__ == "__main__":
    main()
