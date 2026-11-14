# Our model vs One Euro, as a person sees it (test people's replayed tremor)

Produced by `python evaluation/vs_one_euro.py --people test`. Demo page server code, browser-like timing (about 60 uneven samples per second), 41 s per run, scored after 3 s. distance = from the intended path; shake = leftover 3-12 Hz wobble (RMS); jerk = change in velocity per 10 ms step; lag = how far behind a moving hand. All in px except lag (ms).

| Tremor | Movement | Method | Distance | Shake | Jerk | Lag |
|---|---|---|---|---|---|---|
| mild | reaches | No filter | 1.46 | 1.79 | 0.55 | 0 |
| mild | reaches | One Euro | 9.04 | 3.66 | 0.26 | 30 |
| mild | reaches | Our network alone | 1.32 | 1.55 | 0.52 | 0 |
| mild | reaches | Our model + One Euro (the app) | 7.49 | 3.34 | 0.30 | 20 |
| mild | glide | No filter | 1.46 | 1.79 | 0.28 | 0 |
| mild | glide | One Euro | 3.58 | 0.54 | 0.07 | 80 |
| mild | glide | Our network alone | 1.29 | 1.27 | 0.20 | 10 |
| mild | glide | Our model + One Euro (the app) | 3.81 | 0.68 | 0.06 | 90 |
| mild | still | No filter | 1.46 | 1.79 | 0.28 | - |
| mild | still | One Euro | 0.27 | 0.32 | 0.04 | - |
| mild | still | Our network alone | 0.99 | 1.19 | 0.19 | - |
| mild | still | Our model + One Euro (the app) | 0.43 | 0.69 | 0.05 | - |
| medium | reaches | No filter | 5.80 | 6.80 | 1.00 | 0 |
| medium | reaches | One Euro | 9.69 | 4.62 | 0.39 | 20 |
| medium | reaches | Our network alone | 5.06 | 5.78 | 0.90 | 0 |
| medium | reaches | Our model + One Euro (the app) | 9.10 | 4.83 | 0.51 | 20 |
| medium | glide | No filter | 5.80 | 6.80 | 0.85 | 0 |
| medium | glide | One Euro | 3.76 | 2.30 | 0.21 | 80 |
| medium | glide | Our network alone | 4.36 | 5.11 | 0.67 | 10 |
| medium | glide | Our model + One Euro (the app) | 4.41 | 2.67 | 0.25 | 90 |
| medium | still | No filter | 5.80 | 6.80 | 0.85 | - |
| medium | still | One Euro | 1.41 | 1.70 | 0.15 | - |
| medium | still | Our network alone | 4.22 | 5.06 | 0.67 | - |
| medium | still | Our model + One Euro (the app) | 1.57 | 2.45 | 0.21 | - |
| strong | reaches | No filter | 12.54 | 15.14 | 1.80 | 0 |
| strong | reaches | One Euro | 11.02 | 8.06 | 0.72 | 30 |
| strong | reaches | Our network alone | 7.91 | 8.01 | 1.44 | 10 |
| strong | reaches | Our model + One Euro (the app) | 11.79 | 5.95 | 0.49 | 30 |
| strong | glide | No filter | 12.54 | 15.14 | 1.69 | 0 |
| strong | glide | One Euro | 4.89 | 4.88 | 0.47 | 70 |
| strong | glide | Our network alone | 5.34 | 6.10 | 1.21 | 20 |
| strong | glide | Our model + One Euro (the app) | 4.85 | 1.83 | 0.22 | 100 |
| strong | still | No filter | 12.54 | 15.14 | 1.69 | - |
| strong | still | One Euro | 3.37 | 4.38 | 0.41 | - |
| strong | still | Our network alone | 5.18 | 6.09 | 1.21 | - |
| strong | still | Our model + One Euro (the app) | 1.37 | 1.35 | 0.16 | - |

## Average over all 9 situations

| Method | Distance | Shake | Jerk |
|---|---|---|---|
| No filter | 6.60 | 7.91 | 1.00 |
| One Euro | 5.23 | 3.39 | 0.30 |
| Our network alone | 3.96 | 4.46 | 0.78 |
| Our model + One Euro (the app) | 4.98 | 2.64 | 0.25 |

This project is a prototype and is not medical advice.
