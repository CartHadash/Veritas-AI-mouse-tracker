# Step 4 stress test: the app's models on more realistic movement (validation people)

Produced by `python evaluation/realism_stress.py`. Same validation people and tremor recordings; the movement is the realistic version 2 and the cursor goes through `device_view()` (whole pixels, uneven 60/125 samples per second). Detector v2 with its cut-off; corrector v4 (penalty 2) gated by detector v2.

## Detector

| Movement | Windows (tremor) | Missed cases | False alarms |
|---|---|---|---|
| original | 3452 (660) | 20.0% | 27.3% |
| realistic | 3452 (660) | 18.0% | 25.6% |

## Corrector (sequences with marked tremor, scored after 2.56 s)

| Movement | Method | Off the path moving / still (px) | Tremor removed | Lag (ms) | Jerkiness (px) |
|---|---|---|---|---|---|
| original | No filter | 12.25 / 13.95 | 0% | 0 | 1.65 |
| original | One Euro | 15.85 / 8.27 | 48% | 20 | 1.07 |
| original | Our system | 7.16 / 5.40 | 87% | 0 | 1.07 |
| realistic | No filter | 12.54 / 11.50 | 0% | 0 | 1.40 |
| realistic | One Euro | 14.75 / 6.62 | 49% | 20 | 0.93 |
| realistic | Our system | 7.08 / 4.71 | 87% | 0 | 1.14 |

## Decision (rule fixed in advance)

- Missed cases changed by -2.0 points, false alarms by -1.7 points (limit +5).
- The corrector's advantage over no filter while moving: 5.08 px on original movement, 5.45 px on realistic movement (grew by 7%; limit a third).

**No retraining: the models do not clearly drop on realistic movement.**

This project is a prototype and is not medical advice.
