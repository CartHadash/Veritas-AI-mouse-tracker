# Detector v2: validation results (used to choose settings and the cut-off)

Produced by `python models/detector/train.py --version v2 --with-continuous`. Validation people only; test people are not used here. Validation here = normal + pause-free windows.

Chosen settings: `{'learning_rate': 0.05, 'max_leaf_nodes': 31, 'max_iter': 400}`; validation average precision 0.727 (1.0 = perfect ranking; the share of tremor windows, 0.191, = random guessing).

## Trade-off between missed cases and false alarms (DECISION 4)

| Missed cases at most | Cut-off | Missed (all) | False alarms (all) | Missed (hand moving) | False alarms (hand moving) |
|---|---|---|---|---|---|
| 5% | 0.058 | 5.0% | 53.3% | 4.1% | 62.7% |
| 10% | 0.083 | 10.0% | 40.8% | 9.6% | 48.9% |
| 15% | 0.113 | 15.0% | 32.1% | 16.3% | 39.3% |
| 20% | 0.158 | 20.0% | 23.3% | 21.9% | 28.5% |
| 30% | 0.270 | 30.0% | 12.6% | 34.3% | 15.6% |

Size estimate error on validation tremor windows: median 0.98 px (tremor windows' median size 5.10 px).

## Which features mattered (drop in average precision when shuffled)

| Feature | Importance |
|---|---|
| share of time nearly still | 0.170 |
| peak sharpness | 0.078 |
| peak frequency in 3-12 Hz | 0.052 |
| power 7-9 Hz (log) | 0.049 |
| power 9-12 Hz (log) | 0.047 |
| rhythm regularity | 0.046 |
| power 5-7 Hz (log) | 0.043 |
| shake size 3-12 Hz (px, log) | 0.037 |
| direction reversals per second | 0.015 |
| median speed (log) | 0.014 |
| peak height vs typical (log) | 0.013 |
| power 12-20 Hz (log) | 0.008 |
| acceleration size (log) | 0.004 |
| power 3-5 Hz (log) | 0.003 |
| power 20-50 Hz (log) | 0.002 |
| power 0.5-3 Hz (log) | 0.001 |
| max speed (log) | 0.001 |
| mean speed (log) | 0.001 |
| share of power in 3-12 Hz | 0.001 |

This project is a prototype and is not medical advice.
