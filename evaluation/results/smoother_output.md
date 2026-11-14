# A smoother corrected cursor: choosing on validation

Produced by `python evaluation/smoother_output.py --test`. Sequences with marked tremor, gated by detector v2 as in the app, scored after 2.56 s. Jerkiness = average size of the change in cursor velocity from one 10 ms sample to the next (px). Extra smoothing is applied only as much as the correction is on.

## Validation (165 sequences with marked tremor)

| Method | Off the path moving / still (px) | Tremor removed | Lag (ms) | Jerkiness (px) | No marked tremor: off the path / jerkiness (px) |
|---|---|---|---|---|---|
| No filter | 12.25 / 13.95 | 0% | 0 | 1.65 | 1.96 / 0.74 |
| One Euro (original settings) | 15.85 / 8.27 | 48% | 20 | 1.07 | 8.17 / 0.31 |
| Corrector v4, penalty S=0.5 (the app's corrector when this was chosen) | 6.84 / 5.14 | 87% | 0 | 1.28 | 1.70 / 0.74 |
| v4 + One Euro 2 Hz | 9.74 / 3.90 | 89% | 10 | 0.63 | 2.97 / 0.56 |
| v4 + One Euro 4 Hz | 9.16 / 4.26 | 89% | 10 | 0.68 | 2.73 / 0.57 |
| v4 + One Euro 8 Hz | 8.46 / 4.64 | 88% | 10 | 0.76 | 2.44 / 0.60 |
| v4 + One Euro 16 Hz | 7.81 / 4.90 | 88% | 10 | 0.88 | 2.16 / 0.63 |
| v4 + average of 30 ms | 8.54 / 5.02 | 88% | 10 | 0.84 | 2.46 / 0.60 |
| v4 + average of 50 ms | 10.80 / 4.78 | 88% | 20 | 0.69 | 3.38 / 0.57 |
| Corrector v4, penalty S=2 | 7.16 / 5.40 | 87% | 0 | 1.07 | 1.75 / 0.71 |
| Corrector v4, penalty S=8 | 7.78 / 6.97 | 81% | 0 | 1.07 | 1.82 / 0.71 |

Rule fixed in advance: lowest jerkiness with lag at most 20 ms and distance while moving at most 7.52 px (10% above the current corrector's 6.84 px).

**Chosen: Corrector v4, penalty S=2** (jerkiness 1.07 px, lag 0 ms).

## Test (scored once, after choosing on validation; 236 sequences with marked tremor)

| Method | Off the path moving / still (px) | Tremor removed | Lag (ms) | Jerkiness (px) | No marked tremor: off the path / jerkiness (px) |
|---|---|---|---|---|---|
| No filter | 13.17 / 12.74 | 0% | 0 | 1.69 | 2.30 / 0.80 |
| One Euro (original settings) | 15.32 / 6.98 | 49% | 20 | 0.98 | 8.28 / 0.33 |
| Corrector v4, penalty S=0.5 (the app's corrector when this was chosen) | 6.94 / 4.86 | 87% | 0 | 1.37 | 1.85 / 0.78 |
| Corrector v4, penalty S=2 | 7.30 / 5.17 | 86% | 0 | 1.12 | 1.91 / 0.74 |

This project is a prototype and is not medical advice.
