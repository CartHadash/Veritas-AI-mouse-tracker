# Filter modes on the demo page: replayed tremor of TEST people (final figure)

Produced by `python evaluation/compare_modes.py --people test`. Average distance (px) between the shown cursor and the intended path after a 3 s warm-up, over 41 s so all 4 recordings of a strength level play once. Uses the server's own session code. First table: medium replayed tremor (the page's default).

Jerkiness = average size of the change in the shown cursor's velocity from one 10 ms step to the next, on an even 100 Hz time grid (px).

| Intended movement | Off the path: no filter / One Euro / our model (px) | Jerkiness: no filter / One Euro / our model (px) | Intended path jerkiness | Gate above 0.5 |
|---|---|---|---|---|
| reaches (100 Hz) | 6.08 / 7.77 / 4.90 | 1.10 / 0.43 / 0.91 | 0.49 | 88% |
| glide (100 Hz) | 6.08 / 3.55 / 4.26 | 0.91 / 0.26 / 0.63 | 0.00 | 94% |
| still (100 Hz) | 6.08 / 1.62 / 4.07 | 0.91 / 0.18 / 0.62 | 0.00 | 92% |
| reaches (60 Hz, uneven) | 6.00 / 9.73 / 5.22 | 1.00 / 0.39 / 0.90 | 0.44 | 82% |
| glide (60 Hz, uneven) | 6.00 / 3.79 / 4.50 | 0.85 / 0.21 / 0.67 | 0.00 | 93% |

## By replayed tremor strength (reaches and still hand, 100 Hz)

| Replayed tremor | Movement | Off the path: no filter / One Euro / our model (px) | Our model vs no filter | Jerkiness: no filter / One Euro / our model (px) |
|---|---|---|---|---|
| mild | reaches | 1.55 / 7.04 / 1.51 | 3% closer | 0.60 / 0.26 / 0.55 |
| mild | still | 1.55 / 0.29 / 0.91 | 41% closer | 0.30 / 0.04 / 0.15 |
| medium | reaches | 6.08 / 7.77 / 4.90 | 19% closer | 1.10 / 0.43 / 0.91 |
| medium | still | 6.08 / 1.62 / 4.07 | 33% closer | 0.91 / 0.18 / 0.62 |
| strong | reaches | 13.12 / 9.87 / 6.66 | 49% closer | 1.94 / 0.85 / 1.18 |
| strong | still | 13.12 / 4.16 / 4.33 | 67% closer | 1.82 / 0.56 / 0.92 |

Replayed tremor OFF, reaches at 100 Hz: our model 0.07 px from the path (no filter 0.00 px); gate above 0.5 for 16% of the time.

This project is a prototype and is not medical advice.
