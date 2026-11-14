# STATUS: where the project stands right now

**Every agent updates this file at the end of every work session** (rules in `CLAUDE.md`).
The writer builds the write-up from it, and teammates read it instead of asking.
Newest entries go at the top of each list. Use local time and say who you are.

## Right now

| Lane | Working on | Branch | Blocked by |
|---|---|---|---|
| Builder | IN PROGRESS: step 14, results package (evaluation/results/RESULTS.md). Steps 1-13 built | builder/results-package | - |
| Team leader | B1 (whole-laptop tracker) DONE and merged. Next: B2, the assistant | - | - |
| Writer | not started | - | - |

## Done (newest first)

- Sat 14 Nov 16:57 CET, builder's agent: the leader's jerkiness request, and a full review of
  code and docs (three read-only reviewers; every finding checked before fixing). Corrector v4
  (smoothness penalty 0.5) kept and used by the app. Live bugs fixed: tick-clock rounding drift
  (corrected cursor trailed 10 ms), demo replay repeating/skipping 7% of samples, jumps after a
  pause, settings changes restarting the detector, "Lower sensitivity" range, tracking button
  hidden, other websites able to reach the server, broken messages closing the connection.
  Evaluation: one definition of "hand moving", failure analysis pinned to the final models,
  demo comparisons developed on validation people's tremor, jerkiness metric. All affected
  results re-run; the datasets were rebuilt and verified identical (only the moving labels changed).

- Sat 14 Nov 16:02 CET, builder's agent: the leader's demo-gain request. Resampling bug fixed,
  corrector v3 kept (app = detector v2 + corrector v3), demo strength levels, correction
  indicator, `evaluation/compare_modes.py` (now writes `evaluation/results/demo_modes_val.md` / `_test.md`).

- Sat 14 Nov 15:37 CET, builder's agent: step 13, summary page (`web/summary.html`); server
  now counts any movement as active time (slow movement was missed before).

- Sat 14 Nov 15:35 CET, team leader's agent: step B1, the whole-laptop pointer reader
  (`tracker/`). `tracker.reader.start(callback)` / `stop()` follow Contract 1: 100 Hz,
  positions and times only, nothing saved to disk unless asked, idle after 3 s still.
  Added `pyobjc-framework-Quartz==13.0` (macOS only) to `requirements.txt`. Checked with the
  builder's server: it finds the tracker and switches it on/off; a fake 5 Hz wobble sent
  through the server's callback produced the `whole_laptop` summary block.

- Sat 14 Nov 15:30 CET, builder's agent: step 12. Detector v2 kept (app now uses it, on a
  background thread); corrector v2 not kept. `evaluation/results/improvements.md`,
  `detector_v2.md`, `corrector_v1_gate_v2.md`.

- Sat 14 Nov 15:10 CET, builder's agent: step 11, live demo page (`web/`), style C (warm and
  friendly), plain JavaScript. All "must do" steps (1-9 and 11) are now built.

- Sat 14 Nov 15:03 CET, builder's agent: step 10, `server/main.py` (FastAPI, 127.0.0.1 only),
  `server/test_ws.py`, `docs/RUNNING.md` (macOS and Windows sections). The app runs from a
  fresh clone without downloading data.

- Sat 14 Nov 14:52 CET, builder's agent: step 9, `evaluation/find_failures.py` ->
  `evaluation/results/failures/` (charts, `failure_facts.md`, `failures.md`). Saturday-night
  checkpoint reached early: baselines, both models and failures all done with real numbers.

- Sat 14 Nov 14:49 CET, builder's agent: step 8, corrector v1 (`models/corrector/`), trained in
  119 s on the builder's Mac; scored once on test with `evaluation/evaluate_corrector.py` ->
  `evaluation/results/corrector_v1.md`. Detector live calls now use one thread (20 ms -> 2 ms).

- Sat 14 Nov 14:42 CET, builder's agent: step 7, detector v1 (`models/detector/`), scored once
  on test with `evaluation/evaluate_detector.py --missed-target 0.2` ->
  `evaluation/results/detector_v1.md`. Live use via `models/detector/predict.py`.

- Sat 14 Nov 14:29 CET, builder's agent: step 6, `evaluation/metrics.py` (shared scoring) and
  `evaluation/run_baselines.py` -> `evaluation/results/baselines.md`.

- Sat 14 Nov 14:23 CET, builder's agent: step 5, `data_pipeline/build_dataset.py` splits 484
  people by person (340 / 72 / 72, seed 42, `data_pipeline/split.json`) and builds detector
  windows and corrector sequences; `python -m pytest data_pipeline/test_split.py` passes (4).

- Sat 14 Nov 14:20 CET, builder's agent: step 4, `data_pipeline/synthetic_paths.py` generates
  clean mouse paths with reaches, corrections, pauses, drifts and tremor look-alikes
  (wiggles, circles, zig-zags; about 28% of the time). Chart in `evaluation/results/figures/`.

- Sat 14 Nov 14:18 CET, builder's agent: step 3, `data_pipeline/tremor_library.py` builds
  `data/derived/tremor_library.npz` (13,764 segments of 10.24 s) in about 30 s, peak memory
  about 0.5 GB on the builder's 8 GB Mac. Step 1 ticked in the guide after the leader's check.

- Sat 14 Nov, team leader's agent: **first cross-machine check PASSED on the demo Mac**
  (Apple Silicon, macOS 26, Python 3.12.16, fresh `.venv`). `pip install -r
  requirements.txt` installed all pinned versions with no errors and `pip check` reports
  no broken requirements. `python -c "import numpy, pandas, scipy, sklearn, torch, fastapi,
  anthropic"` exits cleanly. `python models/device.py` prints `mps`. Also ran step 2 here:
  `data_pipeline/look_at_data.py` prints the same counts and peaks as on the builder's Mac
  (469 subjects; 4.30 Hz and 4.88 Hz).

- Sat 14 Nov 14:08 CET, builder's agent: data downloaded on the builder's Mac ("PADS: done,
  all files OK."). Step 2: `data_pipeline/look_at_data.py` counts subjects and plots two
  recordings; all numbers match `docs/DATASETS.md`.

- Sat 14 Nov 14:06 CET, builder's agent: step 1. `requirements.txt` (pinned versions) and
  `models/device.py` added. Import check passes on the builder's Mac (Python 3.12.10,
  Apple M3); `python models/device.py` prints `mps`.

- Sat 14 Nov 14:06 CET, builder's agent: the builder now works on a MacBook (Apple
  Silicon), not a Windows PC. Builder guide setup/commands, `CLAUDE.md` commands and the
  plan's "Who does what" updated. Code must still run on macOS and Windows. The demo is
  still the leader's Mac, so the cross-machine checks stay.

- Sat 14 Nov 14:00 CET, team leader's agent: builder guide rewritten for a Windows PC;
  cross-machine checks added (builder on Windows, demo on the leader's Mac).
- Sat 14 Nov 13:30 CET, team leader's agent: repository set up with rules summary, project
  plan, dataset notes, two build guides, reused-code disclosure.

## Results so far (real numbers only; say which script produced them)

- `evaluation/smoothness.py --test` (test, gated by detector v2): corrector v4 (app) off the
  path moving / still 6.94 / 4.86 px, 87% tremor removed, 0 ms lag, jerkiness 1.37 px (no
  filter 1.69, v3 1.96, One Euro 0.64 but 40 ms lag); no marked tremor 1.85 px (no filter 2.30).
- `evaluation/compare_modes.py --people test` (demo page, final): our model vs no filter, hand
  still / reaching: strong 69% / 53% closer, medium 39% / 23%, mild 53% / 6%; smoother than no
  filter in every case. One Euro is closer for a perfectly still hand (medium 1.44 vs 3.70 px).
- `evaluation/find_failures.py` (final models, test): detector v2 misses 34.2% of mild tremor
  vs 2.9% of strong; false alarms 41.7% on action-task segments vs 19.5% rest.
- `models/corrector/time_live.py` (builder's Mac, final): mean 0.48 ms, worst 3.4 ms per update.
- Note: "hand moving" now means intended movement faster than 20 px/s for at least half the
  window everywhere; the moving/still splits in the entries below were re-run with it
  (`evaluation/results/*.md` hold the current values).

- `evaluation/improvements.py --test` (corrector, gated by detector v2): v3 vs v1 off the path
  moving / still 6.85 / 4.93 vs 7.15 / 5.93 px; tremor removed mild / medium / strong 8% / 50%
  / 87% vs 3% / 48% / 85%; steady hand 1.82 vs 2.00 px (no filter 2.30); lag 0 ms both.
- `evaluation/compare_modes.py` (demo page, our model vs no filter, hand still / reaching):
  strong 46% / 34% closer, medium 35% / 21%, mild 20% / -7%. One Euro beats our model for a
  perfectly still hand (medium: 1.44 vs 3.98 px) but lags while reaching (11.8 vs 4.8 px).

- `python -m tracker.demo` (demo Mac, leader moving the pointer in another app): 1,001
  samples in 10 s, 100.0 samples per second, gap median 10.00 ms / 95th percentile 11.80 ms /
  longest 12.50 ms, standard deviation 0.84 ms; no permission prompt.
  `python -m pytest tracker/test_reader.py`: 5 passed.
- `evaluation/improvements.py --test`: detector v2 vs v1 on pause-free test movement: false
  alarms 20.4% vs 45.3% (missed 11.2% vs 8.1%); normal test windows: v2 missed 12.9%, false
  alarms 27.1% (v1 14.3% / 27.0%). Corrector v2 (size-mixed training) vs v1 on validation:
  2.32 / 3.11 / 4.54 px vs 2.21 / 3.05 / 4.55 px at tremor x0.5 / x1 / x2 -> not kept.
- `evaluation/evaluate_corrector.py --detector v2` (final system, test): 84% tremor removed,
  0 ms lag, 7.15 / 5.93 px moving / still, steady hand 2.00 px. `models/corrector/time_live.py`:
  worst 4.4-4.8 ms per update (detector on a background thread).

- `server/test_ws.py` (builder's Mac): 500/500 replies per mode; mean reply 0.56 ms in the
  learned mode with demo tremor (99th percentile 2.92 ms), 0.24-0.25 ms in the other modes.

- `evaluation/find_failures.py` (test): detector misses 37.0% of mild tremor (<3 px) vs 3.4% of
  strong (>10 px); false alarms 43.5% on action-task segments vs 19.0% rest and 8.4% synthetic
  only. Our corrector is further from the path than the better of no filter / One Euro in 54
  of 236 test sequences with marked tremor.

- `evaluation/evaluate_corrector.py` (test people, after the 2.56 s detector warm-up): our
  corrector + detector gate removes 84% of tremor with 0 ms lag; distance to the intended path
  moving / still 7.2 / 5.9 px (no filter 13.2 / 12.7; One Euro original 19.7 / 5.9 with 40 ms
  lag); steady-hand sequences 1.97 px (no filter 2.30). Mild tremor (<3 px): 1% removed.
  `models/corrector/time_live.py` on the builder's Mac: worst 2.9 ms per update with the gate.

- `evaluation/evaluate_detector.py --missed-target 0.2` (test people): detector v1 missed
  14.3%, false alarms 27.0%, accuracy 76.2%; frequency rule (same cut-off rule) missed 14.8%,
  false alarms 59.0%. Hand moving: false alarms 28.9% vs 58.6%. Mild tremor (<3 px) missed
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

- Sat 14 Nov, team leader (human): DECISION L1 = A. Keep only the current session in memory,
  plus an optional local file the user can delete. A history across days to show trends
  (option B) is wanted as a future extension, not for the hackathon.
- Sat 14 Nov 16:57, builder's agent (chosen on validation by a rule fixed in advance): keep
  corrector v4 with smoothness penalty 0.5; the app uses detector v2 + corrector v4.
- Sat 14 Nov 16:02, builder's agent (chosen on validation): keep corrector v3 over v1.
- Sat 14 Nov, builder's agent (step 12, chosen on validation): keep detector v2, keep
  corrector v1. The app used detector v2 + corrector v1 (superseded: corrector v3 at 16:02,
  then v4 at 16:57).
- Sat 14 Nov, builder (human): DECISION 5 = A (models run in Python on the server);
  DECISION 6 = C (warm and friendly look); DECISION 7 = plain JavaScript.

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
- Sat 14 Nov, builder's agent: corrector v2 (trained on tremor 0.5x-2x as large) did not
  beat v1 on validation; dropped. Detector v2's half/double pixel-factor check was not re-run.
- Sat 14 Nov, builder's agent: the server's active-time rule missed slow movement (under
  0.5 px between samples); found by the step 13 session test and fixed.
- Sat 14 Nov, leader's agent: corrector v1 scores well on distance to the intended path
  but looks jumpy live (see the leader's request to the builder, below). Lesson for the
  write-up: one metric can hide a problem a person sees in two seconds; try the demo by hand.
- Sat 14 Nov, builder's agent: the live code's resampling (repeat the last position) made the
  corrector worse than no filter at browser-like 60 Hz; found by the leader's demo test, fixed.
- Sat 14 Nov, builder's agent: for a perfectly still hand One Euro beats our model at every
  tremor strength on the demo page. Not fixed; reported.
- Sat 14 Nov, builder's agent: a code review found live-pipeline bugs that the offline test
  scores could not see (they never go through the live code): tick-clock rounding drift, the
  demo replay repeating/skipping samples, jumps after a pause. Lesson: test the live path
  itself (`evaluation/compare_modes.py`), not only the models.
- Sat 14 Nov, builder's agent: an earlier version of the demo comparison replayed test people's
  tremor while we were still making design choices; now development uses validation people's
  recordings and test people's only once for the final figure.
(Keep this list honest; the write-up needs a "what didn't work" section.)

## Requests to another lane

- Team leader -> builder (Sat 14 Nov, leader tried the demo by hand): **"Our model" looks
  jumpy and ugly; One Euro looks smooth.** The leader saw "random corrections" with Demo
  tremor on. The leader's agent confirmed it with ad-hoc scripts (not in the repo), sending
  a slow back-and-forth reach with the recorded demo tremor at 60 samples/s (browser rate)
  through `/ws/cursor`, and measuring jerkiness = mean size of the frame-to-frame change in
  cursor velocity (px):
  no filter 3.21 (biggest single jump 20.8 px); One Euro 0.62 (7.6 px); our model 9.90
  (28.3 px). At 100 samples/s: 1.41 / 0.24 / 3.70. So the model is closer to the path on
  average but about 3x jerkier than no filter at all. Chart:
  leader's laptop `~/Desktop/screenshots/veritas-prototype/modes_cursor_y_60hz.png`.
  Likely causes: (a) `train.py` loss is only squared position error, so nothing rewards a
  smooth output, and the offset is re-predicted from scratch every 10 ms; (b) at 60 Hz,
  `live.py` resamples by holding the last position, so the network sees zero steps
  followed by double steps that it never saw in training.
  Offline test (subclass of `LiveCorrector`, no repo file changed; 60 Hz; off-path px /
  jerkiness): as now 5.51 / 10.11; linear interpolation when resampling 5.00 / 5.33;
  smoothing the offset over 30 ms 4.69 / 3.89; both 5.54 / 3.29; no filter 6.16 / 2.79.
  So interpolation plus a little smoothing removes most of the jumps but also most of the
  gain over no filter. Suggested: (1) add a jerkiness metric to `evaluation/metrics.py`
  and report it next to distance for every filter (distance alone hid this problem);
  (2) interpolate instead of holding in `live.py`; (3) retrain with a smoothness term in
  the loss (penalise the change in predicted offset between neighbouring ticks), and judge
  it on validation by distance AND jerkiness. Builder decides; please report the numbers.
  ANSWERED (Sat 14 Nov 16:57, builder; the numbers above were measured with corrector v1 and the
  old hold-last-position resampling): (1) jerkiness is in `evaluation/metrics.py` and every
  corrector table; (2) interpolation is in `models/resample.py`; (3) corrector v4 adds a penalty
  on the corrected cursor's jerk, chosen on validation: on test it is smoother than no filter
  (1.37 vs 1.69 px) with 87% tremor removed and 0 ms lag. Two live bugs also caused jumps
  (tick-clock drift, demo replay skipping samples); fixed. On the demo page our cursor is now
  smoother than no filter in every case (`evaluation/compare_modes.py --people test`).

- Team leader -> builder (Sat 14 Nov, after trying the demo page on the demo Mac):
  **"Our model" looked the same as "No filter" to the leader.** The leader's agent sent one
  smooth path (30 s, first 3 s skipped for warm-up) through `/ws/cursor` in each mode with
  an ad-hoc script (not in the repo) and measured the mean distance of the shown cursor from
  the intended path:
  Numbers below are with the step 12 models (detector v2), commit 61fa583:
  - Demo tremor OFF: no filter 0.00 px, One Euro 9.17 px, our model 0.01 px (gate above
    0.5 for 0% of the time). With a steady hand the model correctly does nothing, so there
    is nothing to see. (Before step 12 the gate was open 47% of the time on this path:
    detector v2 fixed that.)
  - Demo tremor ON: no filter 6.20 px, One Euro 8.79 px, our model 4.53 px (gate above
    0.5 for 83% of the time). The model helps, but only about 27% closer to the path, much
    less than the test-set figures in `evaluation/results/corrector_v1.md`; hard to see by eye.
  Requests: (1) on the page, show when the model is correcting (for example the gate value
  or a "correcting" label) and tell the user to switch Demo tremor on first; (2) find out why
  the demo-tremor gain is smaller than on the test set (bigger demo segments? path speed?);
  (3) add a small mode-comparison script like this to the repo so the numbers can be
  reproduced.
  ANSWERED (Sat 14 Nov 16:02, builder): (1) the page now shows "Correction: ON / partly /
  off" and a tip to switch demo tremor on; (2) causes: a resampling bug at browser rates
  (fixed), the demo's medium tremor (gain depends on size; now a mild/medium/strong choice),
  and v1's squared-error training (corrector v3 fixes part of it); (3)
  `python evaluation/compare_modes.py` reproduces the numbers. Details in `docs/EXPLAINED.md`.

- DONE (Sat 14 Nov 15:40, builder): tracker gaps over 1 s now restart the laptop detector;
  the tracking button shows whenever `/api/status` says the tracker is available.

- Team leader -> builder (Sat 14 Nov 15:35): **Contract 1 is live.** `tracker/reader.py` is
  on `main`; after `git pull` and `python -m pip install -r requirements.txt`,
  `GET /api/status` shows the tracker as available. Your `whole_laptop` summary addition
  is fine for the assistant. Please make sure the demo page's tracking on/off button is
  visible. The "delete my data" button will be in the assistant panel (B2). Note: the
  tracker stops sending samples after 3 s of a still pointer, so the server sees time gaps;
  `laptop_detector` should treat a long gap as a fresh start if that matters to it.

- Builder -> team leader (Sat 14 Nov 15:10, updated 16:30): **third cross-machine check
  (step 11), still open.** The page and models changed since (corrector v4, the "Correction"
  indicator, replayed tremor strength). On the demo Mac: `git pull`,
  `python -m uvicorn server.main:app`, open http://127.0.0.1:8000 in Safari AND Chrome,
  switch "Demo tremor" on and choose "Strong", move with the TRACKPAD and check the dark
  (corrected) cursor is visibly steadier than the grey one in "Our model" mode, and that
  switching filter modes works live. Write what you saw here. Your assistant panel goes in
  `<div id="assistant-panel">`; the page loads `web/assistant/assistant.js` if it exists.

- DONE (answered by the leader 15:35) Builder -> team leader (Sat 14 Nov 15:03): the server is ready for your modules.
  (1) It imports `tracker.reader` (or `tracker`) for `start(callback)` / `stop()`, and starts
  it only when the page sends `POST /api/settings {"tracking": true}`: that is the on/off
  switch, and the demo page will show the button. (2) It includes `assistant.router` (or
  `assistant.api.router`). (3) `GET /api/summary` follows Contract 2 and adds an OPTIONAL
  `whole_laptop` block (session, tremor, distance, steadiness) when the tracker has data;
  please tell us if that addition is a problem for the assistant. The `notes` list says when
  demo tremor was on. Run with `python -m uvicorn server.main:app`; `GET /api/status` shows
  what loaded.

- DONE (Sat 14 Nov, leader's Mac, leader's agent): second cross-machine check (step 8).
  After `git pull` and `pip install -r requirements.txt` (`pip check` clean),
  `python models/corrector/time_live.py` printed: "corrector only mean 0.077 ms, 99th
  percentile 0.084 ms, worst 0.124 ms per update" and "corrector + detector gate mean
  0.185 ms, 99th percentile 1.139 ms, worst 1.493 ms per update". Both models load here.
  `python -m uvicorn server.main:app` serves the demo page in the browser; the trackpad
  feel check (third check) is still to do by the leader by hand.

- DONE (see above) Builder -> team leader (Sat 14 Nov 14:49): **second cross-machine check (step 8).** On the
  demo Mac after `git pull` and `python -m pip install -r requirements.txt`, run
  `python models/corrector/time_live.py` and write both lines of output here. It loads
  `models/corrector/weights.pt` and the detector, so it also proves both models load there.

- DONE (covered by the step 8 check) Builder -> team leader (Sat 14 Nov 14:42): optional check on the demo Mac after pulling:
  `python models/detector/predict.py` has no main; instead run
  `python -c "from models.detector.predict import Detector; print('ok')"` to confirm the saved
  detector loads (it needs the same scikit-learn version, which requirements.txt pins).

- DONE (Sat 14 Nov, leader's Mac): builder's first cross-machine check. See "Done".

## Questions waiting for the team leader

- Sat 14 Nov 14:10, from the builder: rewrite `scripts/download_data.py` and
  `baselines/classical_filters.py` from scratch to remove any rule-2 risk? Builder's agent
  recommends yes (about 30-45 min). Changes the decision in `docs/REUSED_CODE.md`.
