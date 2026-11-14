# Filter modes on the demo page: replayed tremor of TEST people (final figure)

Produced by `python evaluation/compare_modes.py --people test`. Average distance (px) between the shown cursor and the intended path after a 3 s warm-up, over 41 s so all 4 recordings of a strength level play once. Uses the server's own session code. First table: medium replayed tremor (the page's default until Sat 14 Nov; now strong).

Jerkiness = average size of the change in the shown cursor's velocity from one 10 ms step to the next, on an even 100 Hz time grid (px).

| Intended movement | Off the path: no filter / One Euro / our model (px) | Jerkiness: no filter / One Euro / our model (px) | Intended path jerkiness | Gate above 0.5 |
|---|---|---|---|---|
| reaches (100 Hz) | 6.08 / 7.77 / 7.38 | 1.10 / 0.43 / 0.47 | 0.49 | 88% |
| glide (100 Hz) | 6.08 / 3.55 / 4.05 | 0.91 / 0.26 / 0.23 | 0.00 | 94% |
| still (100 Hz) | 6.08 / 1.62 / 1.52 | 0.91 / 0.18 / 0.18 | 0.00 | 92% |
| reaches (60 Hz, uneven) | 6.00 / 9.73 / 9.20 | 1.00 / 0.39 / 0.51 | 0.44 | 82% |
| glide (60 Hz, uneven) | 6.00 / 3.79 / 4.45 | 0.85 / 0.21 / 0.25 | 0.00 | 93% |

## By replayed tremor strength (reaches and still hand, 100 Hz)

| Replayed tremor | Movement | Off the path: no filter / One Euro / our model (px) | Our model vs no filter | Jerkiness: no filter / One Euro / our model (px) |
|---|---|---|---|---|
| mild | reaches | 1.55 / 7.04 / 6.43 | -314% closer | 0.60 / 0.26 / 0.27 |
| mild | still | 1.55 / 0.29 / 0.45 | 71% closer | 0.30 / 0.04 / 0.05 |
| medium | reaches | 6.08 / 7.77 / 7.38 | -21% closer | 1.10 / 0.43 / 0.47 |
| medium | still | 6.08 / 1.62 / 1.52 | 75% closer | 0.91 / 0.18 / 0.18 |
| strong | reaches | 13.12 / 9.87 / 9.66 | 26% closer | 1.94 / 0.85 / 0.39 |
| strong | still | 13.12 / 4.16 / 1.33 | 90% closer | 1.82 / 0.56 / 0.13 |

Replayed tremor OFF, reaches at 100 Hz: our model 1.75 px from the path (no filter 0.00 px); gate above 0.5 for 16% of the time.

This project is a prototype and is not medical advice.
