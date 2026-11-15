# Clicking real buttons with the system-wide corrector: simulated (validation people's replayed tremor)

Produced by `python evaluation/systemwide_clicks.py --people val`. The hand reaches 300 px in 0.6 s, stops exactly on the button, presses 0.2-0.6 s later and holds 80-200 ms; 80 clicks per row. Share of clicks that land (on the button at the press and at the release).

| Replayed tremor | Method | 22 px: without / with freeze | 10 px: without / with freeze |
|---|---|---|---|
| medium | No filter | 95% / 96% | 85% / 91% |
| medium | One Euro | 99% / 99% | 95% / 96% |
| medium | Our model, Steadiest | 100% / 100% | 99% / 99% |
| medium | Our model, Balanced | 100% / 100% | 95% / 96% |
| medium | Our model, Faster | 99% / 99% | 95% / 96% |
| strong | No filter | 69% / 81% | 28% / 42% |
| strong | One Euro | 95% / 96% | 74% / 81% |
| strong | Our model, Steadiest | 98% / 99% | 86% / 91% |
| strong | Our model, Balanced | 98% / 99% | 82% / 88% |
| strong | Our model, Faster | 95% / 96% | 78% / 82% |

Rule fixed in advance: B3's default smoothing level is the one with the most clicks landing on the 10 px button with click freeze and strong tremor; a tie goes to the steadier level.

**Chosen: steadiest.**

## Click where you aimed (our model, Steadiest, click freeze on)

At the press, the click is placed at the average of where the cursor was shown over the last moments (only while tremor is being corrected). Share of clicks that land.

| Averaged over | No tremor: 22 px / 10 px | Medium: 22 px / 10 px | Strong: 22 px / 10 px |
|---|---|---|---|
| off (click where the cursor is) | 100% / 100% | 100% / 99% | 99% / 91% |
| 0.1 s | 100% / 100% | 100% / 99% | 99% / 95% |
| 0.2 s | 100% / 100% | 100% / 100% | 99% / 95% |
| 0.3 s | 100% / 100% | 100% / 100% | 99% / 95% |

Rule fixed in advance (team leader): choose the window with the most clicks landing on the 10 px button with strong tremor, if that is more than with it off and no worse with medium tremor or no tremor (both button sizes); a tie goes to the shorter window; otherwise it stays off.

**Chosen: 0.1 s.**

This project is a prototype and is not medical advice.
