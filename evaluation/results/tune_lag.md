# Less lag: tuning the app's smoothing (validation first)

Produced by `python evaluation/tune_lag.py --test`. The app's network with gated One Euro smoothing, demo page code, browser-like timing; averages over mild/medium/strong replayed tremor x reaching/gliding/still (lag: reaching and gliding only).

## Validation people

| Smoothing settings | Lag while moving (ms) | Distance | Shake | Jerk |
|---|---|---|---|---|
| min_cutoff 1, beta 0.004 (now) | 67 | 5.29 | 2.98 | 0.21 |
| min_cutoff 1, beta 0.01 | 52 | 4.37 | 3.18 | 0.25 |
| min_cutoff 1, beta 0.02 | 42 | 3.96 | 3.39 | 0.28 |
| min_cutoff 1, beta 0.05 | 33 | 3.70 | 3.68 | 0.35 |
| min_cutoff 2, beta 0.004 | 55 | 4.89 | 3.14 | 0.24 |
| min_cutoff 2, beta 0.01 | 47 | 4.25 | 3.31 | 0.27 |
| min_cutoff 2, beta 0.02 | 40 | 3.93 | 3.48 | 0.30 |
| min_cutoff 2, beta 0.05 | 32 | 3.71 | 3.74 | 0.35 |
| min_cutoff 4, beta 0.004 | 45 | 4.52 | 3.41 | 0.30 |
| min_cutoff 4, beta 0.01 | 38 | 4.13 | 3.53 | 0.32 |
| min_cutoff 4, beta 0.02 | 35 | 3.91 | 3.65 | 0.34 |
| min_cutoff 4, beta 0.05 | 27 | 3.74 | 3.83 | 0.38 |

Rule fixed in advance: shake and jerk each at most 5% above now; then the lowest lag.

**Chosen: min_cutoff 1, beta 0.004 (now).**

This project is a prototype and is not medical advice.
