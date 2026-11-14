# Calibration test: does choosing the filter per person help? (validation people)

Produced by `python evaluation/calibration_sim.py --people val`. For each of 72 people (41 with any tremor-marked recording): one recording is the 10 s calibration test (still dot, then slowly moving dot), two other recordings of the same person are later use (computer-generated reaches). The tremor is used at 0.5x, 1x and 2x size, like different mouse speed settings. Average distance (px) from the intended path during later use, after the first 2.56 s.

| Tremor size | People | Always our model | Always One Euro | Calibration's choice | Best in hindsight | Calibration chose |
|---|---|---|---|---|---|---|
| 0.5x | all 72 | 1.35 | 11.90 | 1.51 | 1.26 | No filter 20, One Euro 1, Our model 51 |
| 0.5x | with tremor 41 | 1.54 | 11.78 | 1.85 | 1.47 | No filter 10, One Euro 1, Our model 30 |
| 1.0x | all 72 | 2.37 | 12.14 | 3.15 | 2.30 | No filter 7, One Euro 5, Our model 60 |
| 1.0x | with tremor 41 | 2.65 | 12.08 | 3.76 | 2.60 | No filter 4, One Euro 4, Our model 33 |
| 2.0x | all 72 | 3.91 | 12.99 | 5.17 | 3.86 | No filter 4, One Euro 10, Our model 58 |
| 2.0x | with tremor 41 | 4.46 | 13.15 | 6.32 | 4.42 | No filter 2, One Euro 8, Our model 31 |

This project is a prototype and is not medical advice.
