# Dataset facts

Produced by `python evaluation/data_facts.py` from the built data.

## People

- People with recordings: 484 (PADS 469, TremorDB 15).
- Split by person (seed 42): train 340, val 72, test 72.
- Test people by diagnosis: Atypical Parkinsonism 2, Essential Tremor 4, Healthy 12, Multiple Sclerosis 2, Other Movement Disorders 9, Parkinson's 43.
- Test people by age band: 60-69 24, 70 and over 29, under 60 19.
- Test people by sex: female 28, male 44.

## Tremor library (10.24 s segments)

- Segments: 13764; tremor-marked: 1424.
- Tremor-marked segments by diagnosis: Atypical Parkinsonism (PADS) 13, Essential Tremor (PADS) 217, Healthy (PADS) 61, Multiple Sclerosis (PADS) 16, Other Movement Disorders (PADS) 221, Parkinson's (PADS) 635, Parkinson's (TremorDB) 261.
- Pixel factor: PADS 594.0 px per radian; TremorDB 98.6 px per unit.
- On-screen size of tremor-marked segments: median 6.2 px, 10th-90th percentile 1.5-34.3 px.

## Examples per split

| Split | Detector windows (2.56 s) | of which tremor | Pause-free windows (step 12) | Corrector sequences (5.12 s) | of which marked tremor |
|---|---|---|---|---|---|
| train | 16771 | 3848 | 16771 | 4207 | 962 |
| val | 3452 | 660 | 3452 | 809 | 165 |
| test | 3708 | 944 | 3708 | 930 | 236 |

## Demo page recordings (test people only)

- 12 recordings: medium 4, mild 4, strong 4.

This project is a prototype and is not medical advice.
