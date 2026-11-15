# Click freeze: simulated clicks (test people's replayed tremor)

Produced by `python evaluation/click_sim.py --people test`. Perfect aim, hand still, clicks held 80-200 ms; misses come only from the shaking. Share of clicks that succeed (pressed and released on the target).

The 22 px target is the demo page's; the 10 px target (about a small checkbox) was added after seeing that 22 px is easy.

| Replayed tremor | Filter | Clicks | 22 px: without / with freeze | 10 px: without / with freeze |
|---|---|---|---|---|
| mild | No filter | 95 | 100% / 100% | 100% / 100% |
| mild | One Euro | 95 | 100% / 100% | 100% / 100% |
| mild | Our model | 95 | 100% / 100% | 100% / 100% |
| medium | No filter | 95 | 100% / 100% | 75% / 84% |
| medium | One Euro | 95 | 100% / 100% | 100% / 100% |
| medium | Our model | 95 | 100% / 100% | 100% / 100% |
| strong | No filter | 95 | 76% / 79% | 24% / 39% |
| strong | One Euro | 95 | 100% / 100% | 88% / 92% |
| strong | Our model | 95 | 100% / 100% | 99% / 99% |

## Click where you aimed (our model, click freeze on)

At the press the click is placed at the average of where the cursor was shown over the last moments, only while our model is correcting. Share of clicks that land.

| Averaged over | Mild: 22 px / 10 px | Medium: 22 px / 10 px | Strong: 22 px / 10 px |
|---|---|---|---|
| off (click where the cursor is) | 100% / 100% | 100% / 100% | 100% / 99% |
| 0.1 s | 100% / 100% | 100% / 100% | 100% / 100% |

This project is a prototype and is not medical advice.
