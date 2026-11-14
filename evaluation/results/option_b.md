# Option B: a corrector retrained to aim at what the eye sees

Produced by `python evaluation/option_b.py --test`. Averages over mild/medium/strong replayed tremor x reaching/gliding/still, demo page code, browser-like timing (as `vs_one_euro.py`). Candidates trained with `models/corrector/train.py --loss distance --smooth 2 --shake K` (v5_kK).

## Validation people

| Network (with the app's gated One Euro smoothing) | Distance | Shake | Jerk |
|---|---|---|---|
| v4_s2 (option A, the app) | 5.17 | 3.08 | 0.22 |
| v5_k1 | 5.25 | 3.04 | 0.22 |
| v5_k3 | 5.29 | 2.98 | 0.21 |

Rule fixed before training: replace option A only if shake and jerk are both lower and distance at most 5% higher; then the lowest shake.

**Result: v5_k3 qualifies and wins.**

## Test people (scored once)

| Network (with the app's gated One Euro smoothing) | Distance | Shake | Jerk |
|---|---|---|---|
| v4_s2 (option A, the app) | 4.98 | 2.64 | 0.25 |
| v5_k3 | 5.22 | 2.56 | 0.24 |

This project is a prototype and is not medical advice.
