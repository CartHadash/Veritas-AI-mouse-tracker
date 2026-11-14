# Our model vs One Euro, as a person sees it (validation people's replayed tremor)

Produced by `python evaluation/vs_one_euro.py --people val`. Demo page server code, browser-like timing (about 60 uneven samples per second), 41 s per run, scored after 3 s. distance = from the intended path; shake = leftover 3-12 Hz wobble (RMS); jerk = change in velocity per 10 ms step; lag = how far behind a moving hand. All in px except lag (ms).

| Tremor | Movement | Method | Distance | Shake | Jerk | Lag |
|---|---|---|---|---|---|---|
| mild | reaches | No filter | 1.94 | 2.35 | 0.58 | 0 |
| mild | reaches | One Euro | 9.07 | 3.72 | 0.27 | 30 |
| mild | reaches | Our network alone | 1.69 | 2.02 | 0.57 | 0 |
| mild | reaches | Our model + One Euro (the app) | 8.36 | 3.46 | 0.27 | 20 |
| mild | glide | No filter | 1.94 | 2.35 | 0.34 | 0 |
| mild | glide | One Euro | 3.58 | 0.68 | 0.09 | 80 |
| mild | glide | Our network alone | 1.90 | 1.28 | 0.25 | 30 |
| mild | glide | Our model + One Euro (the app) | 4.86 | 0.51 | 0.06 | 110 |
| mild | still | No filter | 1.94 | 2.35 | 0.34 | - |
| mild | still | One Euro | 0.34 | 0.40 | 0.05 | - |
| mild | still | Our network alone | 0.85 | 0.95 | 0.22 | - |
| mild | still | Our model + One Euro (the app) | 0.32 | 0.30 | 0.03 | - |
| medium | reaches | No filter | 4.28 | 5.92 | 0.69 | 0 |
| medium | reaches | One Euro | 9.57 | 4.38 | 0.33 | 30 |
| medium | reaches | Our network alone | 3.19 | 4.09 | 0.67 | 0 |
| medium | reaches | Our model + One Euro (the app) | 8.23 | 4.03 | 0.32 | 20 |
| medium | glide | No filter | 4.28 | 5.92 | 0.45 | 0 |
| medium | glide | One Euro | 3.90 | 2.37 | 0.15 | 80 |
| medium | glide | Our network alone | 3.07 | 3.49 | 0.35 | 30 |
| medium | glide | Our model + One Euro (the app) | 4.24 | 1.72 | 0.12 | 100 |
| medium | still | No filter | 4.28 | 5.92 | 0.45 | - |
| medium | still | One Euro | 1.24 | 1.95 | 0.10 | - |
| medium | still | Our network alone | 2.35 | 3.33 | 0.35 | - |
| medium | still | Our model + One Euro (the app) | 1.07 | 1.55 | 0.10 | - |
| strong | reaches | No filter | 12.96 | 15.20 | 1.33 | 0 |
| strong | reaches | One Euro | 12.14 | 9.30 | 0.63 | 30 |
| strong | reaches | Our network alone | 8.00 | 8.67 | 1.22 | 0 |
| strong | reaches | Our model + One Euro (the app) | 11.70 | 6.93 | 0.47 | 30 |
| strong | glide | No filter | 12.96 | 15.20 | 1.20 | 0 |
| strong | glide | One Euro | 6.03 | 6.19 | 0.42 | 70 |
| strong | glide | Our network alone | 6.53 | 7.39 | 0.99 | 50 |
| strong | glide | Our model + One Euro (the app) | 6.12 | 4.35 | 0.29 | 120 |
| strong | still | No filter | 12.96 | 15.20 | 1.20 | - |
| strong | still | One Euro | 4.65 | 5.78 | 0.38 | - |
| strong | still | Our network alone | 5.90 | 7.28 | 0.97 | - |
| strong | still | Our model + One Euro (the app) | 2.70 | 4.00 | 0.25 | - |

## Average over all 9 situations

| Method | Distance | Shake | Jerk |
|---|---|---|---|
| No filter | 6.40 | 7.82 | 0.73 |
| One Euro | 5.62 | 3.86 | 0.27 |
| Our network alone | 3.72 | 4.28 | 0.62 |
| Our model + One Euro (the app) | 5.29 | 2.98 | 0.21 |

This project is a prototype and is not medical advice.
