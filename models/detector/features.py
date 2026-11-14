"""
features.py - turn a 2.56 s window of cursor positions into about 20 numbers ("features")
that describe it. The detector model (train.py) decides "tremor or not" from these numbers.

Each feature is something a person could explain:
  - how much of the movement happens at each speed of repetition (frequency bands);
  - where the strongest rhythm between 3 and 12 Hz is, and how sharp and regular it is;
  - how large the 3-12 Hz shake is, in pixels;
  - how fast the cursor travels, and how jerky it is;
  - how often it reverses direction.

Works on many windows at once: windows has shape (n, 256, 2) in pixels, 100 samples per
second. Only uses the window itself (the last 2.56 s), so it can run live.
"""

import numpy as np
from scipy.signal import butter, filtfilt, periodogram

RATE = 100
BANDS = [(0.5, 3), (3, 5), (5, 7), (7, 9), (9, 12), (12, 20), (20, 50)]

FEATURE_NAMES = (
    ["power %g-%g Hz (log)" % b for b in BANDS] +
    ["share of power in 3-12 Hz", "peak frequency in 3-12 Hz", "peak sharpness",
     "peak height vs typical (log)", "shake size 3-12 Hz (px, log)", "rhythm regularity",
     "mean speed (log)", "median speed (log)", "max speed (log)",
     "acceleration size (log)", "direction reversals per second", "share of time nearly still"]
)

_BAND_B, _BAND_A = butter(4, [3, 12], btype="bandpass", fs=RATE)


def compute_features(windows):
    """windows: (n, samples, 2) positions in px. Returns (n, len(FEATURE_NAMES)) float32."""
    windows = np.asarray(windows, dtype=np.float64)
    n = len(windows)
    velocity = np.diff(windows, axis=1) * RATE                    # px per second
    speed = np.linalg.norm(velocity, axis=2)

    # Spectrum of the velocity (x and y added): how much movement at each frequency.
    freqs, power = periodogram(velocity, fs=RATE, axis=1, detrend="constant")
    power = power.sum(axis=2) + 1e-9
    total = power[:, freqs >= 0.5].sum(axis=1)
    band_power = [power[:, (freqs >= lo) & (freqs < hi)].sum(axis=1) for lo, hi in BANDS]

    tremor_band = (freqs >= 3) & (freqs <= 12)
    band = power[:, tremor_band]
    band_freqs = freqs[tremor_band]
    peak_index = band.argmax(axis=1)
    peak_freq = band_freqs[peak_index]
    near_peak = np.abs(band_freqs[None, :] - peak_freq[:, None]) <= 1.0
    sharpness = (band * near_peak).sum(axis=1) / band.sum(axis=1)
    peak_height = band.max(axis=1) / np.median(power[:, (freqs >= 1) & (freqs <= 25)], axis=1)

    # The 3-12 Hz part of the position itself: its size in px, and how regular it is
    # (correlation of the shake with itself one rhythm-period later; 1 = perfectly regular).
    shake = filtfilt(_BAND_B, _BAND_A, windows, axis=1)
    shake_size = np.sqrt((shake ** 2).sum(axis=2).mean(axis=1))
    regularity = np.zeros(n)
    for i in range(n):
        lag = int(round(RATE / peak_freq[i]))
        a, b = shake[i, :-lag].ravel(), shake[i, lag:].ravel()
        denom = np.sqrt((a ** 2).sum() * (b ** 2).sum())
        regularity[i] = (a * b).sum() / denom if denom > 0 else 0.0

    acceleration = np.diff(velocity, axis=1) * RATE
    accel_size = np.sqrt((acceleration ** 2).sum(axis=2).mean(axis=1))

    # Direction reversals: how often x or y velocity changes sign. Speeds under 30 px/s are
    # ignored, because sensor jitter alone reaches about that when measured sample to sample.
    moving_x = np.where(np.abs(velocity[..., 0]) > 30, np.sign(velocity[..., 0]), 0)
    moving_y = np.where(np.abs(velocity[..., 1]) > 30, np.sign(velocity[..., 1]), 0)
    reversals = np.zeros(n)
    for axis in (moving_x, moving_y):
        for i in range(n):
            signs = axis[i][axis[i] != 0]
            reversals[i] += (np.diff(signs) != 0).sum()
    reversals /= windows.shape[1] / RATE

    # Nearly still: moved less than 1 px in 50 ms (i.e. slower than 20 px/s), which is
    # measured over 5 samples so jitter does not count as movement.
    still = np.linalg.norm(windows[:, 5:] - windows[:, :-5], axis=2) < 1.0

    log = lambda x: np.log10(x + 1e-6)
    columns = [log(b) for b in band_power] + [
        sum(band_power[1:5]) / total, peak_freq, sharpness, log(peak_height),
        log(shake_size), regularity, log(speed.mean(axis=1)), log(np.median(speed, axis=1)),
        log(speed.max(axis=1)), log(accel_size), reversals, still.mean(axis=1)]
    return np.stack(columns, axis=1).astype(np.float32)
