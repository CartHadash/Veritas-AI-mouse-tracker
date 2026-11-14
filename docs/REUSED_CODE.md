# Code and research from before the hackathon

Rule 2 says all project work must happen during the weekend and that a pre-built project
cannot be extended. On 12–13 Nov 2026 our team ran a short feasibility test and researched
datasets. This file records exactly what from that period is in this repository, so the
write-up can disclose it honestly.

**The team leader decided to reuse the three items below and to disclose them.** This is a
judgement call under rule 2, not something the organisers have confirmed. If in doubt,
email contact@veritasai.com; if they say no, delete the two code files and have the agent
rewrite them (about 30 minutes of work each).

## Reused

| Item | Where | What it is | Why we think it is acceptable |
|---|---|---|---|
| Dataset download script | `scripts/download_data.py` | Downloads the two public datasets and checks their checksums | It only fetches public data; the rules allow browsing datasets beforehand |
| Classical filters | `baselines/classical_filters.py` | Moving average, One Euro and Kalman filters | Standard published algorithms, used only as the **baselines** our model must beat. They are not the project's AI |
| Dataset research | `docs/DATASETS.md` | Formats, sampling rates, licences, citations, known problems | Research, which the rules explicitly allow before kickoff |

Both code files carry a notice at the top saying they predate the hackathon.

## Not reused (deliberately left behind)

The feasibility prototype also contained a pygame click-test app, a simulated-tremor
generator, a "robot user" simulation, a results/chart script and an experimental macOS
system-wide mouse filter. **None of that code is in this repository and none of it may be
copied in.** Anything similar must be written fresh during the weekend.

## What the agent must do

- Do not copy any other file from the old repository (`mouse-tracking-model`) or from
  anyone's local copy of it.
- Do not edit the two reused files except to fix a real bug; if you do, note it here.
- Keep the "Sources" section of the write-up consistent with this file. Suggested wording:

  > Before the hackathon we researched datasets and ran a short feasibility test. Two small
  > files from that test are reused and marked in the code: the dataset download script and
  > three standard smoothing filters that serve as baselines. Everything else, including
  > all models, evaluation and the app, was built during the weekend.

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
