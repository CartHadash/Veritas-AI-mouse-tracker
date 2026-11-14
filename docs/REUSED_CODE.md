# Code and research from before the hackathon

Rule 2 says all project work must happen during the weekend and that a pre-built project
cannot be extended. On 12–13 Nov 2026 our team ran a short feasibility test and researched
datasets. This file records exactly what from that period is in this repository, so the
write-up can disclose it honestly.

**Update (Sat 14 Nov, 21:20, team leader's decision): no pre-hackathon code is left.** The two
code files below were first reused and disclosed, then rewritten from scratch by the builder's
agent during the hackathon to remove any rule-2 risk. Only the dataset research is reused.

## Reused

| Item | Where | What it is | Why we think it is acceptable |
|---|---|---|---|
| Dataset research | `docs/DATASETS.md` | Formats, sampling rates, licences, citations, known problems | Research, which the rules explicitly allow before kickoff |

## Rewritten during the hackathon (Sat 14 Nov)

| File | What it does now | How we checked it |
|---|---|---|
| `scripts/download_data.py` | Fetches both datasets from PhysioNet's public mirror and checks every file's SHA-256 fingerprint; `--check` verifies what is on disk | `--check` on the builder's data: all 12,689 PADS and 123 TremorDB files correct; a fresh TremorDB download into an empty folder gave the same files |
| `baselines/classical_filters.py` | Moving average, One Euro and Kalman filters, written from their published descriptions | Re-ran every evaluation that uses them (see below) |

**What the rewrite changed in the results.** The Kalman filter gives exactly the same numbers.
The moving average differs slightly (a 0.2 s window now holds 20 samples, not 21). **The One
Euro filter differs noticeably**: the new version follows the authors' reference code
(github.com/casiez/OneEuroFilter: speed is measured from the previous *smoothed* position);
the old file did not, and made One Euro look smoother and laggier than the published filter
is. Every result that uses these filters was re-run, and `RESULTS.md` uses the new numbers.

## Not reused (deliberately left behind)

The feasibility prototype also contained a pygame click-test app, a simulated-tremor
generator, a "robot user" simulation, a results/chart script and an experimental macOS
system-wide mouse filter. **None of that code is in this repository and none of it may be
copied in.** Anything similar must be written fresh during the weekend.

## What the agent must do

- Do not copy any other file from the old repository (`mouse-tracking-model`) or from
  anyone's local copy of it.
- Keep the "Sources" section of the write-up consistent with this file. Suggested wording:

  > Before the hackathon we researched datasets and ran a short feasibility test. No code from
  > that test is in the project: everything, including the data download, the baseline
  > filters, all models, evaluation and the app, was written during the weekend.

## Lessons from the feasibility test (knowledge, not code)

These are things we learned, which is allowed to carry over:

- Mouse movement on the demo MacBook arrives at about 122 samples per second with regular
  timing, far more than needed for a 3–12 Hz tremor.
- Reading the cursor position by asking macOS where the pointer is works **without** any
  permission. Listening to mouse *events* (pynput) or *changing* the real cursor needs the
  Accessibility permission and was never proven to work for correction.
- Every smoothing filter trades tremor removal against lag. On a fake sine-wave tremor a
  0.2 s moving average removed about 84% of the shake with about 96 ms of lag; One Euro
  about 75% with about 61 ms; a constant-velocity Kalman filter about 47% with almost no
  lag but a visible overshoot on fast movements.
- A simulated "robot user" gave results that changed completely with small changes to its
  assumptions. Do not rely on a simulated user for headline numbers.
- A teammate's fair objection: simply lowering pointer sensitivity also shrinks tremor on
  screen. Any claim that our filter helps must be compared against that.
