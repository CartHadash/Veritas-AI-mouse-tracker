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

(To be written by the builder's agent after steps 2-5.)

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
