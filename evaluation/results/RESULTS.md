# Results package (for the write-up)

Every number here is copied from a file a script generated; the source is named under each
table. `python evaluation/check_results.py` fails if a number in this file cannot be found in
those generated files. All results are on **test people**, who were never used for training or
for choosing any setting, unless a table says "validation".

**This project is a prototype and is not medical advice.**

## In 30 seconds (five plain sentences)

1. We built a tremor-aware pointer assistant for a person with Parkinson's or essential tremor
   who uses a laptop at home: it flags tremor-like cursor movement and shows a steadier cursor.
2. Our detector (a gradient-boosting model reading 19 explainable measurements of the last
   2.56 seconds) missed 12.9% of tremor windows with 27.1% false alarms on people it had never
   seen, where a simple frequency rule set to the same standard raised 59.0% false alarms.
3. Our corrector (a small neural network that only uses past movement, switched on by the
   detector) removed 87% of the tremor with no measurable delay, where the classic One Euro
   filter removed 68% and trailed the hand by 40 ms.
4. No public recordings of mouse movement from people with tremor exist, so we added real wrist
   and fingertip tremor from two public datasets (484 people) to computer-generated mouse
   movement, and split the data by person so test people never appeared in training.
5. It works best on strong tremor and mostly misses tremor too small to shake a cursor; it has
   not been tested by a person with tremor, and it does not diagnose anything.

## Who it is for

A person with Parkinson's disease or essential tremor who uses a laptop at home and finds
small targets hard to click because the pointer shakes. The assistant runs on their own
laptop; nothing leaves it.

## Data

| Fact | Value |
|---|---|
| People with recordings | 484 (PADS 469, TremorDB 15) |
| Split by person (seed 42) | train 340, validation 72, test 72 |
| Tremor library | 13764 segments of 10.24 s, 1424 tremor-marked |
| Tremor-marked size on screen | median 6.2 px (10th-90th percentile 1.5-34.3 px) |
| Detector windows (2.56 s): train / validation / test | 16771 / 3452 / 3708 (tremor: 3848 / 660 / 944) |
| Corrector sequences (5.12 s): train / validation / test | 4207 / 809 / 930 (marked tremor: 962 / 165 / 236) |

Source: `dataset_facts.md` (`python evaluation/data_facts.py`).

**How the data was built and cleaned** (details in `docs/EXPLAINED.md`): every recording was cut
into 10.24 s pieces; only the 3-12 Hz shaking was kept (band-pass filter) and turned into
on-screen movement in pixels with one conversion factor per dataset (594.0 px per radian for
PADS, 98.6 px per unit for TremorDB); each piece was labelled "tremor" or not by a rule fixed
before any model was trained; healthy pieces that passed the rule were left out. Each example
= computer-generated mouse movement + a real tremor piece (or none).

**Test people by group:** age under 60: 19, 60-69: 24, 70 and over: 29; female 28, male 44;
Parkinson's 43, healthy 12, other movement disorders 9, essential tremor 4, atypical
Parkinsonism 2, multiple sclerosis 2. Groups under 10 people give unreliable results.

## Detector: is there tremor-like movement in the last 2.56 s?

| Detector | Missed cases | False alarms | Accuracy |
|---|---|---|---|
| Always "no tremor" | 100.0% | 0.0% | 74.5% |
| Frequency rule (cut-off chosen like ours) | 14.8% | 59.0% | 52.3% |
| Detector v1 | 14.3% | 27.0% | 76.2% |
| **Detector v2 (the app)** | **12.9%** | **27.1%** | **76.5%** |

Source: `detector_v2.md`, `detector_v1.md`. Cut-off chosen on validation people so that at most
20% of tremor windows are missed there (Decision 4). Accuracy alone is misleading: "always no
tremor" scores 74.5% while missing every case.

Hand moving / still (v2): missed 12.6% / 14.0%, false alarms 29.6% / 18.0% (frequency rule:
false alarms 58.6% / 60.3%). On pause-free movement, v2 raised 20.4% false alarms where v1
raised 45.3% (`improvements.md`).

**Per group (detector v2):**

| Group | Test people | Missed cases | False alarms |
|---|---|---|---|
| Age under 60 | 19 | 12.9% | 30.3% |
| Age 60-69 | 24 | 12.7% | 29.9% |
| Age 70 and over | 29 | 13.2% | 35.1% |
| Female | 28 | 10.4% | 31.6% |
| Male | 44 | 14.8% | 32.3% |
| Parkinson's | 43 | 16.1% | 31.6% |
| Healthy | 12 | - | 27.3% |
| Other movement disorders | 9 (few) | 10.4% | 43.7% |
| Essential tremor | 4 (few) | 7.5% | 62.7% |
| Atypical Parkinsonism | 2 (few) | 25.0% | 23.6% |
| Multiple sclerosis | 2 (few) | - | 32.1% |

Source: `detector_v2.md`. Age bands and sexes are close. (Per-group false alarms are higher
than the 27.1% overall because the windows with no person, synthetic movement only, have just
10.0% false alarms.) By tremor size: missed 34.2% of mild (under 3 px), 11.0% of medium, 2.9%
of strong (over 10 px).

**Does our pixel conversion decide the result?** No. With every tremor at half and double size
(detector v1, rebuilt and retrained): missed / false alarms 16.8% / 34.0% (half), 14.3% / 27.0%
(normal), 12.3% / 22.5% (double); the frequency rule's false alarms were 64.1%, 59.0%, 50.8%.
Source: `detector_v1.md`.

## Corrector: how steady is the corrected cursor?

Test sequences with marked tremor: 236 (scored after the first 2.56 s, the same samples for
every method; the correction is switched on and off by detector v2, as in the app).

| Method | Off the intended path, moving / still (px) | Tremor removed | Lag | Jerkiness (px) |
|---|---|---|---|---|
| No filter | 13.17 / 12.74 | 0% | 0 ms | 1.69 |
| Lower sensitivity x0.5 (hand must travel 2x as far) | 6.59 / 6.40 | 75% | 0 ms | - |
| Moving average 0.2 s | 32.86 / 3.27 | 92% | 100 ms | - |
| One Euro (original settings) | 19.66 / 5.92 | 68% | 40 ms | 0.64 |
| One Euro (tuned on validation) | 13.78 / 10.43 | 15% | 10 ms | - |
| One Euro + our detector switching it | 17.21 / 6.41 | 65% | 30 ms | - |
| Our corrector v1 | 7.15 / 5.93 | 84% | 0 ms | 2.09 |
| Our corrector v3 | 6.85 / 4.93 | 86% | 0 ms | 1.96 |
| **Our corrector v4 (the app)** | **6.94 / 4.86** | **87%** | **0 ms** | **1.37** |

Sources: `smoothness.md` (no filter, One Euro original, v1, v3, v4, jerkiness) and
`corrector_v1_gate_v2.md` (the other baselines; jerkiness was not measured for them). The
Kalman filter is only in `baselines.md`, scored on slightly different samples (after 0.5 s).
Jerkiness = average size of the change in cursor velocity from one 10 ms step to the next.

On sequences without marked tremor (should be left alone): our v4 is 1.85 px from the intended
path, no filter 2.30 px, One Euro 12.95 px. By tremor size (v3, `improvements.md`): 8% of mild,
50% of medium and 87% of strong tremor removed.

**Why no lag?** A smoothing filter averages the past, so it trails behind. Our network predicts
where the steady tremor rhythm is right now from the last 0.64 s and subtracts it.

## On the demo page (what judges see)

Replayed tremor of test people, through the server's own code; our cursor compared with no
filter (`demo_modes_test.md`, `python evaluation/compare_modes.py --people test`):

| Replayed tremor | Closer to the intended path: hand still / reaching | Jerkiness, no filter -> ours: still / reaching (px) |
|---|---|---|
| Strong | 69% / 53% | 1.82 -> 1.29 / 1.94 -> 1.56 |
| Medium | 39% / 23% | 0.91 -> 0.71 / 1.10 -> 1.01 |
| Mild | 53% / 6% | 0.30 -> 0.17 / 0.60 -> 0.59 |

Honest weakness: for a hand held perfectly still, One Euro is closer (medium tremor 1.44 vs
3.70 px); our advantage is during movement (reaching with medium tremor: One Euro 11.76 px off
the path, ours 4.65 px).

## Click freeze (simulation)

A click needs press and release on the target; tremor while the button is held can carry the
cursor off. "Click freeze" holds the shown cursor still from press to release (at most 0.3 s).
Simulated clicks (perfect aim, held 80-200 ms) on a 10 px target with strong replayed tremor of
test people: no filter 24% land, 39% with freeze; our model 92%, 94% with freeze
(`click_freeze_test.md`, `python evaluation/click_sim.py --people test`).

## Where it fails

Full write-up with charts: `failures/failures.md`. In short (`failures/failure_facts.md`):
- Missed tremor is mostly tiny (34.2% of tremor under 3 px is missed, 2.9% over 10 px) or a
  short burst at the end of a window.
- Many false alarms come from "moving on purpose" tasks (41.7%, vs 19.5% at rest), where our
  fixed labelling rule probably left real tremor unmarked; the most confident false alarm is a
  strong, regular 5 Hz shake.
- The corrector loses to One Euro on irregular shaking that the detector correctly does not call
  tremor, so the correction stays off.

## Best charts

1. `figures/tremor_library_examples.png`: real tremor pieces vs healthy people, same scale.
2. `failures/detector_false_alarm_1.png`: a "false alarm" that looks exactly like tremor.
3. `figures/pads_060_relaxed_right.png`: one patient's resting tremor and its sharp frequency peak.

## What we tried that did not work

- Corrector v2, trained on tremor 0.5x to 2x as large (for different mouse settings): no real
  difference on validation, so not kept (`improvements.md`). Corrector v1 already copes with
  that range.
- Stronger smoothness penalties (v4 with 2 and 8): smoother but less accurate; the rule fixed
  in advance chose the weakest penalty that is no jerkier than no filter (`smoothness.md`).
- Detector v1 treated movement that never pauses as tremor (45.3% false alarms on pause-free
  movement); fixed in v2 (20.4%).
- Corrector v1 learned mostly from strong tremor and made mild tremor slightly worse on
  validation; v3 fixed that by changing its training goal.
- Our first demo looked weak and jumpy because of bugs in the live pipeline (a drifting 10 ms
  clock, replayed tremor skipping samples, a staircase at browser rates); found by testing the
  live path and a code review, and fixed. Offline scores could not see them.
- For a perfectly still hand, a classic filter (One Euro) still beats our model.
- A 10 s calibration test that picks the filter for each person (Godson's idea): on validation
  people it did worse than always using our model (2.37 px off the path in later use; the
  test's choice 3.15 px; the best possible choice 2.30 px, `calibration_val.md`). The page's
  test now only reports each filter's distance; it never switches the filter.

## Limits to say out loud

- No mouse data from people with tremor exists publicly: our tremor is real (wrist and
  fingertip sensors), the mouse movement is computer-generated, and the conversion to pixels
  is our assumption. Real-world results will probably be weaker.
- No person with tremor has tried it.
- Several diagnosis groups have under 10 test people.
- It flags tremor-like movement; it does not diagnose anything.
