# Movement-aware detector, cheap version: two cut-offs (validation first)

Produced by `python evaluation/moving_cutoffs.py`. Detector v2, same model and scores; only the cut-off differs. "Looks moving" is a guess from the shaky cursor (0.32 s block averages travelling faster than 20 px/s for at least half of the window); the rows below use the tables' own definition of moving, from the intended path.

## Validation people (3452 windows: 660 tremor, 2792 no tremor)

The guess agrees with the true "moving" on 81.7% of windows (81.8% of tremor windows, 81.7% of no-tremor windows); 72.0% of windows look moving.

Cut-offs, each the fewest false alarms with at most 20% missed in its own group: one cut-off 0.155; two cut-offs 0.152 (looks moving) and 0.157 (looks still).

| Windows | One cut-off: missed | One cut-off: false alarms | Two cut-offs: missed | Two cut-offs: false alarms |
|---|---|---|---|---|
| all windows | 20.0% | 27.3% | 19.8% | 27.9% |
| hand truly moving | 20.9% | 30.3% | 20.7% | 31.1% |
| hand truly still | 17.1% | 17.4% | 17.1% | 17.4% |
| "moving on purpose" tasks (action) | 6.2% | 42.3% | 4.7% | 42.9% |

Rule fixed in advance: keep only if (a) false alarms with the hand truly moving are lower, (b) missed overall at most 20%, (c) false alarms overall not higher.

(a) no, (b) yes, (c) no. **Result: not kept; the app keeps its single cut-off.**

This project is a prototype and is not medical advice.
