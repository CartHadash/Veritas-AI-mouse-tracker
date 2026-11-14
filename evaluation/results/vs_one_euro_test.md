# Our model vs One Euro, as a person sees it (test people's replayed tremor)

Produced by `python evaluation/vs_one_euro.py --people test`. Demo page server code, browser-like timing (about 60 uneven samples per second), 41 s per run, scored after 3 s. distance = from the intended path; shake = leftover 3-12 Hz wobble (RMS); jerk = change in velocity per 10 ms step; lag = how far behind a moving hand. All in px except lag (ms).

| Tremor | Movement | Method | Distance | Shake | Jerk | Lag |
|---|---|---|---|---|---|---|
| mild | reaches | No filter | 1.46 | 1.79 | 0.55 | 0 |
| mild | reaches | One Euro | 9.04 | 3.66 | 0.26 | 30 |
| mild | reaches | Our network alone | 1.31 | 1.49 | 0.54 | 0 |
| mild | reaches | Our model + One Euro (the app) | 7.56 | 3.33 | 0.30 | 20 |
| mild | glide | No filter | 1.46 | 1.79 | 0.28 | 0 |
| mild | glide | One Euro | 3.58 | 0.54 | 0.07 | 80 |
| mild | glide | Our network alone | 1.76 | 1.19 | 0.21 | 30 |
| mild | glide | Our model + One Euro (the app) | 4.45 | 0.66 | 0.06 | 100 |
| mild | still | No filter | 1.46 | 1.79 | 0.28 | - |
| mild | still | One Euro | 0.27 | 0.32 | 0.04 | - |
| mild | still | Our network alone | 0.84 | 1.03 | 0.19 | - |
| mild | still | Our model + One Euro (the app) | 0.44 | 0.67 | 0.04 | - |
| medium | reaches | No filter | 5.80 | 6.80 | 1.00 | 0 |
| medium | reaches | One Euro | 9.69 | 4.62 | 0.39 | 20 |
| medium | reaches | Our network alone | 4.58 | 5.41 | 0.93 | 0 |
| medium | reaches | Our model + One Euro (the app) | 8.97 | 4.77 | 0.51 | 20 |
| medium | glide | No filter | 5.80 | 6.80 | 0.85 | 0 |
| medium | glide | One Euro | 3.76 | 2.30 | 0.21 | 80 |
| medium | glide | Our network alone | 3.84 | 4.16 | 0.66 | 40 |
| medium | glide | Our model + One Euro (the app) | 5.31 | 2.42 | 0.22 | 120 |
| medium | still | No filter | 5.80 | 6.80 | 0.85 | - |
| medium | still | One Euro | 1.41 | 1.70 | 0.15 | - |
| medium | still | Our network alone | 3.08 | 3.98 | 0.64 | - |
| medium | still | Our model + One Euro (the app) | 1.23 | 2.24 | 0.19 | - |
| strong | reaches | No filter | 12.54 | 15.14 | 1.80 | 0 |
| strong | reaches | One Euro | 11.02 | 8.06 | 0.72 | 30 |
| strong | reaches | Our network alone | 7.68 | 7.92 | 1.52 | 10 |
| strong | reaches | Our model + One Euro (the app) | 11.68 | 6.01 | 0.50 | 30 |
| strong | glide | No filter | 12.54 | 15.14 | 1.69 | 0 |
| strong | glide | One Euro | 4.89 | 4.88 | 0.47 | 70 |
| strong | glide | Our network alone | 5.21 | 5.48 | 1.21 | 60 |
| strong | glide | Our model + One Euro (the app) | 6.23 | 1.69 | 0.21 | 140 |
| strong | still | No filter | 12.54 | 15.14 | 1.69 | - |
| strong | still | One Euro | 3.37 | 4.38 | 0.41 | - |
| strong | still | Our network alone | 4.40 | 5.45 | 1.21 | - |
| strong | still | Our model + One Euro (the app) | 1.11 | 1.23 | 0.14 | - |

## Average over all 9 situations

| Method | Distance | Shake | Jerk |
|---|---|---|---|
| No filter | 6.60 | 7.91 | 1.00 |
| One Euro | 5.23 | 3.39 | 0.30 |
| Our network alone | 3.64 | 4.01 | 0.79 |
| Our model + One Euro (the app) | 5.22 | 2.56 | 0.24 |

This project is a prototype and is not medical advice.
