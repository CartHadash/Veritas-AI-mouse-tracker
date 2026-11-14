# Filter modes on the demo page: replayed tremor of VALIDATION people (development)

Produced by `python evaluation/compare_modes.py --people val`. Average distance (px) between the shown cursor and the intended path after a 3 s warm-up, over 41 s so all 4 recordings of a strength level play once. Uses the server's own session code. First table: medium replayed tremor (the page's default).

Jerkiness = average size of the change in the shown cursor's velocity from one 10 ms step to the next, on an even 100 Hz time grid (px).

| Intended movement | Off the path: no filter / One Euro / our model (px) | Jerkiness: no filter / One Euro / our model (px) | Intended path jerkiness | Gate above 0.5 |
|---|---|---|---|---|
| reaches (100 Hz) | 4.44 / 11.87 / 3.10 | 0.76 / 0.25 / 0.70 | 0.49 | 89% |
| glide (100 Hz) | 4.44 / 5.72 / 2.87 | 0.48 / 0.11 / 0.36 | 0.00 | 76% |
| still (100 Hz) | 4.44 / 1.22 / 2.50 | 0.48 / 0.10 / 0.34 | 0.00 | 71% |
| reaches (60 Hz, uneven) | 4.39 / 13.64 / 3.34 | 0.69 / 0.28 / 0.67 | 0.44 | 87% |
| glide (60 Hz, uneven) | 4.39 / 5.77 / 2.94 | 0.45 / 0.10 / 0.36 | 0.00 | 76% |

## By replayed tremor strength (reaches and still hand, 100 Hz)

| Replayed tremor | Movement | Off the path: no filter / One Euro / our model (px) | Our model vs no filter | Jerkiness: no filter / One Euro / our model (px) |
|---|---|---|---|---|
| mild | reaches | 2.05 / 11.55 / 1.64 | 20% closer | 0.65 / 0.21 / 0.62 |
| mild | still | 2.05 / 0.36 / 0.66 | 68% closer | 0.37 / 0.05 / 0.19 |
| medium | reaches | 4.44 / 11.87 / 3.10 | 30% closer | 0.76 / 0.25 / 0.70 |
| medium | still | 4.44 / 1.22 / 2.50 | 44% closer | 0.48 / 0.10 / 0.34 |
| strong | reaches | 13.36 / 13.19 / 7.32 | 45% closer | 1.44 / 0.52 / 1.25 |
| strong | still | 13.36 / 4.35 / 6.41 | 52% closer | 1.28 / 0.35 / 0.96 |

Replayed tremor OFF, reaches at 100 Hz: our model 0.08 px from the path (no filter 0.00 px); gate above 0.5 for 16% of the time.

This project is a prototype and is not medical advice.
