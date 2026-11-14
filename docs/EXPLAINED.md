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
