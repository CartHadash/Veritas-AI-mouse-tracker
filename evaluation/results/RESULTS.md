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
   detector) removed 88% of the tremor with no measurable delay, where the classic One Euro
   filter removed 49% and trailed the hand by 20 ms; in the app it is combined with One Euro
   smoothing, which leaves less visible shake than One Euro alone (2.56 vs 3.39 px) but lags
   behind a moving hand like One Euro does.
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
| Moving average 0.2 s | 32.44 / 3.29 | 91% | 90 ms | - |
| One Euro (original settings) | 15.32 / 6.98 | 49% | 20 ms | 0.98 |
| One Euro (tuned on validation) | 13.62 / 11.03 | 10% | 10 ms | - |
| One Euro + our detector switching it | 13.99 / 7.43 | 48% | 20 ms | - |
| Our corrector v1 | 7.15 / 5.93 | 84% | 0 ms | 2.09 |
| Our corrector v3 | 6.85 / 4.93 | 86% | 0 ms | 1.96 |
| Our corrector v4, penalty 0.5 (first choice) | 6.94 / 4.86 | 87% | 0 ms | 1.37 |
| Our corrector v4, penalty 2 (second choice) | 7.30 / 5.17 | 86% | 0 ms | 1.12 |
| **Our corrector v5, shake penalty 3 (the app's network)** | **7.32 / 4.29** | **88%** | **0 ms** | **1.27** |

Sources: `smoothness.md` (no filter, One Euro original, v1, v3, v4, jerkiness) and
`corrector_v1_gate_v2.md` (the other baselines; jerkiness was not measured for them). The
Kalman filter is only in `baselines.md`, scored on slightly different samples (after 0.5 s).
Jerkiness = average size of the change in cursor velocity from one 10 ms step to the next.
Penalty 2 replaced 0.5 after the team leader found the cursor still jittery by hand; it was
chosen on validation by a rule fixed in advance (`smoother_output.md`): smoother, no lag, 5%
further from the path while moving. v5 was then trained with an extra penalty on visible shake
(option B) and replaced it, chosen by a rule fixed before training on how the app looks with
its smoothing (`option_b.md`). This table scores the network alone; in the app it is smoothed
(see "On the demo page"). One Euro's numbers are from our rewritten filter, which follows the
authors' reference code (`docs/REUSED_CODE.md`).

On sequences without marked tremor (should be left alone): our v5 network is 1.83 px from the
intended path, no filter 2.30 px, One Euro 8.28 px. By tremor size (v3, `improvements.md`): 8% of mild,
50% of medium and 87% of strong tremor removed.

**Why no lag?** A smoothing filter averages the past, so it trails behind. Our network predicts
where the steady tremor rhythm is right now from the last 0.64 s and subtracts it.

## On the demo page (what judges see)

**What the app's "Our model" is now (Sun 15 Nov):** the corrector network (v5), plus One Euro
smoothing of its output, both switched on only as much as our detector says tremor is present
(a steady hand is left exactly as it is). The team found the network alone looked jittery by
eye; measuring what the eye sees confirmed it (below), so the smoothing was added.

**As a person sees it** (`vs_one_euro_test.md`, `python evaluation/vs_one_euro.py --people test`):
the demo page's own code, browser-like timing, test people's replayed tremor, averaged over
mild/medium/strong tremor and reaching/gliding/still. Shake = leftover 3-12 Hz wobble (RMS);
jerk = change in velocity per 10 ms step; distance = from the intended path (all px).

| Method | Distance | Shake | Jerk |
|---|---|---|---|
| No filter | 6.60 | 7.91 | 1.00 |
| One Euro | 5.23 | 3.39 | 0.30 |
| Our network alone | 3.64 | 4.01 | 0.79 |
| **Our model (network + gated One Euro; the app)** | **5.22** | **2.56** | **0.24** |

The app's cursor shakes least and is least jumpy, and stays closer to the intended path than
One Euro; the network alone is closest to the path but nearly as jumpy as no filter.

**Still vs reaching** (`demo_modes_test.md`, `python evaluation/compare_modes.py --people test`;
distance from the intended path, no filter / One Euro / the app, px):

| Replayed tremor | Hand still | Reaching |
|---|---|---|
| Strong | 13.12 / 4.16 / 0.97 (93% closer than no filter) | 13.12 / 9.87 / 9.74 (26% closer) |
| Medium | 6.08 / 1.62 / 1.09 (82% closer) | 6.08 / 7.77 / 7.38 (21% further) |
| Mild | 1.55 / 0.29 / 0.43 (73% closer) | 1.55 / 7.04 / 6.53 (320% further) |

**Honest weakness:** the smoothing lags behind a moving hand like One Euro does, so while
reaching with mild or medium tremor the app's cursor is further from the path than no filter
(the network alone has no lag, but looked jittery). The detector switches the correction on for
mild tremor too, so mild tremor while moving is the worst case.

## Click freeze (simulation)

A click needs press and release on the target; tremor while the button is held can carry the
cursor off. "Click freeze" holds the shown cursor still from press to release (at most 0.3 s).
Simulated clicks (perfect aim, held 80-200 ms) on a 10 px target with strong replayed tremor of
test people: no filter 24% land, 39% with freeze; our model (the app) 99%, 99% with freeze;
One Euro 88%, 92% (`click_freeze_test.md`, `python evaluation/click_sim.py --people test`).

## Where it fails

Full write-up with charts: `failures/failures.md`. In short (`failures/failure_facts.md`):
- Missed tremor is mostly tiny (34.2% of tremor under 3 px is missed, 2.9% over 10 px) or a
  short burst at the end of a window.
- Many false alarms come from "moving on purpose" tasks (41.7%, vs 19.5% at rest), where our
  fixed labelling rule probably left real tremor unmarked; the most confident false alarm is a
  strong, regular 5 Hz shake.
- The corrector loses to One Euro on irregular shaking that the detector correctly does not call
  tremor, so the correction stays off.
- On real marked tremor, 12 of 236 test sequences end up further from the path than with no
  filter (6 of 47 mild, 6 of 88 medium, 0 of 101 strong): during a fast deliberate movement
  the corrector can subtract a large wrong offset (`failures/extras.md`, charts
  `corrector_worse_tremor_1.png` and `_2.png`).

## How sure are these numbers? (step 9)

Redrawing the 72 test people at random with repeats, 1000 times (a "bootstrap"), gives the
range that holds 95% of the results (`failures/extras.md`, `python evaluation/failure_extras.py`):

| Number | Test result | 95% range |
|---|---|---|
| Detector: missed tremor windows | 12.9% | 9.7% to 18.4% |
| Detector: false alarms | 27.1% | 24.7% to 29.5% |
| Corrector, marked tremor: tremor removed | 88% | 78% to 91% |

The missed-cases range is wide because few test people have tremor. Missed windows are
concentrated (8 people cause half of them); false alarms are spread out (25 people cause half).

## Best charts

1. `figures/tremor_library_examples.png`: real tremor pieces vs healthy people, same scale.
2. `failures/detector_false_alarm_1.png`: a "false alarm" that looks exactly like tremor.
3. `figures/pads_060_relaxed_right.png`: one patient's resting tremor and its sharp frequency peak.

## Clicking real buttons with the system-wide corrector (simulated)

`systemwide_clicks_test.md` (test people's replayed tremor, strong; the hand reaches, stops on
the button, then clicks; 80 clicks per row). Clicks landing on a 10 px button without / with
click freeze: no filter 30% / 46%, One Euro 90% / 95%, our model (Steadiest) 99% / 99%. On
validation people (`systemwide_clicks_val.md`) Steadiest landed the most clicks (91% with
freeze; Balanced 88%, Faster 82%), so it stays the default. Limits: perfect aim, no jolt from
pressing the button, and no person steering by a trailing cursor; on the demo Mac the team
leader still found real buttons hard to click.

"Click where you aimed" (added after that hand check): at the press, the click is placed at
the average of where the cursor was shown over the last 0.1 s, only while tremor is being
corrected. The window was chosen on validation people (`systemwide_clicks_val.md`: clicks
landing on the 10 px button with strong tremor and click freeze went from 91% to 95%; 0.2 s
and 0.3 s gave the same 95%, so the shortest was taken). Test people, scored once: 99% without
it, 100% with it; medium tremor and no tremor unchanged.

## What we tried that did not work

- A movement-aware detector, cheap version (`moving_cutoffs.md`, validation): one cut-off for
  windows that look like a moving hand and one for windows that look still, each chosen by the
  usual rule. The two came out almost the same as the single cut-off (0.152 and 0.157 against
  0.155), and false alarms with the hand truly moving went from 30.3% to 31.1%, so it was not
  kept and test people were not scored. The detector already misses about the same share in
  both groups, so a cut-off alone cannot lower false alarms while moving without missing more
  tremor; that would need retraining.

- Corrector v2, trained on tremor 0.5x to 2x as large (for different mouse settings): no real
  difference on validation, so not kept (`improvements.md`). Corrector v1 already copes with
  that range.
- Smoothness penalties: the first rule (`smoothness.md`) chose the weakest penalty (0.5) that
  is no jerkier than no filter; by hand it still looked jittery, so a second rule
  (`smoother_output.md`) chose penalty 2. Extra smoothing layers (One Euro or a short average
  on our output) made the cursor smoother still but further from the path while moving, so
  that rule rejected them. By eye the network alone still looked jittery, and measuring shake
  and jumpiness (`vs_one_euro_val.md`) showed why, so the app now adds gated One Euro smoothing
  (see "On the demo page"). Lesson: we first chose by distance from the path, which hid jitter.
- Less lag by retuning that smoothing (`tune_lag.md`, validation): every setting with less lag
  shook more (lag 67 -> 52 ms raised shake 2.98 -> 3.18 px and jerk 0.21 -> 0.25), beyond the limit fixed in
  advance, so the settings were kept. Steadiness and lag are a trade-off here, so the page now
  lets the person choose (`response_levels.md`, test people): Steadiest (default) 72 ms lag,
  shake 2.56 px; Balanced 47 ms, 2.87 px; Faster 30 ms, 3.38 px.
- Our pre-hackathon One Euro filter did not follow the published algorithm and made One Euro
  look smoother and laggier than it is; the rewritten one follows the authors' reference code.
- Detector v1 treated movement that never pauses as tremor (45.3% false alarms on pause-free
  movement); fixed in v2 (20.4%).
- Corrector v1 learned mostly from strong tremor and made mild tremor slightly worse on
  validation; v3 fixed that by changing its training goal.
- Our first demo looked weak and jumpy because of bugs in the live pipeline (a drifting 10 ms
  clock, replayed tremor skipping samples, a staircase at browser rates); found by testing the
  live path and a code review, and fixed. Offline scores could not see them.
- For a perfectly still hand, a classic filter (One Euro) beat our network alone; with the
  app's smoothing, ours is now closer (medium tremor 1.09 vs 1.62 px, strong 0.97 vs 4.16 px,
  `demo_modes_test.md`).
- A 10 s calibration test that picks the filter for each person (Godson's idea): with the
  network alone it did worse than always using our model, so the page's test only reports.
  Re-run with the app's smoothed model (`calibration_val.md`, normal size): always our model
  4.83 px off the path in later use, the test's choice 3.61 px, the best possible 2.46 px, so
  per-person choice would now help; not switched on (no time to re-test it properly). The page's
  test now only reports each filter's distance; it never switches the filter.

## Limits to say out loud

- No mouse data from people with tremor exists publicly: our tremor is real (wrist and
  fingertip sensors), the mouse movement is computer-generated, and the conversion to pixels
  is our assumption. Real-world results will probably be weaker.
- No person with tremor has tried it.
- Robustness check (step 4): on more realistic computer-generated movement (curves, uneven
  speed, whole pixels, uneven timing), validation results did not drop: detector missed /
  false alarms 18.0% / 25.6% (original movement 20.0% / 27.3%); the corrector's advantage
  over no filter while moving 5.45 px (original 5.08 px) (`realism_stress.md`).
- Reproducibility: a fresh copy on the team leader's Mac rebuilt everything; the detector
  reproduced exactly, while retraining the corrector there gives slightly different numbers
  with the same conclusions (training is not bit-identical across machines).
- Several diagnosis groups have under 10 test people.
- It flags tremor-like movement; it does not diagnose anything.
