# Smoother corrector (v4): choosing the penalty S on validation

Produced by `python evaluation/smoothness.py --test`. Sequences with marked tremor: 165; sequences without marked tremor: 644. Scored after the first 2.56 s. Jerkiness = average size of the change in cursor velocity from one 10 ms sample to the next (px); the intended path itself has 0.64 px.

## Validation

| Method (gated by detector v2) | Off the path moving / still (px) | Tremor removed | Lag (ms) | Jerkiness (px) | No marked tremor: off the path / jerkiness (px) |
|---|---|---|---|---|---|
| No filter | 12.25 / 13.95 | 0% | 0 | 1.65 | 1.96 / 0.74 |
| One Euro (original) | 20.40 / 7.04 | 67% | 40 | 0.69 | 12.93 / 0.24 |
| v1 | 7.04 / 6.22 | 84% | 0 | 2.00 | 1.85 / 1.00 |
| v3 | 6.70 / 5.23 | 87% | 0 | 1.83 | 1.68 / 0.85 |
| v4, S=0.5 | 6.84 / 5.14 | 87% | 0 | 1.28 | 1.70 / 0.74 |
| v4, S=2 | 7.16 / 5.40 | 87% | 0 | 1.07 | 1.75 / 0.71 |
| v4, S=8 | 7.78 / 6.97 | 81% | 0 | 1.07 | 1.82 / 0.71 |

**Chosen: v4, S=0.5** - the smallest S whose jerkiness (1.28 px) is at most no filter's (1.65 px).

## Test (scored once, after choosing on validation)

Sequences with marked tremor: 236; without marked tremor: 694; intended path jerkiness 0.63 px.

| Method (gated by detector v2) | Off the path moving / still (px) | Tremor removed | Lag (ms) | Jerkiness (px) | No marked tremor: off the path / jerkiness (px) |
|---|---|---|---|---|---|
| No filter | 13.17 / 12.74 | 0% | 0 | 1.69 | 2.30 / 0.80 |
| One Euro (original) | 19.66 / 5.92 | 68% | 40 | 0.64 | 12.95 / 0.25 |
| v1 | 7.15 / 5.93 | 84% | 0 | 2.09 | 2.00 / 1.06 |
| v3 | 6.85 / 4.93 | 86% | 0 | 1.96 | 1.82 / 0.91 |
| v4, S=0.5 | 6.94 / 4.86 | 87% | 0 | 1.37 | 1.85 / 0.78 |
| v4, S=2 | 7.30 / 5.17 | 86% | 0 | 1.12 | 1.91 / 0.74 |
| v4, S=8 | 7.79 / 6.44 | 83% | 0 | 1.12 | 2.00 / 0.74 |

This project is a prototype and is not medical advice.
