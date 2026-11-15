# Clicking real buttons with the system-wide corrector: simulated (test people's replayed tremor)

Produced by `python evaluation/systemwide_clicks.py --people test`. The hand reaches 300 px in 0.6 s, stops exactly on the button, presses 0.2-0.6 s later and holds 80-200 ms; 80 clicks per row. Share of clicks that land (on the button at the press and at the release).

| Replayed tremor | Method | 22 px: without / with freeze | 10 px: without / with freeze |
|---|---|---|---|
| medium | No filter | 99% / 100% | 78% / 85% |
| medium | One Euro | 100% / 100% | 100% / 100% |
| medium | Our model, Steadiest | 100% / 100% | 99% / 99% |
| medium | Our model, Balanced | 100% / 100% | 99% / 99% |
| medium | Our model, Faster | 100% / 100% | 99% / 99% |
| strong | No filter | 68% / 78% | 30% / 46% |
| strong | One Euro | 100% / 100% | 90% / 95% |
| strong | Our model, Steadiest | 100% / 100% | 99% / 99% |
| strong | Our model, Balanced | 99% / 99% | 96% / 98% |
| strong | Our model, Faster | 98% / 98% | 96% / 98% |

## Click where you aimed (our model, Steadiest, click freeze on)

At the press, the click is placed at the average of where the cursor was shown over the last moments (only while tremor is being corrected). Share of clicks that land.

| Averaged over | No tremor: 22 px / 10 px | Medium: 22 px / 10 px | Strong: 22 px / 10 px |
|---|---|---|---|
| off (click where the cursor is) | 100% / 100% | 100% / 99% | 100% / 99% |
| 0.1 s | 100% / 100% | 100% / 99% | 100% / 100% |

This project is a prototype and is not medical advice.
