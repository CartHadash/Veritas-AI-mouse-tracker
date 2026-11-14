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

## Kept versions on TEST people (scored once)

| Detector | Data | Missed cases | False alarms |
|---|---|---|---|
| v1 | test, normal | 14.3% | 27.0% |
| v1 | test, pause-free | 8.1% | 45.3% |
| v2 | test, normal | 12.9% | 27.1% |
| v2 | test, pause-free | 11.2% | 20.4% |

This project is a prototype and is not medical advice.
