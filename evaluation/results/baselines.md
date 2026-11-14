# Baselines

Produced by `python evaluation/run_baselines.py` (step 6). Do not edit by hand.

## Detector baselines

Missed cases = real tremor windows called "no tremor". False alarms = no-tremor windows called "tremor". Cut-offs chosen on validation only.

Frequency rule cut-offs (share of movement power in 3-12 Hz): balanced 0.592; missed <= 10% on validation 0.065.

### Validation (3452 windows: 660 tremor, 2792 no tremor)

| Detector | Windows | Missed cases | False alarms | Accuracy |
|---|---|---|---|---|
| Always "no tremor" | all | 100.0% | 0.0% | 80.9% |
| Always "no tremor" | hand moving | 100.0% | 0.0% | 80.8% |
| Always "no tremor" | hand still | 100.0% | 0.0% | 81.0% |
| Frequency rule (balanced) | all | 52.9% | 21.5% | 72.5% |
| Frequency rule (balanced) | hand moving | 54.9% | 20.5% | 72.9% |
| Frequency rule (balanced) | hand still | 46.1% | 24.8% | 71.1% |
| Frequency rule (missed <= 10% on val) | all | 9.7% | 74.4% | 38.0% |
| Frequency rule (missed <= 10% on val) | hand moving | 9.8% | 75.6% | 37.0% |
| Frequency rule (missed <= 10% on val) | hand still | 9.2% | 70.2% | 41.4% |

### Test (3708 windows: 944 tremor, 2764 no tremor)

| Detector | Windows | Missed cases | False alarms | Accuracy |
|---|---|---|---|---|
| Always "no tremor" | all | 100.0% | 0.0% | 74.5% |
| Always "no tremor" | hand moving | 100.0% | 0.0% | 75.0% |
| Always "no tremor" | hand still | 100.0% | 0.0% | 72.7% |
| Frequency rule (balanced) | all | 47.2% | 19.4% | 73.5% |
| Frequency rule (balanced) | hand moving | 50.5% | 18.0% | 73.9% |
| Frequency rule (balanced) | hand still | 36.7% | 24.6% | 72.1% |
| Frequency rule (missed <= 10% on val) | all | 7.4% | 72.9% | 43.8% |
| Frequency rule (missed <= 10% on val) | hand moving | 7.6% | 73.2% | 43.1% |
| Frequency rule (missed <= 10% on val) | hand still | 6.8% | 71.5% | 46.1% |

## Corrector baselines (test: 236 sequences with marked tremor, 694 without)

Distances, tremor removed and lag are measured on the sequences with marked tremor; the "steady-hand" column is the average distance on sequences without marked tremor (a good filter should not make a steady hand worse). The first 0.5 s of each sequence is ignored so every filter has warmed up. Lag = the delay (0-400 ms) that best lines the output up with the intended path while moving.

| Method | Distance while moving (px) | Distance while still (px) | Tremor removed | Lag (ms) | Distance on steady-hand sequences (px) | Notes |
|---|---|---|---|---|---|---|
| No filter | 12.51 | 12.75 | 0% | 0 | 2.36 |  |
| Lower sensitivity x0.5 | 6.23 | 6.38 | 75% | 0 | 1.18 | hand must travel 2x as far |
| Lower sensitivity x0.25 | 3.03 | 3.25 | 94% | 0 | 0.59 | hand must travel 4x as far |
| Moving average | 21.46 | 8.43 | 51% | 40 | 12.32 | settings chosen on validation: {'window': 0.1} |
| Moving average (pre-hackathon default settings) | 34.06 | 3.38 | 91% | 90 | 22.65 |  |
| One Euro | 13.03 | 10.97 | 10% | 10 | 4.31 | settings chosen on validation: {'min_cutoff': 2.0, 'beta': 0.03} |
| One Euro (pre-hackathon default settings) | 15.02 | 6.92 | 50% | 20 | 8.04 |  |
| Kalman | 15.04 | 14.78 | -36% | 0 | 3.85 | settings chosen on validation: {'measurement_std': 3.0, 'accel_std': 4000.0} |
| Kalman (pre-hackathon default settings) | 17.75 | 9.11 | 66% | 20 | 11.25 |  |

This project is a prototype and is not medical advice.
