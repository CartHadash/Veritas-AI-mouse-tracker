# The page's "Steadier or more responsive" choice

Produced by `python evaluation/response_levels.py`. Each choice set through `server.settings` as the page sets it, then the demo page's server code with replayed tremor, browser-like timing; averages over mild/medium/strong x reaching/gliding/still (lag: reaching and gliding only). Distance, shake and jerk in px, as in `vs_one_euro.py`.

## Validation people

| Choice on the page | Lag while moving (ms) | Distance | Shake | Jerk |
|---|---|---|---|---|
| Steadiest (default) | 67 | 5.29 | 2.98 | 0.21 |
| Balanced | 42 | 3.96 | 3.39 | 0.28 |
| Faster | 27 | 3.74 | 3.83 | 0.38 |

## Test people

| Choice on the page | Lag while moving (ms) | Distance | Shake | Jerk |
|---|---|---|---|---|
| Steadiest (default) | 72 | 5.22 | 2.56 | 0.24 |
| Balanced | 47 | 3.68 | 2.87 | 0.32 |
| Faster | 30 | 3.47 | 3.38 | 0.45 |

## Switching while moving (validation people, strong tremor, reaching)

| Run | Largest single step of the cursor (px) |
|---|---|
| Always Steadiest (default) | 54.86 |
| Always Balanced | 54.83 |
| Always Faster | 54.58 |
| Switching level every 2 s | 55.78 |

This project is a prototype and is not medical advice.
