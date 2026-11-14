# Calibration test: does choosing the filter per person help? (validation people)

Produced by `python evaluation/calibration_sim.py --people val`. For each of 72 people (41 with any tremor-marked recording): one recording is the 10 s calibration test (still dot, then slowly moving dot), two other recordings of the same person are later use (computer-generated reaches). The tremor is used at 0.5x, 1x and 2x size, like different mouse speed settings. Average distance (px) from the intended path during later use, after the first 2.56 s.

| Tremor size | People | Always our model | Always One Euro | Calibration's choice | Best in hindsight | Calibration chose |
|---|---|---|---|---|---|---|
| 0.5x | all 72 | 1.40 | 7.40 | 1.69 | 1.31 | No filter 17, One Euro 4, Our model (half strength) 1, Our model 50 |
| 0.5x | with tremor 41 | 1.61 | 7.42 | 1.98 | 1.54 | No filter 10, One Euro 3, Our model 28 |
| 1.0x | all 72 | 2.45 | 7.87 | 3.40 | 2.36 | No filter 7, One Euro 12, Our model 53 |
| 1.0x | with tremor 41 | 2.75 | 8.00 | 3.96 | 2.69 | No filter 4, One Euro 8, Our model 29 |
| 2.0x | all 72 | 4.02 | 9.24 | 5.13 | 3.97 | No filter 4, One Euro 17, Our model 51 |
| 2.0x | with tremor 41 | 4.59 | 9.68 | 5.98 | 4.55 | No filter 2, One Euro 11, Our model 28 |

This project is a prototype and is not medical advice.
