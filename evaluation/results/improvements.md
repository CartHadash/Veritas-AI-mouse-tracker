# Step 12: one measured improvement to each model

Produced by `python evaluation/improvements.py --test`. Settings and the keep/drop choice use validation people only.

## Detector: v1 vs v2 (v2 also learned from pause-free movement)

Cut-off for both: at most 20% missed on the normal validation windows.

| Version | Data | Average precision | Missed cases | False alarms |
|---|---|---|---|---|
| v1 | validation, normal | 0.676 | 19.8% | 27.8% |
| v1 | validation, pause-free | 0.699 | 13.5% | 43.6% |
| v2 | validation, normal | 0.684 | 20.0% | 27.3% |
| v2 | validation, pause-free | 0.768 | 19.5% | 19.8% |

## Corrector: v1 vs v2 (v2 trained on tremor 0.5x-2x as large)

Average distance to the intended path on validation sequences, corrector always on (no detector gate, to isolate the change), after the first 2.56 s.

| Version | Tremor x0.5 | Tremor x1 | Tremor x2 | Tremor removed x0.5 / x1 / x2 |
|---|---|---|---|---|
| v1 | 2.21 px | 3.05 px | 4.55 px | 80% / 90% / 94% |
| v2 | 2.32 px | 3.11 px | 4.54 px | 81% / 91% / 95% |

## Corrector: v1 vs v3 (plain-distance training), validation, gated by detector v2

| Version | Sequences | Off the path moving / still (px) | Tremor removed | Lag (ms) |
|---|---|---|---|---|
| v1 | all with marked tremor (165) | 7.04 / 6.22 | 84% | 0 |
| v1 | mild (under 3 px) (50) | 1.99 / 1.05 | -53% | 0 |
| v1 | medium (3-10 px) (57) | 3.84 / 2.99 | 34% | 0 |
| v1 | strong (over 10 px) (58) | 14.86 / 13.27 | 85% | 10 |
| v1 | without marked tremor (644) | 1.85 overall | | |
| v3 | all with marked tremor (165) | 6.70 / 5.23 | 87% | 0 |
| v3 | mild (under 3 px) (50) | 1.53 / 0.86 | 11% | 0 |
| v3 | medium (3-10 px) (57) | 3.87 / 2.54 | 34% | 0 |
| v3 | strong (over 10 px) (58) | 14.24 / 11.15 | 87% | 10 |
| v3 | without marked tremor (644) | 1.68 overall | | |

No filter on the sequences without marked tremor: 1.96 px.

## Corrector: v1 vs v3 (plain-distance training), TEST (scored once), gated by detector v2

| Version | Sequences | Off the path moving / still (px) | Tremor removed | Lag (ms) |
|---|---|---|---|---|
| v1 | all with marked tremor (236) | 7.15 / 5.93 | 84% | 0 |
| v1 | mild (under 3 px) (47) | 1.73 / 1.16 | 3% | 0 |
| v1 | medium (3-10 px) (88) | 3.83 / 3.16 | 48% | 0 |
| v1 | strong (over 10 px) (101) | 12.37 / 10.89 | 85% | 0 |
| v1 | without marked tremor (694) | 2.00 overall | | |
| v3 | all with marked tremor (236) | 6.85 / 4.93 | 86% | 0 |
| v3 | mild (under 3 px) (47) | 1.58 / 0.98 | 8% | 0 |
| v3 | medium (3-10 px) (88) | 3.86 / 2.53 | 50% | 0 |
| v3 | strong (over 10 px) (101) | 11.71 / 9.13 | 87% | 0 |
| v3 | without marked tremor (694) | 1.82 overall | | |

No filter on the sequences without marked tremor: 2.30 px.

## Kept versions on TEST people (scored once)

| Detector | Data | Missed cases | False alarms |
|---|---|---|---|
| v1 | test, normal | 14.3% | 27.0% |
| v1 | test, pause-free | 8.1% | 45.3% |
| v2 | test, normal | 12.9% | 27.1% |
| v2 | test, pause-free | 11.2% | 20.4% |

This project is a prototype and is not medical advice.
