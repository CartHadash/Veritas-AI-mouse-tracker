# Corrector v1 (gate: detector v2): results on TEST people

Produced by `python evaluation/evaluate_corrector.py --detector v2`. Test sequences: 930 (236 with marked tremor, 694 without). Scored after the first 2.56 s of each 5.12 s sequence (the detector's warm-up), the same samples for every method. Distances, tremor removed and lag are on sequences with marked tremor; the last column is the average distance on sequences without marked tremor.

| Method | Distance while moving (px) | Distance while still (px) | Tremor removed | Lag (ms) | Distance on sequences without marked tremor (px) | Notes |
|---|---|---|---|---|---|---|
| No filter | 13.17 | 12.74 | 0% | 0 | 2.30 |  |
| Lower sensitivity x0.5 | 6.59 | 6.40 | 75% | 0 | 1.15 | hand must travel 2x as far |
| Moving average 0.2 s (original) | 32.86 | 3.27 | 92% | 100 | 23.89 |  |
| One Euro (original settings) | 19.66 | 5.92 | 68% | 40 | 12.95 |  |
| One Euro (tuned on validation) | 13.78 | 10.43 | 15% | 10 | 4.96 |  |
| One Euro (original) + detector gate | 17.21 | 6.41 | 65% | 30 | 5.85 | classical filter switched by our detector |
| Corrector v1, always on | 6.72 | 5.18 | 89% | 0 | 2.43 | our network alone |
| **Corrector v1 + detector gate** | 7.15 | 5.93 | 84% | 0 | 2.00 | **our system: both models together** |

## By tremor size (sequences with marked tremor)

| Tremor size | Sequences | Still: no filter | Still: One Euro (orig.) + gate | Still: our system | Removed: One Euro (orig.) + gate | Removed: our system |
|---|---|---|---|---|---|---|
| mild (under 3 px) | 47 | 1.53 | 1.44 | 1.16 | -205% | 3% |
| medium (3-10 px) | 88 | 4.62 | 2.40 | 3.16 | 37% | 48% |
| strong (over 10 px) | 101 | 25.81 | 12.57 | 10.89 | 66% | 85% |

This project is a prototype and is not medical advice.
