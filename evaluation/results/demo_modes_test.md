# Filter modes on the demo page: replayed tremor of TEST people (final figure)

Produced by `python evaluation/compare_modes.py --people test`. Average distance (px) between the shown cursor and the intended path after a 3 s warm-up, over 41 s so all 4 recordings of a strength level play once. Uses the server's own session code. First table: medium replayed tremor (the page's default).

Jerkiness = average size of the change in the shown cursor's velocity from one 10 ms step to the next, on an even 100 Hz time grid (px).

| Intended movement | Off the path: no filter / One Euro / our model (px) | Jerkiness: no filter / One Euro / our model (px) | Intended path jerkiness | Gate above 0.5 |
|---|---|---|---|---|
| reaches (100 Hz) | 6.08 / 11.76 / 4.65 | 1.10 / 0.31 / 1.01 | 0.49 | 88% |
| glide (100 Hz) | 6.08 / 5.57 / 4.00 | 0.91 / 0.17 / 0.72 | 0.00 | 94% |
| still (100 Hz) | 6.08 / 1.44 / 3.70 | 0.91 / 0.16 / 0.71 | 0.00 | 92% |
| reaches (60 Hz, uneven) | 6.00 / 13.79 / 5.03 | 1.00 / 0.33 / 0.93 | 0.44 | 82% |
| glide (60 Hz, uneven) | 6.00 / 5.60 / 4.29 | 0.85 / 0.16 / 0.69 | 0.00 | 93% |

## By replayed tremor strength (reaches and still hand, 100 Hz)

| Replayed tremor | Movement | Off the path: no filter / One Euro / our model (px) | Our model vs no filter | Jerkiness: no filter / One Euro / our model (px) |
|---|---|---|---|---|
| mild | reaches | 1.55 / 11.54 / 1.46 | 6% closer | 0.60 / 0.20 / 0.59 |
| mild | still | 1.55 / 0.28 / 0.74 | 53% closer | 0.30 / 0.04 / 0.17 |
| medium | reaches | 6.08 / 11.76 / 4.65 | 23% closer | 1.10 / 0.31 / 1.01 |
| medium | still | 6.08 / 1.44 / 3.70 | 39% closer | 0.91 / 0.16 / 0.71 |
| strong | reaches | 13.12 / 12.65 / 6.23 | 53% closer | 1.94 / 0.59 / 1.56 |
| strong | still | 13.12 / 3.46 / 4.06 | 69% closer | 1.82 / 0.42 / 1.29 |

Replayed tremor OFF, reaches at 100 Hz: our model 0.08 px from the path (no filter 0.00 px); gate above 0.5 for 16% of the time.

This project is a prototype and is not medical advice.
