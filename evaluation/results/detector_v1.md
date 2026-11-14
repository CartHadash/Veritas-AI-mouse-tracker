# Detector v1: results on TEST people

Produced by `python evaluation/evaluate_detector.py --missed-target 0.2`. Test people (3708 windows: 944 tremor, 2764 no tremor) were used once, after every setting was chosen on validation.

DECISION 4: cut-off chosen on validation so that missed cases are at most 20% there (model cut-off 0.165; frequency-rule cut-off 0.140, chosen the same way).

## Headline

| Detector | Missed cases | False alarms | Accuracy |
|---|---|---|---|
| Always "no tremor" | 100.0% | 0.0% | 74.5% |
| Frequency rule | 14.8% | 59.0% | 52.3% |
| **Detector v1 (our model)** | **14.3%** | **27.0%** | **76.2%** |

## Moving vs still (model, with the frequency rule in brackets)

| Hand | Missed cases | False alarms |
|---|---|---|
| moving | 14.4% (17.0%) | 29.0% (58.9%) |
| still | 14.0% (10.4%) | 22.8% (59.2%) |

## Per group (judges check that it works equally well across groups)

Groups with fewer than 10 people are marked "few!": their numbers are unreliable.
Missed cases only exist for groups with tremor windows; healthy people and synthetic-only windows can only produce false alarms.

### By age band

| Group | Windows (tremor / no tremor) | People | Missed cases | False alarms |
|---|---|---|---|---|
| under 60 | 264 / 542 | 19 | 13.6% | 29.5% |
| 60-69 | 300 / 755 | 24 | 15.3% | 31.8% |
| 70 and over | 380 / 849 | 29 | 13.9% | 34.7% |

### By sex

| Group | Windows (tremor / no tremor) | People | Missed cases | False alarms |
|---|---|---|---|---|
| female | 396 / 841 | 28 | 10.9% | 30.0% |
| male | 548 / 1305 | 44 | 16.8% | 33.9% |

### By diagnosis

| Group | Windows (tremor / no tremor) | People | Missed cases | False alarms |
|---|---|---|---|---|
| Atypical Parkinsonism | 4 / 55 | 2 (few!) | 25.0% | 27.3% |
| Essential Tremor | 212 / 59 | 4 (few!) | 8.5% | 61.0% |
| Healthy | 0 / 660 | 12 | - | 27.6% |
| Multiple Sclerosis | 0 / 56 | 2 (few!) | - | 32.1% |
| Other Movement Disorders | 212 / 199 | 9 (few!) | 11.3% | 40.2% |
| Parkinson's | 516 / 1117 | 43 | 17.8% | 32.6% |
| none | 0 / 618 | 0 (few!) | - | 8.4% |

### By task type

| Group | Windows (tremor / no tremor) | People | Missed cases | False alarms |
|---|---|---|---|---|
| rest | 504 / 622 | 72 | 18.3% | 19.0% |
| postural | 380 / 719 | 70 | 10.3% | 31.6% |
| action | 60 / 805 | 70 | 6.7% | 43.5% |

### By source of the window

| Group | Windows (tremor / no tremor) | People | Missed cases | False alarms |
|---|---|---|---|---|
| tremor | 944 / 0 | 35 | 14.3% | - |
| patient, no tremor | 0 / 1486 | 60 | - | 34.5% |
| healthy | 0 / 660 | 12 | - | 27.6% |
| synthetic only | 0 / 618 | 0 (few!) | - | 8.4% |

### By tremor size (tremor windows only)

| Group | Windows (tremor / no tremor) | People | Missed cases | False alarms |
|---|---|---|---|---|
| mild (under 3 px) | 219 / 0 | 31 | 37.0% | - |
| medium (3-10 px) | 317 / 0 | 32 | 12.6% | - |
| strong (over 10 px) | 408 / 0 | 19 | 3.4% | - |

## Size estimate (tremor windows)

| Tremor size | Windows | Median error (px) | Median true size (px) |
|---|---|---|---|
| mild (under 3 px) | 219 | 0.52 | 1.77 |
| medium (3-10 px) | 317 | 1.18 | 5.39 |
| strong (over 10 px) | 408 | 1.76 | 20.04 |

## Does the pixel factor (DECISION 1) decide the result?

Everything rebuilt and retrained with every tremor at half and double size; cut-offs chosen on validation the same way.

| Pixel factor | Model: missed | Model: false alarms | Rule: missed | Rule: false alarms |
|---|---|---|---|---|
| x0.5 | 16.8% | 34.0% | 15.7% | 64.1% |
| x1 | 14.3% | 27.0% | 14.8% | 59.0% |
| x2 | 12.3% | 22.5% | 14.3% | 50.8% |

This project is a prototype and is not medical advice.
