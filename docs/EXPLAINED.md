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

## The baselines

(To be written after step 6.)

## The detector

(To be written after step 7.)

## The corrector

(To be written after step 8.)

## Where it fails

(To be written after step 9.)

## The app

(To be written after steps 10-13.)

## The pointer reader and the assistant

(To be written by the team leader's agent after steps B1 and B2.)
