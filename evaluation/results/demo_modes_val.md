# Filter modes on the demo page: replayed tremor of VALIDATION people (development)

Produced by `python evaluation/compare_modes.py --people val`. Average distance (px) between the shown cursor and the intended path after a 3 s warm-up, over 41 s so all 4 recordings of a strength level play once. Uses the server's own session code. First table: medium replayed tremor (the page's default until Sat 14 Nov; now strong).

Jerkiness = average size of the change in the shown cursor's velocity from one 10 ms step to the next, on an even 100 Hz time grid (px).

| Intended movement | Off the path: no filter / One Euro / our model (px) | Jerkiness: no filter / One Euro / our model (px) | Intended path jerkiness | Gate above 0.5 |
|---|---|---|---|---|
| reaches (100 Hz) | 4.44 / 7.75 / 3.28 | 0.76 / 0.34 / 0.62 | 0.49 | 89% |
| glide (100 Hz) | 4.44 / 3.68 / 3.07 | 0.48 / 0.18 / 0.31 | 0.00 | 76% |
| still (100 Hz) | 4.44 / 1.47 / 2.84 | 0.48 / 0.13 / 0.30 | 0.00 | 71% |
| reaches (60 Hz, uneven) | 4.39 / 9.60 / 3.50 | 0.69 / 0.33 / 0.62 | 0.44 | 87% |
| glide (60 Hz, uneven) | 4.39 / 3.94 / 3.13 | 0.45 / 0.15 / 0.34 | 0.00 | 76% |

## By replayed tremor strength (reaches and still hand, 100 Hz)

| Replayed tremor | Movement | Off the path: no filter / One Euro / our model (px) | Our model vs no filter | Jerkiness: no filter / One Euro / our model (px) |
|---|---|---|---|---|
| mild | reaches | 2.05 / 7.08 / 1.76 | 14% closer | 0.65 / 0.28 / 0.56 |
| mild | still | 2.05 / 0.37 / 1.04 | 50% closer | 0.37 / 0.06 / 0.18 |
| medium | reaches | 4.44 / 7.75 / 3.28 | 26% closer | 0.76 / 0.34 / 0.62 |
| medium | still | 4.44 / 1.47 / 2.84 | 36% closer | 0.48 / 0.13 / 0.30 |
| strong | reaches | 13.36 / 11.05 / 7.85 | 41% closer | 1.44 / 0.77 / 1.04 |
| strong | still | 13.36 / 5.75 / 6.87 | 49% closer | 1.28 / 0.54 / 0.79 |

Replayed tremor OFF, reaches at 100 Hz: our model 0.07 px from the path (no filter 0.00 px); gate above 0.5 for 16% of the time.

This project is a prototype and is not medical advice.
