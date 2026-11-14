# Detector v1: validation results (used to choose settings and the cut-off)

Produced by `python models/detector/train.py`. Validation people only; test people are not used here.

Chosen settings: `{'learning_rate': 0.05, 'max_leaf_nodes': 31, 'max_iter': 200}`; validation average precision 0.676 (1.0 = perfect ranking; the share of tremor windows, 0.191, = random guessing).

## Trade-off between missed cases and false alarms (DECISION 4)

| Missed cases at most | Cut-off | Missed (all) | False alarms (all) | Missed (hand moving) | False alarms (hand moving) |
|---|---|---|---|---|---|
| 5% | 0.070 | 5.0% | 56.5% | 4.9% | 61.7% |
| 10% | 0.093 | 10.0% | 46.5% | 10.2% | 50.6% |
| 15% | 0.131 | 15.0% | 35.3% | 15.7% | 38.3% |
| 20% | 0.166 | 20.0% | 27.8% | 20.9% | 30.3% |
| 30% | 0.241 | 30.0% | 16.4% | 32.1% | 18.3% |

Size estimate error on validation tremor windows: median 1.31 px (tremor windows' median size 5.10 px).

## Which features mattered (drop in average precision when shuffled)

| Feature | Importance |
|---|---|
| share of time nearly still | 0.340 |
| peak sharpness | 0.063 |
| power 7-9 Hz (log) | 0.026 |
| power 9-12 Hz (log) | 0.026 |
| median speed (log) | 0.026 |
| rhythm regularity | 0.021 |
| peak frequency in 3-12 Hz | 0.018 |
| power 5-7 Hz (log) | 0.018 |
| shake size 3-12 Hz (px, log) | 0.015 |
| power 12-20 Hz (log) | 0.007 |
| direction reversals per second | 0.007 |
| peak height vs typical (log) | 0.004 |
| acceleration size (log) | 0.003 |
| power 3-5 Hz (log) | 0.001 |
| share of power in 3-12 Hz | 0.001 |
| power 0.5-3 Hz (log) | 0.000 |
| max speed (log) | 0.000 |
| power 20-50 Hz (log) | 0.000 |
| mean speed (log) | -0.001 |

This project is a prototype and is not medical advice.
