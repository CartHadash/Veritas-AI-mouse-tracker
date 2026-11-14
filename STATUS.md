# STATUS: where the project stands right now

**Every agent updates this file at the end of every work session** (rules in `CLAUDE.md`).
The writer builds the write-up from it, and teammates read it instead of asking.
Newest entries go at the top of each list. Use local time and say who you are.

## Right now

| Lane | Working on | Branch | Blocked by |
|---|---|---|---|
| Builder | IN PROGRESS: step 9, failure analysis (evaluation/). Steps 1-8 done (8 awaits Mac check) | builder/failures | - |
| Team leader | not started | - | - |
| Writer | not started | - | - |

## Done (newest first)

- Sat 14 Nov 15:00 CET, builder's agent: step 8, corrector v1 (`models/corrector/`), trained in
  119 s on the builder's Mac; scored once on test with `evaluation/evaluate_corrector.py` ->
  `evaluation/results/corrector_v1.md`. Detector live calls now use one thread (20 ms -> 2 ms).

- Sat 14 Nov 14:45 CET, builder's agent: step 7, detector v1 (`models/detector/`), scored once
  on test with `evaluation/evaluate_detector.py --missed-target 0.2` ->
  `evaluation/results/detector_v1.md`. Live use via `models/detector/predict.py`.

- Sat 14 Nov 14:40 CET, builder's agent: step 6, `evaluation/metrics.py` (shared scoring) and
  `evaluation/run_baselines.py` -> `evaluation/results/baselines.md`.

- Sat 14 Nov 14:30 CET, builder's agent: step 5, `data_pipeline/build_dataset.py` splits 484
  people by person (340 / 72 / 72, seed 42, `data_pipeline/split.json`) and builds detector
  windows and corrector sequences; `python -m pytest data_pipeline/test_split.py` passes (4).

- Sat 14 Nov 14:25 CET, builder's agent: step 4, `data_pipeline/synthetic_paths.py` generates
  clean mouse paths with reaches, corrections, pauses, drifts and tremor look-alikes
  (wiggles, circles, zig-zags; about 28% of the time). Chart in `evaluation/results/figures/`.

- Sat 14 Nov 14:20 CET, builder's agent: step 3, `data_pipeline/tremor_library.py` builds
  `data/derived/tremor_library.npz` (13,764 segments of 10.24 s) in about 30 s, peak memory
  about 0.5 GB on the builder's 8 GB Mac. Step 1 ticked in the guide after the leader's check.

- Sat 14 Nov, team leader's agent: **first cross-machine check PASSED on the demo Mac**
  (Apple Silicon, macOS 26, Python 3.12.16, fresh `.venv`). `pip install -r
  requirements.txt` installed all pinned versions with no errors and `pip check` reports
  no broken requirements. `python -c "import numpy, pandas, scipy, sklearn, torch, fastapi,
  anthropic"` exits cleanly. `python models/device.py` prints `mps`. Also ran step 2 here:
  `data_pipeline/look_at_data.py` prints the same counts and peaks as on the builder's Mac
  (469 subjects; 4.30 Hz and 4.88 Hz).

- Sat 14 Nov 14:10 CET, builder's agent: data downloaded on the builder's Mac ("PADS: done,
  all files OK."). Step 2: `data_pipeline/look_at_data.py` counts subjects and plots two
  recordings; all numbers match `docs/DATASETS.md`.

- Sat 14 Nov 14:05 CET, builder's agent: step 1. `requirements.txt` (pinned versions) and
  `models/device.py` added. Import check passes on the builder's Mac (Python 3.12.10,
  Apple M3); `python models/device.py` prints `mps`.

- Sat 14 Nov 14:00 CET, builder's agent: the builder now works on a MacBook (Apple
  Silicon), not a Windows PC. Builder guide setup/commands, `CLAUDE.md` commands and the
  plan's "Who does what" updated. Code must still run on macOS and Windows. The demo is
  still the leader's Mac, so the cross-machine checks stay.

- Sat 14 Nov 14:00 CET, team leader's agent: builder guide rewritten for a Windows PC;
  cross-machine checks added (builder on Windows, demo on the leader's Mac).
- Sat 14 Nov 13:30 CET, team leader's agent: repository set up with rules summary, project
  plan, dataset notes, two build guides, reused-code disclosure.

## Results so far (real numbers only; say which script produced them)

- `evaluation/evaluate_corrector.py` (test people, after the 2.56 s detector warm-up): our
  corrector + detector gate removes 84% of tremor with 0 ms lag; distance to the intended path
  moving / still 7.2 / 5.9 px (no filter 13.2 / 12.7; One Euro original 19.7 / 5.9 with 40 ms
  lag); steady-hand sequences 1.97 px (no filter 2.30). Mild tremor (<3 px): 1% removed.
  `models/corrector/time_live.py` on the builder's Mac: worst 2.9 ms per update with the gate.

- `evaluation/evaluate_detector.py --missed-target 0.2` (test people): detector v1 missed
  14.3%, false alarms 27.0%, accuracy 76.2%; frequency rule (same cut-off rule) missed 14.8%,
  false alarms 59.0%. Hand moving: false alarms 29.0% vs 58.9%. Mild tremor (<3 px) missed
  37.0%. Half / double pixel factor: model 16.8% / 34.0% and 12.3% / 22.5% (missed / false
  alarms). Validation average precision 0.676 (`models/detector/train.py`).

- `evaluation/run_baselines.py` (test people): detector "always no tremor" missed 100%,
  false alarms 0%, accuracy 74.5%. Frequency rule (balanced cut-off) missed 47.2%, false
  alarms 19.4%; at missed <= 10% on validation: missed 7.4%, false alarms 72.9%. Corrector,
  distance to the intended path moving / still: no filter 12.5 / 12.8 px; One Euro
  (original settings) 19.7 / 5.9 px, 68% tremor removed, 40 ms lag; moving average 0.2 s
  34.8 / 3.4 px, 91%, 100 ms. Full table in `evaluation/results/baselines.md`.

- `data_pipeline/build_dataset.py`: detector windows train 16,771 (3,848 tremor), val 3,452
  (660), test 3,708 (944). Corrector sequences train 4,207, val 809, test 930. Test people:
  PD 43, healthy 12, other movement disorders 9, ET 4, atypical 2, MS 2 (TremorDB 2); ages
  19 / 24 / 29 (under 60 / 60-69 / 70+); 28 female, 44 male. Groups under 10 are unreliable.

- `data_pipeline/tremor_library.py`: 13,764 segments. Tremor-marked: PADS Parkinson's 635 of
  7,728 (156 people), essential tremor 217 of 784 (26), other movement disorders 221 of
  1,680 (40), atypical Parkinsonism 13 of 420 (6), MS 16 of 308 (5), healthy 61 of 2,212
  (33); TremorDB 261 of 632 (14 of the 15 people with recordings; subject v3 has none). Pixel factor: PADS 594 px/rad, TremorDB
  98.6 px/unit. Tremor-marked size median 6.2 px (10th-90th percentile 1.5-34.3 px).

- `data_pipeline/look_at_data.py`: PADS 469 subjects (276 Parkinson's, 79 healthy, 60 other
  movement disorders, 28 essential tremor, 15 atypical Parkinsonism, 11 MS); ages 161 / 149 /
  159 (under 60 / 60-69 / 70+); 281 male, 188 female. PADS 060 right wrist Relaxed: peak
  4.30 Hz, 99% of power in 3-12 Hz. TremorDB rofh/s6rof.let: peak 4.88 Hz, 98% in 3-12 Hz.

## Decisions made along the way (what, why, who decided)

- Sat 14 Nov, builder (human): DECISION 3 = A (gradient boosting on explainable features)
  and train on the builder's Mac (8 GB was enough: about 0.5 GB used so far).
- Sat 14 Nov, builder (human): DECISION 4 = B, cut-off at most 20% missed on validation
  (10% would have meant 46.5% false alarms).
- Sat 14 Nov, builder (human): DECISION 1 = A, one pixel factor per dataset with the median
  tremor-marked Parkinson's segment at 6 px; re-check at half and double later.
- Sat 14 Nov, builder (human): DECISION 2 = A, all PADS task types, labelled rest /
  postural / action.
- Sat 14 Nov, builder's agent: tremor-marking rule fixed before any model (see
  `data_pipeline/tremor_library.py`); strength compared with healthy controls of the same
  task type, because deliberate movement looks like tremor-band power otherwise.

## Problems and things that did not work

- Sat 14 Nov, builder's agent: step 3 was merged before its `STATUS.md` entry was written (a
  scripted edit failed silently); fixed in the next commit on `main`. Lesson: check each
  edit succeeded before committing.
- Sat 14 Nov, builder's agent: the same slip again at step 8 (merged before STATUS, guide and
  SOURCES were updated); fixed in the next commit. Git commands now only run after every
  scripted edit has succeeded.
- None else yet. (Keep this honest; the write-up needs a "what didn't work" section.)

## Requests to another lane

- Builder -> team leader (Sat 14 Nov 15:00): **second cross-machine check (step 8).** On the
  demo Mac after `git pull` and `python -m pip install -r requirements.txt`, run
  `python models/corrector/time_live.py` and write both lines of output here. It loads
  `models/corrector/weights.pt` and the detector, so it also proves both models load there.

- Builder -> team leader (Sat 14 Nov 14:45): optional check on the demo Mac after pulling:
  `python models/detector/predict.py` has no main; instead run
  `python -c "from models.detector.predict import Detector; print('ok')"` to confirm the saved
  detector loads (it needs the same scikit-learn version, which requirements.txt pins).

- DONE (Sat 14 Nov, leader's Mac): builder's first cross-machine check. See "Done".

## Questions waiting for the team leader

- Sat 14 Nov 14:10, from the builder: rewrite `scripts/download_data.py` and
  `baselines/classical_filters.py` from scratch to remove any rule-2 risk? Builder's agent
  recommends yes (about 30-45 min). Changes the decision in `docs/REUSED_CODE.md`.
