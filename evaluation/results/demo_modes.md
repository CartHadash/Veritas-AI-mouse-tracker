# Filter modes on the demo page (demo tremor ON unless stated)

Produced by `python evaluation/compare_modes.py`. Average distance (px) between the shown cursor and the intended path after a 3 s warm-up, over 41 s so all 4 demo recordings of a strength level play once. Uses the server's own session code. First table: medium demo tremor (the page's default).

| Intended movement | No filter | One Euro | Our model | Our model, gate forced open | Our model, away from seams | Gate above 0.5 |
|---|---|---|---|---|---|---|
| reaches (100 Hz) | 6.09 | 11.76 | 4.81 | 4.80 | 4.85 | 87% |
| glide (100 Hz) | 6.09 | 5.56 | 4.17 | 3.99 | 4.19 | 95% |
| still (100 Hz) | 6.09 | 1.44 | 3.98 | 3.73 | 3.99 | 91% |
| reaches (60 Hz, uneven) | 6.08 | 13.78 | 5.05 | 5.01 | 5.09 | 89% |
| glide (60 Hz, uneven) | 6.08 | 5.58 | 4.34 | 4.26 | 4.36 | 96% |

## By demo tremor strength (reaches and still hand, 100 Hz)

| Demo tremor | Movement | No filter | One Euro | Our model | Our model vs no filter |
|---|---|---|---|---|---|
| mild | reaches | 1.56 | 11.54 | 1.67 | -7% closer |
| mild | still | 1.56 | 0.28 | 1.24 | 20% closer |
| medium | reaches | 6.09 | 11.76 | 4.81 | 21% closer |
| medium | still | 6.09 | 1.44 | 3.98 | 35% closer |
| strong | reaches | 13.15 | 12.65 | 8.63 | 34% closer |
| strong | still | 13.15 | 3.45 | 7.16 | 46% closer |

Demo tremor OFF, reaches at 100 Hz: our model 0.07 px from the path (no filter 0.00 px); gate above 0.5 for 16% of the time.

This project is a prototype and is not medical advice.
