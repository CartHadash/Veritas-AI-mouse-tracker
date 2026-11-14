# Click freeze: simulated clicks (validation people's replayed tremor)

Produced by `python evaluation/click_sim.py --people val`. Perfect aim, hand still, clicks held 80-200 ms; misses come only from the shaking. Share of clicks that succeed (pressed and released on the target).

The 22 px target is the demo page's; the 10 px target (about a small checkbox) was added after seeing that 22 px is easy.

| Replayed tremor | Filter | Clicks | 22 px: without / with freeze | 10 px: without / with freeze |
|---|---|---|---|---|
| mild | No filter | 95 | 100% / 100% | 100% / 100% |
| mild | One Euro | 95 | 100% / 100% | 100% / 100% |
| mild | Our model | 95 | 100% / 100% | 100% / 100% |
| medium | No filter | 95 | 98% / 100% | 84% / 89% |
| medium | One Euro | 95 | 99% / 100% | 97% / 100% |
| medium | Our model | 95 | 99% / 100% | 94% / 97% |
| strong | No filter | 95 | 71% / 82% | 28% / 46% |
| strong | One Euro | 95 | 96% / 97% | 73% / 83% |
| strong | Our model | 95 | 95% / 97% | 71% / 82% |

This project is a prototype and is not medical advice.
