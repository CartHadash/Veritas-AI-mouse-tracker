# Calibration test: does choosing the filter per person help? (validation people)

Produced by `python evaluation/calibration_sim.py --people val`. For each of 72 people (41 with any tremor-marked recording): one recording is the 10 s calibration test (still dot, then slowly moving dot), two other recordings of the same person are later use (computer-generated reaches). The tremor is used at 0.5x, 1x and 2x size, like different mouse speed settings. Average distance (px) from the intended path during later use, after the first 2.56 s.

| Tremor size | People | Always our model | Always One Euro | Calibration's choice | Best in hindsight | Calibration chose |
|---|---|---|---|---|---|---|
| 0.5x | all 72 | 3.76 | 7.40 | 2.17 | 1.38 | No filter 47, One Euro 3, Our model (half strength) 12, Our model 10 |
| 0.5x | with tremor 41 | 4.18 | 7.42 | 2.58 | 1.65 | No filter 25, One Euro 2, Our model (half strength) 8, Our model 6 |
| 1.0x | all 72 | 4.83 | 7.87 | 3.61 | 2.46 | No filter 40, One Euro 8, Our model (half strength) 16, Our model 8 |
| 1.0x | with tremor 41 | 5.21 | 8.00 | 4.21 | 2.88 | No filter 23, One Euro 5, Our model (half strength) 9, Our model 4 |
| 2.0x | all 72 | 6.28 | 9.24 | 5.85 | 4.11 | No filter 28, One Euro 11, Our model (half strength) 16, Our model 17 |
| 2.0x | with tremor 41 | 6.79 | 9.68 | 6.94 | 4.79 | No filter 15, One Euro 7, Our model (half strength) 8, Our model 11 |

This project is a prototype and is not medical advice.
