# A canceller tuned to the person's tremor rhythm (notch filter): validation first

Produced by `python evaluation/notch_canceller.py`. Sequences with marked tremor, gated by detector v2 as in the app, scored after 2.56 s. The notch is centred on the rhythm the detector measures every 0.1 s; Q sets its width.

## Validation (165 sequences with marked tremor)

| Method | Off the path moving / still (px) | Tremor removed | Lag (ms) | Jerkiness (px) | No marked tremor: off the path (px) |
|---|---|---|---|---|---|
| No filter | 12.25 / 13.95 | 0% | 0 | 1.65 | 1.96 |
| Our corrector (v4, penalty 2; the app) | 7.16 / 5.40 | 87% | 0 | 1.07 | 1.75 |
| Notch, Q=4 | 8.75 / 7.32 | 75% | 10 | 1.14 | 2.98 |
| Our corrector + notch, Q=4 | 8.47 / 4.21 | 92% | 10 | 0.99 | 2.88 |
| Notch, Q=2 | 9.94 / 5.71 | 83% | 10 | 1.04 | 3.85 |
| Our corrector + notch, Q=2 | 10.55 / 3.62 | 93% | 20 | 0.95 | 3.81 |
| Notch, Q=1 | 13.59 / 4.39 | 88% | 30 | 0.93 | 5.55 |
| Our corrector + notch, Q=1 | 14.78 / 3.09 | 93% | 30 | 0.91 | 5.57 |

Rule fixed in advance: replace the current corrector only if closer to the path both while moving and still, lag at most 20 ms, jerkiness no higher; then the closest while moving.

**Result: no candidate qualifies; the app keeps its corrector.**

This project is a prototype and is not medical advice.
