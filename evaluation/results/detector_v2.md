# Detector v2: results on TEST people

Produced by `python evaluation/evaluate_detector.py --missed-target 0.2 --version v2`. Test people (3708 windows: 944 tremor, 2764 no tremor) were used once, after every setting was chosen on validation.

DECISION 4: cut-off chosen on validation so that missed cases are at most 20% there (model cut-off 0.155; frequency-rule cut-off 0.140, chosen the same way).

## Headline

| Detector | Missed cases | False alarms | Accuracy |
|---|---|---|---|
| Always "no tremor" | 100.0% | 0.0% | 74.5% |
| Frequency rule | 14.8% | 59.0% | 52.3% |
| **Detector v2 (our model)** | **12.9%** | **27.1%** | **76.5%** |

## Moving vs still (model, with the frequency rule in brackets)

| Hand | Missed cases | False alarms |
|---|---|---|
| moving | 12.6% (15.2%) | 29.6% (58.6%) |
| still | 14.0% (13.6%) | 18.0% (60.3%) |

## Per group (judges check that it works equally well across groups)

Groups with fewer than 10 people are marked "few!": their numbers are unreliable.
Missed cases only exist for groups with tremor windows; healthy people and synthetic-only windows can only produce false alarms.

### By age band

| Group | Windows (tremor / no tremor) | People | Missed cases | False alarms |
|---|---|---|---|---|
| under 60 | 264 / 542 | 19 | 12.9% | 30.3% |
| 60-69 | 300 / 755 | 24 | 12.7% | 29.9% |
| 70 and over | 380 / 849 | 29 | 13.2% | 35.1% |

### By sex

| Group | Windows (tremor / no tremor) | People | Missed cases | False alarms |
|---|---|---|---|---|
| female | 396 / 841 | 28 | 10.4% | 31.6% |
| male | 548 / 1305 | 44 | 14.8% | 32.3% |

### By diagnosis

| Group | Windows (tremor / no tremor) | People | Missed cases | False alarms |
|---|---|---|---|---|
| Atypical Parkinsonism | 4 / 55 | 2 (few!) | 25.0% | 23.6% |
| Essential Tremor | 212 / 59 | 4 (few!) | 7.5% | 62.7% |
| Healthy | 0 / 660 | 12 | - | 27.3% |
| Multiple Sclerosis | 0 / 56 | 2 (few!) | - | 32.1% |
| Other Movement Disorders | 212 / 199 | 9 (few!) | 10.4% | 43.7% |
| Parkinson's | 516 / 1117 | 43 | 16.1% | 31.6% |
| none | 0 / 618 | 0 (few!) | - | 10.0% |

### By task type

| Group | Windows (tremor / no tremor) | People | Missed cases | False alarms |
|---|---|---|---|---|
| rest | 504 / 622 | 72 | 15.9% | 19.5% |
| postural | 380 / 719 | 70 | 10.3% | 32.1% |
| action | 60 / 805 | 70 | 5.0% | 41.7% |

### By source of the window

| Group | Windows (tremor / no tremor) | People | Missed cases | False alarms |
|---|---|---|---|---|
| tremor | 944 / 0 | 35 | 12.9% | - |
| patient, no tremor | 0 / 1486 | 60 | - | 34.2% |
| healthy | 0 / 660 | 12 | - | 27.3% |
| synthetic only | 0 / 618 | 0 (few!) | - | 10.0% |

### By tremor size (tremor windows only)

| Group | Windows (tremor / no tremor) | People | Missed cases | False alarms |
|---|---|---|---|---|
| mild (under 3 px) | 219 / 0 | 31 | 34.2% | - |
| medium (3-10 px) | 317 / 0 | 32 | 11.0% | - |
| strong (over 10 px) | 408 / 0 | 19 | 2.9% | - |

## Size estimate (tremor windows)

| Tremor size | Windows | Median error (px) | Median true size (px) |
|---|---|---|---|
| mild (under 3 px) | 219 | 0.49 | 1.77 |
| medium (3-10 px) | 317 | 1.09 | 5.39 |
| strong (over 10 px) | 408 | 1.40 | 20.04 |

## Does the pixel factor (DECISION 1) decide the result?

Everything rebuilt and retrained with every tremor at half and double size; cut-offs chosen on validation the same way.

| Pixel factor | Model: missed | Model: false alarms | Rule: missed | Rule: false alarms |
|---|---|---|---|---|
| x0.5 | not trained for this version | | | |
| x1 | 12.9% | 27.1% | 14.8% | 59.0% |
| x2 | not trained for this version | | | |

This project is a prototype and is not medical advice.
