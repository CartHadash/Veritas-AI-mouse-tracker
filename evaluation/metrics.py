"""
metrics.py - the scoring functions every baseline and model is measured with.

Using one shared file means the baselines and our models are scored in exactly the same way.

DETECTOR (says "tremor" or "no tremor" for a 2.56 s window):
  missed cases  = share of real tremor windows it called "no tremor"   (false negatives)
  false alarms  = share of no-tremor windows it called "tremor"         (false positives)
  accuracy      = share of all windows it got right
The Health brief requires missed cases and false alarms to be reported separately.

CORRECTOR (turns shaky cursor positions into steadier ones):
  distance while moving / still = average distance in px between the output and the
                                  intended (clean) path, split by whether the hand was moving
  tremor removed               = how much of the 3-12 Hz shake left in the output is gone,
                                  compared with no filter (100% = all of it)
  lag                          = how many milliseconds the output trails the intended path
  jerkiness                    = average size (px) of the change in cursor velocity from one
                                  sample to the next. A smooth cursor is near 0. Added after the
                                  team leader saw our corrector look jumpy although its distance
                                  score was good: distance alone hid that problem.
"""

import numpy as np
from scipy.signal import butter, filtfilt

RATE = 100
# Corrector scoring ignores the first 2.56 s of every sequence (the detector needs that much
# history before the gate can open), so every method is scored on the same samples.
CORRECTOR_SKIP = 256
# Tremor size classes used in every report (on-screen RMS size of the added tremor piece).
SIZE_CLASSES = [("mild (under 3 px)", 0, 3), ("medium (3-10 px)", 3, 10), ("strong (over 10 px)", 10, 1e9)]
MOVING_SPEED = 20.0      # px/s: above this (measured over 50 ms) the hand counts as moving


# ---------------------------------------------------------------- detector

def detector_scores(labels, predictions):
    """labels, predictions: arrays of 0/1. Returns a dict of the three scores and counts."""
    labels = np.asarray(labels).astype(bool)
    predictions = np.asarray(predictions).astype(bool)
    tremor, no_tremor = labels.sum(), (~labels).sum()
    missed = (labels & ~predictions).sum()
    alarms = (~labels & predictions).sum()
    return dict(
        missed=missed / tremor if tremor else float("nan"),
        false_alarms=alarms / no_tremor if no_tremor else float("nan"),
        accuracy=(predictions == labels).mean(),
        n_tremor=int(tremor), n_no_tremor=int(no_tremor))


def choose_threshold(scores, labels, max_missed=None):
    """
    Pick the cut-off on a score (higher = more tremor-like), using VALIDATION data only.
      max_missed=None : the cut-off with the best balance of missed cases and false alarms
      max_missed=0.10 : the cut-off with the fewest false alarms that keeps missed <= 10%
    """
    scores, labels = np.asarray(scores), np.asarray(labels).astype(bool)
    best, best_value = None, None
    for cut in np.unique(np.quantile(scores, np.linspace(0, 1, 501))):
        s = detector_scores(labels, scores >= cut)
        if max_missed is None:
            value = -(s["missed"] + s["false_alarms"])        # higher is better
        else:
            if s["missed"] > max_missed:
                continue
            value = -s["false_alarms"]
        if best_value is None or value > best_value:
            best, best_value = cut, value
    return float(best)


# ---------------------------------------------------------------- corrector

_BAND_B, _BAND_A = butter(4, [3, 12], btype="bandpass", fs=RATE)


def window_is_moving(clean):
    """clean: (windows, samples, 2) intended movement. True for a window when the hand is
    moving (faster than 20 px/s, as in moving_mask) for at least half of it. This is THE
    definition of "hand moving" for every table in the project."""
    return moving_mask(np.asarray(clean, dtype=np.float64)).mean(axis=1) >= 0.5


def moving_mask(clean):
    """clean: (sequences, samples, 2). True where the intended movement is faster than 20 px/s."""
    step = np.zeros(clean.shape[:2])
    step[:, 5:] = np.linalg.norm(clean[:, 5:] - clean[:, :-5], axis=2) * RATE / 5
    step[:, :5] = step[:, 5:6]
    return step > MOVING_SPEED


def band_power(signal):
    """Total 3-12 Hz power of (sequences, samples, 2). Used to measure the shake left over."""
    return float((filtfilt(_BAND_B, _BAND_A, signal, axis=1) ** 2).sum())


def estimate_lag_ms(output, clean, mask, max_shift=40):
    """
    Shift the intended path later by 0..400 ms and see which shift matches the output best
    (while moving). That shift is the lag. Returns milliseconds.
    """
    errors = []
    for k in range(max_shift + 1):
        later = clean[:, : clean.shape[1] - k]
        out = output[:, k:]
        m = mask[:, k:]
        errors.append(np.linalg.norm(out - later, axis=2)[m].mean())
    return 1000.0 * int(np.argmin(errors)) / RATE


def jerkiness(positions):
    """positions: (sequences, samples, 2) or (samples, 2). Mean |p[t] - 2 p[t-1] + p[t-2]| in px."""
    positions = np.asarray(positions)
    second = positions[..., 2:, :] - 2 * positions[..., 1:-1, :] + positions[..., :-2, :]
    return float(np.linalg.norm(second, axis=-1).mean())


def corrector_scores(output, clean, shaky, skip=50):
    """
    output, clean, shaky: (sequences, samples, 2) in px. The first `skip` samples (0.5 s) are
    ignored, so every filter has had time to warm up.
    """
    output, clean, shaky = output[:, skip:], clean[:, skip:], shaky[:, skip:]
    mask = moving_mask(clean)
    distance = np.linalg.norm(output - clean, axis=2)
    shake_before = band_power(shaky - clean)
    shake_after = band_power(output - clean)
    return dict(
        distance_moving=float(distance[mask].mean()),
        distance_still=float(distance[~mask].mean()),
        tremor_removed=1.0 - shake_after / shake_before if shake_before > 0 else float("nan"),
        lag_ms=estimate_lag_ms(output, clean, mask),
        jerkiness=jerkiness(output))


def run_filter(make, shaky):
    """Run a filter with reset()/update(x, y, t) over every sequence, sample by sample."""
    out = np.empty_like(shaky)
    for i, seq in enumerate(shaky):
        f = make()
        f.reset()
        for j, (x, y) in enumerate(seq):
            out[i, j] = f.update(float(x), float(y), j / RATE)
    return out
