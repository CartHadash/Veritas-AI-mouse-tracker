# The project explained in plain language

Every agent adds to this file after each step it finishes: **what this part does, why we
chose it, and how we know it works**, in words a classmate would understand. This is how
the team learns the project well enough to explain it to judges, which the rules require.

Keep entries short. Newest sections go at the bottom, in the order the project is built.
If something changes later, fix the old entry instead of adding a contradicting one.

## The idea

People with hand tremor find small on-screen targets hard to click, because the tremor
makes the pointer shake. Tremor is fast and rhythmic (about 3 to 12 back-and-forth
movements a second), while deliberate pointing is much slower. That difference in speed is
what lets a computer tell them apart.

We train two models. The **detector** looks at a couple of seconds of pointer movement and
says whether tremor-like shaking is present, and how strong. The **corrector** takes shaky
movement and outputs where the pointer was meant to be. An app shows the corrected cursor,
keeps a summary of the session, and has an assistant that explains the numbers.

## The toolbox (step 1)

**What it is.** A private folder of Python libraries for this project (`.venv`), and a list
of them (`requirements.txt`) with exact versions, so every laptop runs the same code the
same way. The main ones: NumPy and SciPy for maths and signal processing, scikit-learn for
the first detector, PyTorch for the neural-network corrector, FastAPI for the local web
server, and the Anthropic library for the assistant.

**Why.** If two laptops have different library versions, a model can train on one and
crash on the other. Pinning versions avoids that, which matters because we build on one
Mac and demo on another.

**The chip.** `models/device.py` picks where the maths runs: an NVIDIA graphics card if
there is one, else the Apple graphics chip (`mps`), else the normal processor. On the
builder's Mac it prints `mps` (from running `python models/device.py`). Our models are
small, so even the normal processor is fast enough.

**How we know it works.** `python -c "import numpy, pandas, scipy, sklearn, torch, fastapi, anthropic"`
exits with no error on the builder's Mac (Python 3.12.10).

## Where the data comes from

### Looking at the data first (step 2)

**What it does.** `data_pipeline/look_at_data.py` counts the people in the PADS dataset and
draws two known tremor recordings: the signal over time, a 3-second zoom, and its
**frequency spectrum**. A spectrum answers "how much of this movement repeats at each speed?";
a tremor is one tall, narrow peak between 3 and 12 repetitions per second (Hz).

**Why.** Before training anything we check the data is complete and really contains tremor.
If a file were missing or read wrongly, every later number would be wrong without us noticing.

**What we found** (output of `python data_pipeline/look_at_data.py`):

- PADS has 469 people: 276 Parkinson's, 79 healthy, 60 other movement disorders, 28 essential
  tremor, 15 atypical Parkinsonism, 11 multiple sclerosis.
- By age: 161 under 60, 149 aged 60-69, 159 aged 70 and over. By sex: 281 male, 188 female.
- PADS subject 060 (Parkinson's, right wrist, resting): a peak at 4.30 Hz, with 99% of the
  movement in the 3-12 Hz band.
- TremorDB recording `rofh/s6rof.let` (fingertip at rest, treatment off): a peak at 4.88 Hz,
  98% in 3-12 Hz, plus a smaller second peak near 10 Hz (an echo of the first, called a harmonic).

**How we know it works.** The counts and both peaks match the numbers published for these
datasets (written in `docs/DATASETS.md` before the hackathon). The charts are in
`evaluation/results/figures/`: the zoom shows a regular wave of about 4-5 beats per second.

Note: the PADS chart and spectrum use the one gyroscope axis with the most movement.

### The tremor library (step 3)

**What it does.** `data_pipeline/tremor_library.py` cuts every recording of both datasets
into 10.24-second pieces (13,764 in all), keeps only the shaking part (movement repeating 3
to 12 times per second, using a "band-pass filter" that removes slower and faster movement),
turns it into on-screen cursor movement in pixels, and marks each piece "tremor" or "no
tremor" with a fixed rule. It runs in about 30 seconds.

**From a wrist to a cursor.** PADS measures how fast the wrist rotates. Adding that up over
time gives the wrist's angle; of its three rotation directions we keep the two it moves most
in, as the cursor's x and y. TremorDB measures fingertip speed in one direction only, so the
second direction is the same recording 3 seconds later. Then one conversion factor per
dataset turns the movement into pixels. **This conversion is our assumption**: a wrist
sensor is not a mouse.

**The pixel factor (Decision 1, team chose A).** One factor per dataset, set so that the
typical (median) tremor-marked Parkinson's piece moves the cursor about 6 px from its centre
(root-mean-square). PADS: 594 px per radian of wrist rotation; TremorDB: 98.6 px per unit.
Because it is one factor, not one per person, strong tremor stays strong and weak stays weak:
tremor-marked pieces range from 1.5 to 34.3 px (10th to 90th percentile). Later we redo the
main results at half and double the factor to show the choice does not decide the outcome.

**The rule for "contains tremor"** (fixed on Saturday 14 Nov before any model existed; it is
never changed after seeing model results). A PADS piece is tremor-marked when both:
1. *strong enough*: its 3-12 Hz movement is bigger than in 95% of healthy people doing the
   same type of task (rest, holding a position, or moving on purpose);
2. *one clear rhythm*: at least half of its 3-12 Hz movement lies within 1 Hz of its
   strongest frequency. Real tremor is one steady beat; deliberate movement is spread out.

Why condition 1 compares with the same task type: when healthy people move their arm on
purpose, the movement also has a lot of 3-12 Hz content (we checked: as much as Parkinson's
patients). Comparing everyone with resting healthy people would have called deliberate
movement "tremor". TremorDB has no healthy people, so condition 1 becomes "at least half of
all movement is in 3-12 Hz", which works because those are resting recordings.

**Task types (Decision 2, team chose A).** All 11 PADS tasks are kept and labelled rest /
postural (holding a position) / action (moving on purpose).

**What we got** (output of `python data_pipeline/tremor_library.py`):

| Dataset | Diagnosis | Pieces | Tremor-marked | People with any | Seconds marked |
|---|---|---|---|---|---|
| PADS | Parkinson's | 7,728 | 635 | 156 | 6,502 |
| PADS | Essential tremor | 784 | 217 | 26 | 2,222 |
| PADS | Other movement disorders | 1,680 | 221 | 40 | 2,263 |
| PADS | Atypical Parkinsonism | 420 | 13 | 6 | 133 |
| PADS | Multiple sclerosis | 308 | 16 | 5 | 164 |
| PADS | Healthy | 2,212 | 61 | 33 | 625 |
| TremorDB | Parkinson's | 632 | 261 | 14 | 2,673 |

By task type (PADS): rest 528 of 3,752 marked, postural 490 of 4,690, action 145 of 4,690.

**Things to be honest about.**
- 61 healthy pieces pass the rule (expected: the threshold lets about 5% of healthy pieces
  through on strength). In the training data, healthy people are always "no tremor" anyway.
- Healthy people's leftover 3-12 Hz movement is usually tiny (median 1.2 px) but can reach
  9.2 px (90th percentile), mostly from deliberate arm movement. Those will be hard cases.
- The healthy thresholds were computed from all healthy people, including those who will
  later be test subjects. This defines the labels; it does not tune any model.
- TremorDB recordings used two different laser range settings (0.2 and 0.5), and the units
  are unreliable, so one factor may make some TremorDB subjects look bigger or smaller than
  they really were.

**How we know it works.** `evaluation/results/figures/tremor_library_examples.png` shows 8
random pieces on the same scale: the tremor-marked patients wave regularly with one sharp
spectrum peak (4.7-5.5 Hz), the healthy controls are nearly flat.

### Synthetic "intended" mouse movement (step 4)

**What it does.** `data_pipeline/synthetic_paths.py` makes up realistic clean mouse
movement: no tremor, just what a person *meant* to do. Step 5 adds real tremor on top, so
for every example we know both the shaky version and the clean answer.

**What is in it.** Reaches to targets 50-900 px away lasting 0.3-1.2 s, using the
"minimum-jerk" shape (the smooth speed-up-then-slow-down that real human pointing follows),
often slightly curved, and 60% of the time landing a little off target followed by a short
correction. Also pauses and slow drifts. Plus **tremor look-alikes** that are deliberate,
not tremor: back-and-forth wiggles (2-6 per second), fast small circles (1.5-4 per second)
and zig-zags. Wiggles overlap the tremor speed range on purpose: if the detector only
looked for "something rhythmic at 3-12 Hz" it would raise false alarms here, so this tests
whether it learns more than that. Finally a little sensor jitter (0-0.3 px).

Share of time over 500 generated paths (from `python data_pipeline/synthetic_paths.py`):
still 19.7%, reach 27.9%, correction 6.7%, drift 17.4%, wiggle 11.2%, circle 10.3%,
zigzag 6.8%. So about 28% of the time contains a look-alike.

**Why synthetic.** No public dataset of mouse movement from people with tremor exists, and
the rules forbid recording real people for training. Generated movement is our assumption,
and we say so: real people move in more varied ways than these six kinds of event.

**How we know it works.** `evaluation/results/figures/synthetic_paths_examples.png` shows six
paths and one speed curve: reaches are bell-shaped in speed, look-alikes are fast and jumpy.
A fixed random seed means the same paths come out every time.

### Training, validation and test sets (step 5)

**What it does.** `data_pipeline/build_dataset.py` puts every person into exactly one of
three groups, then builds labelled examples from their recordings.

**Split by person, not by recording.** If one patient's recordings were in both the
learning and the testing groups, the model could recognise *the person* instead of *the
tremor*, and the score would be fake. So people are split 70% train (learn from), 15%
validation (tune settings), 15% test (locked away for the final score), separately inside
each diagnosis group so every group appears in all three. Fixed random seed (42); the lists
are in `data_pipeline/split.json`. `data_pipeline/test_split.py` fails if anyone appears in
two groups or if an example uses a person from the wrong group (4 checks, all pass).

People: 484 = 469 PADS + 15 TremorDB (TremorDB's description lists 16, but subject v3 has
no recordings in the dataset). Train 340, validation 72, test 72.

**Detector examples** are 2.56-second windows (256 samples), each a freshly generated
synthetic movement plus either:
- a piece of a tremor-marked patient segment → label "tremor";
- a piece of a patient segment *not* marked as tremor → "no tremor";
- a piece of a healthy person's segment (their tiny natural tremor) → "no tremor";
- nothing (synthetic movement alone) → "no tremor".

| Split | Windows | Tremor | No tremor: patient / healthy / synthetic only |
|---|---|---|---|
| Train | 16,771 | 3,848 | 7,146 / 2,982 / 2,795 |
| Validation | 3,452 | 660 | 1,557 / 660 / 575 |
| Test | 3,708 | 944 | 1,486 / 660 / 618 |

About a quarter of the windows are "tremor", so a model that always says "no tremor" gets
about 75% accuracy while missing every case. That is why we report missed cases and false
alarms separately, never accuracy alone. The hand is mostly moving in about two thirds of
windows (11,367 / 2,313 / 2,519).

**Corrector examples** are 5.12-second sequences (512 samples): input = synthetic movement +
a tremor piece (or nothing), target = the clean synthetic movement. Train 4,207 (962 with
marked tremor), validation 809 (165), test 930 (236). The rest have small or no tremor,
because the corrector must also leave a steady hand alone.

**Small groups in the test set (be honest about this).** Test people: Parkinson's 43,
healthy 12, other movement disorders 9, essential tremor 4, atypical Parkinsonism 2,
multiple sclerosis 2; TremorDB 2. Age: 19 under 60, 24 aged 60-69, 29 aged 70+. Sex: 28
female, 44 male. Groups under about 10 people (essential tremor, atypical Parkinsonism, MS,
other movement disorders, TremorDB) give unreliable results; the write-up must say so.
Validation has no atypical-Parkinsonism tremor windows and test has no MS tremor windows.

Also: the 61 healthy segments that pass the tremor rule are left out entirely, so no
"no tremor" example contains rule-passing tremor. Each window's label comes from its whole
10.24-second segment; a short window from a segment with on-and-off tremor may contain
little tremor (a known source of noisy labels).

Numbers from `python data_pipeline/build_dataset.py` (17 s, about 0.45 GB memory).

## The baselines

A **baseline** is the simplest way to do the job. Judges want our model's score next to it,
to see how much the AI adds. `python evaluation/run_baselines.py` scores them all (about 4
minutes) and writes `evaluation/results/baselines.md`. All scoring code is in
`evaluation/metrics.py`, shared with our models so the comparison is fair. Settings and
cut-offs are chosen on **validation** people only; the numbers below are on **test** people.

### Detector baselines (test: 3,708 windows, 944 with tremor)

- **Always "no tremor"**: 74.5% accuracy, yet it misses 100% of tremor. This is why
  accuracy alone is misleading.
- **Frequency rule** ("tremor" when enough of the movement is at 3-12 Hz):
  - best balance: misses 47.2% of tremor windows, false alarms on 19.4% of the others;
  - forced to miss at most 10% on validation: misses 7.4% on test but false alarms jump
    to 72.9%.
  - Hand still vs moving (balanced): misses 35.2% vs 53.1%. Deliberate movement hides
    tremor from a simple frequency rule, as expected.

The rule is far from perfect even when the hand is still, so the task is not too easy.

### Corrector baselines (test: 236 sequences with marked tremor)

| Method | Off the intended path while moving / still (px) | Tremor removed | Lag |
|---|---|---|---|
| No filter | 12.5 / 12.8 | 0% | 0 ms |
| Lower sensitivity 1/2 (hand travels 2x) | 6.2 / 6.4 | 75% | 0 ms |
| Lower sensitivity 1/4 (hand travels 4x) | 3.0 / 3.3 | 94% | 0 ms |
| Moving average, original setting (0.2 s) | 34.8 / 3.4 | 91% | 100 ms |
| One Euro, original settings | 19.7 / 5.9 | 68% | 40 ms |
| Kalman, original settings | 17.8 / 9.1 | 66% | 20 ms |
| Moving average, tuned on validation | 21.9 / 8.1 | 54% | 50 ms |
| One Euro, tuned on validation | 13.2 / 10.4 | 15% | 10 ms |
| Kalman, tuned on validation | 15.0 / 14.8 | -36% | 0 ms |

**What this shows.** Classical filters face a trade-off they cannot escape. Heavy smoothing
removes most tremor while the hand is still (good for clicking) but makes the cursor trail
behind fast reaches by 20-100 ms, which puts it 20-35 px off. Tuned to stay close to the
path overall, they barely smooth at all (One Euro removes 15%), and Kalman even overshoots
and *adds* shake. Our idea: the detector switches smoothing on only when tremor is present,
and the learned corrector should remove tremor with less lag. Lower sensitivity looks
strong on paper, but the hand must travel 2-4 times as far, which is tiring.

**How we know the scoring works.** The lag measurement gives 50 ms for a 0.1 s moving
average and 100 ms for a 0.2 s one: exactly half the window, as theory says.

Note: the filters were tuned for the lowest average distance over the whole sequence, and
fast reaches dominate that average. That is why the tuned settings smooth so little.

## The detector

**What it does.** It looks at the last 2.56 seconds of cursor movement and says whether it
contains tremor-like shaking (a score from 0 to 1), how big the shaking is in pixels, and at
what frequency. It flags tremor-*like* movement; it does not diagnose anything.

**How it works (version 1, Decision 3 option A).** `models/detector/features.py` describes
each window with 19 numbers a person can explain: how much movement there is in each
frequency band, where the strongest 3-12 Hz rhythm is and how sharp and regular it is, how big
the 3-12 Hz shake is in pixels, speed, acceleration, direction reversals, and the share of
time the cursor is nearly still. `models/detector/train.py` feeds these to **gradient
boosting**: many small decision trees, each correcting the mistakes of the ones before, that
vote together. A second model of the same kind estimates the shake's size. Trained on train
people only (25 s on the builder's Mac); settings picked on validation people (average
precision 0.676, where random guessing gives 0.191). Saved model: 0.51 MB.

**Which measurements mattered** (shuffle one on validation and see how much worse the model
gets): by far "share of time nearly still", then peak sharpness, power at 7-12 Hz, median
speed and rhythm regularity. Honest caveat: our synthetic "still" hand is perfectly still
apart from tiny jitter, so any shaking while still stands out. A real hand resting on a real
mouse is probably less still, so real-world false alarms could be higher than measured here.

**The alarm cut-off (Decision 4, team chose B).** The cut-off is set on validation so that at
most 20% of tremor windows are missed (cut-off 0.165). The guide suggested 10%, but on
validation that meant 46.5% false alarms: a healthy person would see "tremor" about half the
time. At 20% the false alarms drop to about a quarter. The corrector's smoothing follows the
0-1 score smoothly, not this yes/no line, so the line mainly affects what we tell the user.

**Results on test people** (`python evaluation/evaluate_detector.py --missed-target 0.2`; used
once, after everything was chosen on validation):

| Detector | Missed cases | False alarms | Accuracy |
|---|---|---|---|
| Always "no tremor" | 100.0% | 0.0% | 74.5% |
| Frequency rule (cut-off chosen the same way) | 14.8% | 59.0% | 52.3% |
| **Our detector v1** | **14.3%** | **27.0%** | **76.2%** |

Same missed cases as the rule, less than half the false alarms. With the hand moving: 29.0%
false alarms vs the rule's 58.9%; with the hand still: 22.8% vs 59.2%.

**Across groups** (full tables in `evaluation/results/detector_v1.md`): missed cases by age
band 13.6% / 15.3% / 13.9% (under 60 / 60-69 / 70+), by sex 10.9% female / 16.8% male. False
alarms by age 29.5% / 31.8% / 34.7%, by sex 30.0% / 33.9% (these exclude the synthetic-only
windows, which have no person and only 8.4% false alarms, so they are higher than the 27.0%
overall). Essential tremor, atypical Parkinsonism, MS and other movement disorders have under
10 test people each, so their numbers are unreliable.

**Where it is weaker.** Mild tremor (under 3 px) is missed 37.0% of the time (medium 12.6%,
strong 3.4%). Windows from "moving on purpose" tasks get 43.5% false alarms (rest: 19.0%).
Patient windows that the rule did not mark as tremor get 34.5% false alarms; some of them
probably contain weaker tremor that the rule left unmarked.

**Size estimate.** Median error 0.52 px for mild tremor (true median 1.77 px), 1.18 px for
medium (5.39 px), 1.76 px for strong (20.04 px).

**Does our pixel factor decide the result? No.** Everything was rebuilt and retrained with
every tremor at half and at double size. Model missed / false alarms: 16.8% / 34.0% (half),
14.3% / 27.0% (normal), 12.3% / 22.5% (double); the frequency rule's false alarms were 64.1%,
59.0% and 50.8%. Bigger tremor is easier, as expected, and the model beats the rule at all three.

## The corrector

**What it does.** It takes shaky cursor movement and outputs where the cursor was *meant* to
be, live, sample by sample.

**How it works (version 1).** A small neural network (`models/corrector/model.py`, 10,722
weights, a 0.046 MB file). It sees the last 64 movement steps (0.64 s) and outputs an offset
that moves the raw cursor back onto the intended path. It uses three "1-D convolution"
layers: each looks at a few neighbouring time steps, with gaps that double from layer to
layer (1, 2, 4), so the last layer covers a wide stretch of the past. It is **causal**: it
only ever sees past and current samples. Trained to minimise the squared distance to the
clean path (`models/corrector/train.py`): 6,000 steps in 119 s on the builder's Mac (Apple
graphics chip, about 0.5 GB of memory). Validation people picked the best version (average
distance 3.02 px). Loss curve: `evaluation/results/figures/corrector_v1_loss.png`.

**The two models together ("gating").** The detector's 0-1 score becomes a gate: closed (raw
cursor, no correction) when the score is under 0.05, fully open at the Decision 4 cut-off,
blending in between, and changing smoothly over about 0.3 s. So a steady hand gets no
correction at all, and the cursor never jumps. `models/corrector/live.py` does this live.

**Results on test people** (`python evaluation/evaluate_corrector.py`; 236 test sequences with
marked tremor, 694 without; scored after the detector's 2.56 s warm-up, the same samples for
every method):

| Method | Off the path moving / still (px) | Tremor removed | Lag | Steady hand (px) |
|---|---|---|---|---|
| No filter | 13.2 / 12.7 | 0% | 0 ms | 2.30 |
| Lower sensitivity 1/2 (hand travels 2x) | 6.6 / 6.4 | 75% | 0 ms | 1.15 |
| One Euro, original settings | 19.7 / 5.9 | 68% | 40 ms | 12.95 |
| One Euro + our detector gate | 17.3 / 6.4 | 65% | 30 ms | 5.89 |
| Our corrector, always on | 6.7 / 5.2 | 89% | 0 ms | 2.43 |
| **Our corrector + detector gate** | **7.2 / 5.9** | **84%** | **0 ms** | **1.97** |

Our system removes 84% of the tremor with no measurable lag, roughly halves the distance to
the intended path while moving (13.2 -> 7.2 px), and does not harm a steady hand (1.97 px vs
2.30 with no filter). It beats One Euro, also when One Euro is switched by the same detector.
By tremor size it removes 1% of mild tremor (under 3 px), 49% of medium and 85% of strong.

**Why can it have no lag when classical filters cannot?** A smoothing filter averages the
past, so it always trails behind. Our network instead *predicts* the tremor: tremor is a
steady rhythm, so from the last 0.64 s it can estimate where the shake is right now and
subtract it.

**The honest limit.** The "intended" movement is synthetic and follows a smooth textbook
shape, which makes it easier to predict than real human movement. Real-world results will
probably be weaker. We cannot measure that without recording people, which the rules forbid.

**Speed.** `python models/corrector/time_live.py` on the builder's Mac: corrector alone 0.18
ms per update; with the detector gate mean 0.40 ms, worst 2.9 ms (the detector runs every
10th sample). Well under the 8 ms limit. A first measurement showed 21 ms spikes: scikit-learn
was starting parallel worker threads for every single window, so live calls now use one thread.

**How we know the scoring matches the live code.** Feeding test sequences through
`live.py` sample by sample gives the same positions as the offline scoring, to within 0.09 px.

## Where it fails

Full write-up: `evaluation/results/failures/failures.md` (charts in the same folder, made by
`python evaluation/find_failures.py` on test people). In short:

- **Missed tremor is mostly tiny.** 37.0% of mild tremor (under 3 px) is missed, but only 3.4%
  of strong tremor (over 10 px). The three most confident misses are 0.2-0.4 px: marked as
  tremor by the wrist sensor, but too small to visibly shake a cursor.
- **Many "false alarms" are probably real tremor our labelling rule left unmarked.** They
  cluster in action tasks (43.5% false alarms there, vs 19.0% for rest). For action tasks the
  rule compares with healthy people moving on purpose, a very high bar, so real tremor during
  action can end up labelled "no tremor". The most confident false alarm is a strong, regular
  5 Hz shake that looks exactly like tremor. We do not change the rule after seeing results;
  we report it. Deliberate look-alike movement also causes false alarms (33.4% when it fills
  more than 30% of the window, vs 21.6% otherwise).
- **Smooth continuous movement can trigger the detector.** Found while testing the server
  (step 10): a slow, perfectly smooth circle with no pauses scored just over the cut-off.
  The strongest feature is "share of time nearly still", and our synthetic movement almost
  always has pauses, so uninterrupted movement looks unusual to the model.
- **The corrector loses to One Euro on irregular shaking.** When the shaking is not a steady
  rhythm, the detector keeps the gate closed, so our system leaves it alone; One Euro smooths
  everything (and pays with 40 ms of lag everywhere else).

## The app

### The server (step 10)

**What it does.** `server/main.py` is a small Python program that runs on the user's own
laptop, keeps both models loaded, and talks to the web page. Start it with
`python -m uvicorn server.main:app` and open http://127.0.0.1:8000. It only listens on this
computer, never on the network.

**How the page and the server talk.** Through a **WebSocket**: a connection that stays open so
messages flow both ways quickly. The page sends every pointer position; the server replies
with the corrected position, the detector's tremor score, the estimated tremor size and
frequency. Measured with `python server/test_ws.py` on the builder's Mac: 500 samples in,
500 replies out in every filter mode; average reply time 0.56 ms with our model and demo
tremor on (99th percentile 2.92 ms). Far below what a person can notice.

**Decision 5 (team chose A):** the models run in Python on the server, not inside the
browser, so there is one copy of each model and the timing we measured is the timing users get.

**Filter modes:** none / lower sensitivity (cursor moves half as far) / One Euro / our model.
Strength 0-1 blends between the raw and the filtered cursor.

**Demo tremor.** None of us has a tremor, so a switch adds a real patient's recorded tremor on
top of the user's own live movement. It replays 8 tremor recordings (4.7-14.2 px, 3.5-9.8 Hz)
from **test** people only, saved in `server/demo_tremor.npz` (63 KB, made by
`data_pipeline/make_demo_tremor.py`), so the demo never shows tremor the models trained on.
The summary notes when demo mode was on.

**The session summary** (`GET /api/summary`, Contract 2): share of analysed time with
tremor-like movement, typical frequency and size, a per-minute breakdown, distance moved,
clicks and click accuracy, and a steadiness score (1 = no shaking, 0 = typical shaking of
10 px or more). It includes the detector's real test error rates (missed 14.3%, false alarms
27.0%), read from the file `evaluation/evaluate_detector.py` writes, never typed in by hand.

**Optional parts from the team leader.** If the whole-laptop tracker or the assistant is
missing or cannot load (the tracker is Mac-only), the server carries on and says so at
`GET /api/status`. The tracker only starts when the user switches tracking on.

### The live demo page (step 11)

**What it does.** `web/index.html`, `web/styles.css` and `web/app.js`: the page judges see at
http://127.0.0.1:8000. In the practice area the normal mouse pointer is hidden and two
cursors are drawn: a faint grey one (the raw movement: your hand, plus replayed tremor in demo
mode) and a solid dark one (the corrected cursor). Clicks count where the **corrected** cursor
is, and a table tallies hits, misses and time per target for each filter mode, so you can
feel and see the difference.

On the right: filter buttons (no filter / lower sensitivity / One Euro / our model), a
strength slider, the demo tremor switch (with the required banner "Demo mode: replaying
recorded tremor from a public dataset." and which test-set recording is playing), and the
live tremor meter (score bar with the cut-off marked, estimated frequency and size). The
whole-laptop tracking button appears only when the leader's tracker can run. The disclaimer
is in the footer.

**Decisions.** Style C, warm and friendly (Decision 6), with large text and 48 px tall buttons
so they are easy to hit with a shaky hand. Plain JavaScript with no build tools (Decision 7).
It uses the browser's "pointer events", which behave the same for a mouse and a trackpad.

**How we know it works.** Tested in the app's built-in browser on the builder's Mac: with demo
tremor on and a hand held nearly still, the meter showed "Tremor-like movement detected",
score 0.79, and 3.9 Hz, the same frequency as the replayed recording (an essential tremor
patient, 3.9 Hz). Clicks were tallied per mode and counted in the summary. The size estimate
showed 5.4 px while that recording's average size is 14.2 px over 10 s, so the size readout
can underestimate.

**Something we noticed while testing:** a perfectly smooth, slow circular movement without
any pauses scored 0.185, just over the cut-off (0.165), so the meter said "tremor". Our
synthetic training movement almost always contains pauses, so the detector learned that
uninterrupted movement is unusual. See "Where it fails".

## The pointer reader and the assistant

(To be written by the team leader's agent after steps B1 and B2.)
