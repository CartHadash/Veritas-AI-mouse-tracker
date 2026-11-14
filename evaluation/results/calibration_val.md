# Calibration test: does choosing the filter per person help? (validation people)

Produced by `python evaluation/calibration_sim.py --people val`. For each of 72 people (41 with any tremor-marked recording): one recording is the 10 s calibration test (still dot, then slowly moving dot), two other recordings of the same person are later use (computer-generated reaches). The tremor is used at 0.5x, 1x and 2x size, like different mouse speed settings. Average distance (px) from the intended path during later use, after the first 2.56 s.

| Tremor size | People | Always our model | Always One Euro | Calibration's choice | Best in hindsight | Calibration chose |
|---|---|---|---|---|---|---|
| 0.5x | all 72 | 3.78 | 7.40 | 2.20 | 1.39 | No filter 47, One Euro 3, Our model (half strength) 11, Our model 11 |
| 0.5x | with tremor 41 | 4.21 | 7.42 | 2.63 | 1.66 | No filter 25, One Euro 2, Our model (half strength) 7, Our model 7 |
| 1.0x | all 72 | 4.86 | 7.87 | 3.62 | 2.48 | No filter 40, One Euro 8, Our model (half strength) 16, Our model 8 |
| 1.0x | with tremor 41 | 5.23 | 8.00 | 4.21 | 2.91 | No filter 23, One Euro 5, Our model (half strength) 9, Our model 4 |
| 2.0x | all 72 | 6.36 | 9.24 | 5.97 | 4.19 | No filter 26, One Euro 11, Our model (half strength) 17, Our model 18 |
| 2.0x | with tremor 41 | 6.88 | 9.68 | 7.05 | 4.88 | No filter 13, One Euro 7, Our model (half strength) 10, Our model 11 |

This project is a prototype and is not medical advice.
