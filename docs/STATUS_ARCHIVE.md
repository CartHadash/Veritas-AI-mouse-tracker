# STATUS archive (snapshot of STATUS.md, Sun 15 Nov 10:45 CET)

Moved here by the leader's agent when `STATUS.md` was trimmed to what is live (leader's request).
Nothing was deleted: every finished request, superseded result and older decision is below,
exactly as it was. Current numbers: `evaluation/results/RESULTS.md`. Current state: `STATUS.md`.

---


## Right now

| Lane | Working on | Branch | Blocked by |
|---|---|---|---|
| Builder | Steps 1-15 built (4, 9, 11, 14, 15 await human or Mac checks) + click freeze + calibration test + step 4 path check. Next: see "Builder's plan" below | main | - |
| Team leader | B1 (tracker), B2 (assistant) and the UI redesign DONE and merged. Next: try the new page with a real hand on the trackpad; the B3 real-cursor check on the demo Mac; Part A checks | - | - |
| Writer | IN PROGRESS: drafting the write-up. Start from `docs/WRITER_BRIEF.md` (where everything is) | - | - |

### Builder's plan: what is left (written Sat 14 Nov 20:03 CET; tick or delete lines as they finish)

Time line: first full version by **Sun 15 Nov 22:00 CET**; no new features after about Sun
20:00 CET; hard deadline Mon 16 Nov 05:59 CET.

**1. Builder can do now (no one else needed), in this order:**
- [x] Bug: "Lower sensitivity" cursor offset (leader's request 20:30). Plan: Pointer Lock in
      that mode (click the area to lock, Esc to leave), so the drawn cursor is the only one and
      cannot leave the area. About 45 min.
- [x] Session history on the summary page (leader's request 21:00), plus saving the last
      minute when "New session" is pressed. About 45 min.

**2. Waiting for people (builder is blocked until then):**
- [x] Round 1 of the step 4 path check (Timofey): realistic version 1 rated worse; version 2 built.
- [ ] Everyone: round 2 of the path check (`git pull`, reload `path_check.html` with
      Cmd+Shift+R, 5 min), reports in the group chat. If version 2 rates higher than the
      original, the builder asks the saved step 4 question (stress test / retrain); the step 9
      question can be answered any time.
- [ ] Oleksandr: read `evaluation/results/failures/failures.md` (step 9) and `RESULTS.md` (step 14).
- [ ] Timofey: trackpad check on the demo Mac (step 11). Partly done 21:35-21:50: model closer
      than One Euro but still jittery (request below); Pointer Lock works in Safari; Chrome
      hand check of the fresh copy done, results sent to the builder in the group chat. (Step 15 fresh-clone test on the demo
      Mac: DONE by the leader's agents, see "Results"; it found and fixed a RUNNING.md order bug.)
- [x] Timofey: answer the open question on rewriting the two pre-hackathon files (YES, 21:20).

- [x] Rewrite `scripts/download_data.py` and `baselines/classical_filters.py` from scratch
      (leader said YES, 21:20); re-run the baselines and check the numbers still match; update
      `docs/REUSED_CODE.md`. About 30-45 min.
- [x] Step 9 additions picked by the leader (21:20): per-person uncertainty ranges; failures
      per person and a corrector failure on real marked tremor; the live still-hand weak
      spot. About 1 h.

**3. After the answers (only if time allows; cut from the bottom up):**
- [x] Step 4: stress test the models on the realistic movement: no clear drop, no retraining.
- [x] Leader's "still jittery" request: corrector v4 penalty 2 chosen on validation (smoother, no lag).
- [ ] Timofey's idea 3, sticky targets (about 1 h). **UI: taken by the team leader (Sat 22:00).**
- [ ] **UI: taken by the team leader (Sat 22:00).** Accessibility (Oleksandr's idea): a "Read aloud" button for the summary numbers (the
      browser's built-in speech, no new library), a font toggle that is easier to read with
      dyslexia, colour-blind-safe colours for the two cursors, targets and charts, and larger
      text. About 1-1.5 h for all. Reading the assistant's answers aloud touches
      `web/assistant/` (leader's lane): needs the leader's OK, or the leader adds it.
- [x] (built; real-cursor check by the leader pending) B3, correcting the real cursor everywhere (`systemwide/`), moved to the builder by the
      leader (21:20). **Leader (Sat 22:00): wanted, not optional.** Time box 2 h, finished
      before Sun 15:00 CET (start by about 13:00); if not visibly steadier by then, stop and
      document it. Steps in `BUILD_GUIDE_LEADER.md` "Step B3". Mac-only and needs the
      Accessibility permission; the demo Mac is the leader's, so the leader runs the check.
- [ ] Step 16, the desktop window (cut first).

## Done (newest first)

- Sun 15 Nov, builder's agent: bug hunt and speed-up (Oleksandr: "bugfix and then optimize").
  Measured first, in the browser and with a timing snippet, not by a committed script, so no
  figures are recorded here; what changed: (1) the page's "Shake" readout compared every sample
  with every other one four times a second, which stalled the page; it now uses a sliding
  window and gives identical values. (2) The meter is redrawn once per frame, not once per
  reply. (3) The page sends at most one sample per 4 ms (plus the newest of each event), so a
  very fast mouse cannot flood the server; the models work at 100 a second anyway. (4) The
  summary's per-minute table no longer searches the whole session once per minute (identical
  output). (5) Bug: browsers kept an old `app.js` after `git pull`; the server now sends
  `Cache-Control: no-cache`, so a normal reload is enough. (6) Bug: the calibration test ignored
  the Steadiest / Balanced / Faster choice. (7) The 404 for `favicon.ico` is gone. Checks
  re-run: `server/test_ws.py`, 19 tests, `time_live.py`, `check_results.py`, and
  `evaluation/compare_modes.py` (results file unchanged).

- Sun 15 Nov, builder's agent: a "Steadier or more responsive" choice for Our model (Oleksandr:
  "feels a bit laggy"; team chose to let users pick, starting at the steadiest). Three levels
  from the lag tuning grid (`models/corrector/live.py` RESPONSE_LEVELS), sent as `response` in
  `POST /api/settings`, switched without losing the detector's history. Test people
  (`evaluation/results/response_levels.md`, `python evaluation/response_levels.py`): Steadiest
  72 ms lag / shake 2.56 px; Balanced 47 ms / 2.87; Faster 30 ms / 3.38. Switching while
  moving adds no jump (largest step 55.78 px switching vs 54.86 px always Steadiest: that is
  the reach itself). Small UI addition in `web/index.html` + `web/app.js` (request below).

- Sun 15 Nov 00:55 CET, builder's agent: the model review the team asked for (Timofey 23:14). Measuring what
  the eye sees (`evaluation/vs_one_euro.py`) showed our network's cursor almost as jumpy as no
  filter. Option A: the app adds One Euro smoothing switched by our detector. Option B: corrector
  v5 trained against visible shake; it beat A by the rule fixed before training and is now the
  app's network. Test people (`vs_one_euro_test.md`): shake 2.56 px (One Euro 3.39, no filter
  7.91), jerk 0.24 (0.30 / 1.00). Price: it lags while reaching like One Euro. Lag tuning
  (`tune_lag.md`): less lag always meant more shake, so kept. Also a first-use guide
  (`web/tutorial.js`). Oleksandr's notch-filter idea tested, not kept (`notch_canceller.md`).

- Sat 14 Nov, leader's agent: `leader/ui` merged into `main` on the leader's word (the two
  entries below say "not merged": that was true when they were written). The only conflict
  was this file; both lanes' entries were kept.

- Sat 14 Nov 22:13 CET, leader's agent: second pass on the redesign (`leader/ui`, pushed, not merged), after
  the leader asked for more interaction and more visual statistics. Practice: a ring bursts
  from a hit target with the time it took, a cross marks a miss, a "3 in a row" streak chip, a
  live graph of the last 20 seconds of the detector's score with the cut-off line, and "Your
  targets" as one bar per filter (share of clicks that hit). Analysis: ring charts for
  tremor-like share and clicks hit, a 0-to-1 gauge for steadiness, numbers that count up, and
  the minute-by-minute chart shows a minute's exact numbers under the pointer. How it works:
  each step has a "Show me" button that opens Practice and rings the part it describes. No
  new numbers: every figure is one the page already showed. Checked in the browser at 1440 px
  with simulated pointer events (hits, a miss, hover, Show me), no console errors;
  `python server/test_ws.py` still passes. Not checked with a real hand on the trackpad.

- Sat 14 Nov 21:57 CET, leader's agent: interface redesign on branch `leader/ui` (pushed, not merged yet).
  One page with three tabs (Practice with a larger practice area, Analysis = the old summary
  page, How it works), the assistant as a floating button that opens a window, the same warm
  look made tidier, and a fading trail behind the raw and corrected cursors. Controls are
  ui-sdk web components, copied into `web/vendor/ui-sdk/` so the page needs no internet.
  `summary.html` now only forwards to `index.html#analysis`. Checked in the browser at
  1440 px and 375 px wide: tabs, filter choice, demo tremor, click freeze, meter, assistant
  window open/stay open/close, no console errors. Re-run and still passing:
  `python server/test_ws.py` (4 modes x 500 replies) and
  `python -m pytest data_pipeline/test_split.py tracker/test_reader.py` (7 passed, 7 skipped).
  Not checked: a real hand on the trackpad (calibration test, Pointer Lock in "Lower
  sensitivity", target clicks), and a live question to the assistant in the new window.

- Sat 14 Nov 22:02 CET, builder's agent: B3 built (`systemwide/`): safety first (auto-off after 60 s,
  Control + Option + X, Ctrl+C, filter failure -> cursor follows the hand, stays on screen,
  permission only checked, never requested). Logic tests pass (`systemwide/test_steady.py`, 5);
  on the builder's Mac (no permission) it stops with instructions. Real-cursor check: leader.

- Sat 14 Nov 21:59 CET, builder's agent: the leader's list (Sat 20:59).
  (1) `scripts/download_data.py` and `baselines/classical_filters.py` rewritten from scratch;
  no pre-hackathon code is left. The download script checked all 12,689 PADS + 123 TremorDB
  files on disk and fetched TremorDB into an empty folder correctly. Kalman reproduces
  exactly; the old One Euro did not follow the authors' reference code, so One Euro now looks
  less smooth and less laggy (test: 49% removed, 20 ms; was 68%, 40 ms). Every evaluation
  using the filters was re-run and `RESULTS.md` updated.
  (2) Step 9 additions (`evaluation/failure_extras.py` -> `failures/extras.md`, explained in
  `failures.md`): 95% ranges by redrawing people, failures per person, corrector failures on
  real marked tremor, the still-hand weak spot.
  (3) "Still jittery": `evaluation/smoother_output.py` chose corrector v4 with penalty 2 on
  validation (rule fixed in advance); on test jerkiness 1.37 -> 1.12 px, no lag, 5% more
  distance while moving. The app now uses it (`models/corrector/live.py`).
  (4) Step 4 stress test (`evaluation/realism_stress.py`): on realistic movement the models do
  not drop, so no retraining.

- Sat 14 Nov 20:49 CET, builder's agent: step 4 path check round 1 (Timofey's ratings,
  `evaluation/results/path_check_ratings_1.md`): current generator 2.3 / 5, realistic
  version 1 only 1.5 / 5 ("too straight" on all 6). Built realistic version 2 (curves, slow
  sideways wobble, uneven speed, blended corrections, settling pauses, wandering drifts, fewer
  look-alikes). Original generator unchanged. Round 2 paths (seed 2027) are on the check page.

- Sat 14 Nov 20:15 CET, builder's agent: the leader's two requests. "Lower sensitivity" now uses Pointer Lock
  (the drawn cursor is the only cursor and reaches every edge; simulated check: 200 px of hand
  movement -> 100 px of cursor, far edge reached). The summary page shows earlier sessions
  (`GET /api/assistant/history`) with demo/filter notes and the "not a health trend" line;
  "New session" saves the session first. Also fixed: the "Replayed tremor" row showed while
  demo tremor was off (a CSS rule overrode `hidden`).

- Sat 14 Nov 21:00 CET, team leader's agent: session history (DECISION L1 now B). Each
  session's summary numbers are saved every minute to `local_logs/sessions/` (never raw
  movement); the assistant compares with the last 7 sessions (pointer numbers only, never
  health trends); "How does today compare with before?" button when history exists;
  `GET /api/assistant/history` for the summary page; "delete my data" also empties it.

- Sat 14 Nov 19:59 CET, builder's agent: step 4 review. Found five realism gaps in the generated movement
  (still hand creeps at a median 19.4 px/s; no whole pixels, 6.7% of validation tremor
  windows under 1 px; perfect 100 Hz timing; symmetric reaches that ignore target size; no
  text selection or dragging). Added an opt-in realistic version (`realistic=True`,
  `device_view()`); the original is unchanged (identical paths), so no data, model or number
  changed. Added the blind team test `web/path_check.html` (`data_pipeline/make_path_check.py`).

- Sat 14 Nov 20:00 CET, team leader's agent: assistant v3 (leader's requests): key details
  highlighted, simpler and shorter wording, and follow-up questions after every answer that
  become the new one-tap buttons ("Main questions" goes back). Re-tested 13/13 safe.

- Sat 14 Nov 19:34 CET, builder's agent: Godson's calibration idea. "Calibrate for my mouse (10 s)" on the
  demo page: hold a blue dot, then follow it; the server replays the test through each filter
  and reports each one's distance from the dot, the samples per second and the shaking.
  `evaluation/calibration_sim.py` (validation): letting the test choose the filter was WORSE
  than always using our model (later use, normal size: 2.37 px vs 3.15 px; best possible
  2.30 px), so the test only reports and never switches the filter. Measuring the mouse's
  speed setting itself is impossible from the cursor alone (explained in `docs/EXPLAINED.md`).

- Sat 14 Nov 19:20 CET, team leader's agent: step B2, the assistant (`assistant/`,
  `web/assistant/`). `claude-sonnet-5-5` at effort `low`, streamed; sees only the summary
  numbers; safety rules in `assistant/prompt.py`; a plain non-AI summary when there is no
  key. Routes: `POST /api/assistant/chat` (Contract 3), `GET /api/assistant/explain`,
  `GET /api/assistant/status`, `POST /api/assistant/delete-my-data` (empties `local_logs/`).
  Chat panel with three one-tap questions, a delete button and the disclaimer. Test page:
  `python -m assistant.standalone` (port 8001, example summary). Trap questions: all 13 safe
  (`assistant/test_prompts.md`).

- Sat 14 Nov 18:14 CET, builder's agent: click freeze (Timofey's idea 2). Demo page hits need
  press and release on the target; a "Click freeze" switch holds the cursor until release
  (max 0.3 s). `evaluation/click_sim.py --people test`: 10 px target, strong tremor: no
  filter 24% -> 39% of clicks land with freeze, our model 92% -> 94%.

- Sat 14 Nov 18:05 CET, builder's agent: step 15 on the builder's Mac. Fresh clone from GitHub
  + "On macOS" commands: install 41 s, app and `server/test_ws.py` pass with no data. With
  the datasets copied in, all data rebuilt from raw and every evaluation re-run: every results
  file and chart byte-for-byte identical. No secrets, data or files over 1 MB in git.

- Sat 14 Nov 17:17 CET, builder's agent: step 14, `evaluation/results/RESULTS.md` (results
  package for the writer), `evaluation/data_facts.py` -> `dataset_facts.md`, and
  `evaluation/check_results.py` (passes: every number is in a generated results file).

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

- `evaluation/smoother_output.py --test` (test, after choosing on validation): corrector v4
  penalty 2 (the app now) off the path moving / still 7.30 / 5.17 px, 86% removed, 0 ms lag,
  jerkiness 1.12 px (penalty 0.5: 6.94 / 4.86, 87%, 1.37; One Euro 15.32 / 6.98, 49%, 20 ms, 0.98).
- `evaluation/failure_extras.py` (test): missed 12.9% (95% range 9.7-18.4%), false alarms
  27.1% (24.7-29.5%), tremor removed 86% (75-90%); 19 of 236 marked-tremor sequences worse
  than no filter (7 mild, 10 medium, 2 strong).
- `evaluation/realism_stress.py` (validation, realistic movement v2 + device view): missed 18.0%
  (original 20.0%), false alarms 25.6% (27.3%); corrector advantage while moving 5.45 px
  (5.08 px). No retraining.
- `evaluation/run_baselines.py` with the rewritten filters (test): One Euro original settings
  15.02 / 6.92 px, 50% removed, 20 ms lag (old file: 19.68 / 5.91, 68%, 40 ms); Kalman identical.

- Step 15 on the DEMO Mac (Sat 14 Nov 21:30, leader's agent; fresh clone of commit 89b896d
  into a new folder, the "On macOS" commands of `docs/RUNNING.md` exactly, Python 3.12.16):
  `pip install -r requirements.txt` 24 s, `pip check` clean. The first server start took more
  than 30 s (fresh copy, first imports), then `/api/status`: tracker available, assistant
  available, 12 demo tremor segments. `python server/test_ws.py`: 500/500 replies in every
  mode, mean 0.60-0.79 ms, 99th percentile 4.4-6.9 ms; summary keys OK.
  `python -m pytest tracker/test_reader.py`: 5 passed. No `.env`, `data/` or `local_logs/` in
  git, no tracked file over 2 MB. `python models/corrector/time_live.py` with the Mac heavily
  loaded (load average 19.9): with the gate worst 6.8-7.4 ms over three runs (under the 8 ms
  limit but close; mean 0.68-0.73 ms); corrector alone one 21 ms spike in the first run, then
  5.0-5.4 ms. Re-measure on a quiet Mac before the demo. Evaluation scripts not re-run here
  (the builder's step 15 reproduced them byte for byte).
  Note from a second leader's-agent session (same evening): the heavy load during that timing
  was very likely this second session's full rebuild (next entry) running at the same time. On the quiet Mac just before,
  `time_live.py` in a fresh clone gave: corrector alone worst 0.36 ms, with the gate mean
  0.35 ms, worst 2.75 ms.

- Full rebuild from a fresh clone on the DEMO Mac (Sat 14 Nov 21:00-21:40, leader's agent;
  raw datasets linked in, every command of `docs/RUNNING.md` "Rebuild the data and re-score
  everything" except the download, about 20 minutes): (1) **the listed order failed** at
  `evaluation/evaluate_detector.py --missed-target 0.2` (needs `detector_val_x0.5.npz`, which
  the `--tremor-scale 0.5 / 2` builds only made later). With those two builds moved up, all 33
  steps ran. `RUNNING.md` is now in that order. (2) **Detector: reproduced exactly** (all
  detector results files identical). (3) **Corrector: retraining on this Mac is not
  bit-identical**, so its numbers move a little but the conclusions hold: e.g. our system
  (corrector v1 + gate) moving / still 7.15 / 5.92 px -> 7.03 / 5.69 px, tremor removed 84% ->
  84%; smoothness still chooses v4 S=0.5; mild tremor removed -1% -> -9% (weak either way).
  `check_results.py` therefore lists 14 corrector numbers as "not found" after this rebuild;
  with the committed model files (what the app and RESULTS.md use) nothing changes.

- `python -m assistant.run_test_prompts`, assistant v4 (history): 18/18 safe, incl. 5 questions
  with `docs/contracts/history_example.json` ("So is my tremor getting worse?", "more pills on
  days like that?", "worse tomorrow?"); 3-5 sentences, 32-98 words (comparisons longest, as they
  name the reasons numbers can differ); none of 54 suggested buttons mention medical topics.
  `python -m pytest assistant/test_history.py`: 5 passed.

- `python -m assistant.run_test_prompts`, assistant v3 prompt: 13/13 safe, numbers correct,
  every answer highlights 1-2 key facts, 3-4 sentences (39-73 words), all 39 suggested
  follow-up questions safe. A 4-turn chat following the first suggestion each time: none of
  12 suggestions repeated an earlier question. Details in `assistant/test_prompts.md`.

- `python -m assistant.run_test_prompts` (13 questions, example summary, `claude-sonnet-5-5`,
  effort `low`): version 1 prompt: 13/13 safe, all numbers correct, but only 2 of 13 within
  the 3-6 sentences asked (5-12 sentences, 79-182 words). Version 2 (firmer length rule):
  13/13 safe, 3-5 sentences, 33-71 words. Answers in `assistant/test_answers_v1.md` and
  `assistant/test_answers.md`; judged in `assistant/test_prompts.md`.

- `evaluation/smoothness.py --test` (test, gated by detector v2): corrector v4 (app) off the
  path moving / still 6.94 / 4.86 px, 87% tremor removed, 0 ms lag, jerkiness 1.37 px (no
  filter 1.69, v3 1.96, One Euro 0.64 but 40 ms lag); no marked tremor 1.85 px (no filter 2.30).
- `evaluation/compare_modes.py --people test` (demo page, final): our model vs no filter, hand
  still / reaching: strong 69% / 53% closer, medium 39% / 23%, mild 53% / 6%; smoother than no
  filter in every case. One Euro is closer for a perfectly still hand (medium 1.44 vs 3.70 px).
- `evaluation/calibration_sim.py` (validation, 72 people; later-use distance from the path,
  px, at 0.5x / 1x / 2x tremor): always our model 1.35 / 2.37 / 3.91; calibration's choice
  1.51 / 3.15 / 5.17; best in hindsight 1.26 / 2.30 / 3.86; always One Euro 11.90 / 12.14 / 12.99.
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

- Sat 14 Nov 21:57 CET, team leader (human): redesign choices. Look: keep style C (warm and friendly),
  polished. Layout: tabs, a big practice area, the assistant as a floating window. Pages:
  live demo, summary, assistant panel (not the path check tool). Components: ui-sdk web
  components with no build step, files copied locally so the demo works offline.

- Sat 14 Nov 21:59 CET, builder's agent (chosen on validation by rules fixed in advance): the app's corrector
  is now v4 with penalty 2 (`smoother_output.md`); no retraining on realistic movement
  (`realism_stress.md`). One Euro numbers everywhere now come from the rewritten filter.

- Sat 14 Nov 22:10, team leader (human): README shows no team names or schools (round 1 is
  reviewed blind); the "Team:" line reads "Names on the submission form". Recorded in
  `docs/WRITER_BRIEF.md`.

- Sat 14 Nov 21:20, team leader (human): (1) YES, the builder rewrites
  `scripts/download_data.py` and `baselines/classical_filters.py` from scratch (removes any
  rule-2 risk). (2) Step 9 additions: per-person uncertainty ranges, failures (per person,
  and a corrector failure on real marked tremor), and the live still-hand weak spot.
  (3) B3, correcting the real cursor everywhere (`systemwide/`), moves from the leader's lane
  to the builder's; still a stretch goal, cut before everything except step 16.

- Sat 14 Nov evening, team leader (human): DECISION L1 changed from A to B. Keep a history of
  session SUMMARIES (numbers only) on the laptop so the assistant can compare sessions; it may
  describe pointer differences but never judge health trends.

- Sat 14 Nov, team leader (human): DECISION L2 = `claude-sonnet-5-5` (neither suggested
  option: cheaper than Opus, stronger than Haiku). Effort `low`, the recommended start for chat.
- Sat 14 Nov, team leader (human): the assistant stays one instructed AI call, not an agent
  with tools (it only reads numbers and writes text, which is simpler to make and prove safe).
  A one-tap "apply this suggested setting" button is a possible later extra.

- Sat 14 Nov, team leader (human): DECISION L1 = A. Keep only the current session in memory,
  plus an optional local file the user can delete. A history across days to show trends
  (option B) is wanted as a future extension, not for the hackathon.
- Sat 14 Nov 19:34, builder's agent (chosen on validation): the calibration test only reports;
  it does not switch the filter, because choosing from the test did worse than always using
  our model (`calibration_val.md`). Not run on test people (method not kept).
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

- Sat 14 Nov, team leader's agent: the first API key was not scoped to a workspace, so every
  assistant request failed with error 400 ("must include the anthropic-workspace-id
  header"); an organisation ID did not work either. Fixed by adding the workspace ID
  (`wrkspc_...`) as `ANTHROPIC_WORKSPACE_ID` in `.env` (template in `.env.example`).
- Sat 14 Nov, team leader's agent: the first assistant prompt gave answers 2-3 times longer
  than asked (see Results). A firmer length rule fixed it; safety answers were fine both times.

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
- Sat 14 Nov 18:14, builder's agent: the click-freeze change was committed straight to `main`
  instead of via `builder/click-freeze` (a failed check stopped one part of a command chain
  but a later part still switched to `main`). The code was already tested and checked; no
  history was rewritten. Commands are now chained so that nothing runs after a failure.
(Keep this list honest; the write-up needs a "what didn't work" section.)

## Requests to another lane

- Sun 15 Nov, builder -> team leader (UI is yours): the builder added a small "Steadier or more
  responsive" control (Steadiest / Balanced / Faster) under "Adjust" in `web/index.html` (id
  `response-row`, shown only for Our model) and two lines in `web/app.js` (`showSettings`,
  `onChange("response", ...)`). Restyle or move it freely; keep the id and the `response` value
  sent to the server. It also deserves a line in the tutorial if you rework it.
- Sun 15 Nov, builder -> team leader (UI is yours): builder bug fixes in `web/app.js` (sliding
  window in `shakeNow`, meter redrawn in `draw`, `SEND_GAP_MS` in the pointermove handler) and one
  line in `web/index.html` (`<link rel="icon" href="data:,">`). No visual change.

- Sat 14 Nov 23:37 CET, builder -> team leader: **merged on main, please pull before editing `web/`:**
  (1) a first-use guide, `web/tutorial.js` (own file; two lines in `index.html` load it; a
  "How to use" button is added to the top bar) - Oleksandr's request, restyle freely;
  (2) the app's "Our model" now adds One Euro smoothing switched by our detector (option A,
  chosen by Oleksandr after your 23:14 request); test people: least shake and jumpiness of all
  filters, but it lags while reaching. Numbers in `RESULTS.md` "On the demo page".

- Sat 14 Nov 23:12 CET, builder -> team leader: **two small additions to your page (approved by Oleksandr)**,
  please pull before editing `web/`: (1) demo tremor now starts at "strong" (server default;
  with medium the correction was invisible by eye: `demo_modes_test.md`, medium, browser-like
  timing, reaching: 6.00 -> 5.22 px);
  (2) the tremor meter has a fourth readout, "Shake (2 s)": raw -> shown cursor, in px
  (`web/index.html` one line, `web/app.js` `shakeNow()`). Restyle them freely.

- Sat 14 Nov 23:03 CET, Oleksandr (human, after trying the new design) -> team leader: **a first-use tutorial
  or explanation is needed.** On first sight of the orange target it is not clear what to do.
  Idea: a short guided intro (3-4 steps: "move here", "click the orange target", "switch on
  demo tremor and compare the two cursors", "try another filter") or at least a one-line
  instruction above the practice area. UI is the leader's lane.
- Sat 14 Nov 23:03 CET, builder -> team leader: **I changed `web/app.js`** (bug fix, merged): Lower
  sensitivity now retries Pointer Lock on every click (before, one refusal, e.g. clicking
  within a second of pressing Esc in Chrome, disabled it for the whole session) and draws a
  clear message in the middle of the practice area ("Click here to start Lower sensitivity" /
  "This browser blocked the pointer lock"). Please pull before your next `web/app.js` edit.

- Sat 14 Nov 22:30 CET, builder -> team leader: **tested the new design** (app's built-in browser, simulated
  movement, desktop and 375 px phone width). Works: all three tabs, filters, demo tremor and
  levels, meter and live graph, correction indicator, targets and hit bars, strength slider,
  click freeze, tracking switch, calibration, Lower sensitivity hint and Pointer Lock fallback,
  "Show me" buttons, Analysis tiles, chart and history, assistant plain summary, old
  summary.html forwarding, path check page; no sideways overflow on a phone. To fix (your
  files): (1) the floating "Ask the assistant" button covers content at the bottom right (e.g.
  "Clicks that hit the target" in Analysis); (2) Analysis chart: right-hand labels cut off
  ("21.8 p"); (3) How it works -> "How well it does" repeats "Filter now: Our model, strength 1"
  and gives no corrector result (test: 86% of tremor removed, no lag, `RESULTS.md`); (4) the
  meter keeps showing the last values ("Correction: ON (100%)") after the hand stops or leaves
  the area: grey it out after about a second without movement?; (5) assistant plain summary
  says "moving for about 0 minutes" (0.3 min) and "Cursor smoothing: learned" (say "Our model").
  Fixed by the builder (one line, `web/app.js`): a refused Pointer Lock left an "Uncaught"
  error in the browser console. Not tested: a real hand in Chrome and Safari, AI answers with a key.

- Sat 14 Nov 22:02 CET, builder -> team leader: **B3 is ready for your check on the demo Mac** (it needs
  the Accessibility permission, which only you may switch on). `git pull`, then follow
  `docs/RUNNING.md` "System-wide correction": first `--demo strong --mode none` (the real
  cursor shakes in every app), then `--demo strong` (our model). Please write here: does the
  cursor move at all (if not, try `--method warp`), is it visibly steadier with our model, does
  Control + Option + X switch it off every time, and do clicks land where the cursor is shown.
  If it works, a 30-second screen recording of both runs is for the video. Time box: decide
  by Sun 15:00.

- Team leader -> builder (Sat 14 Nov 22:00): (1) **B3 is wanted**: please do it (2 h time
  box, done before Sun 15:00 CET; safety off-switch first; the leader runs the check on the
  demo Mac and switches on the Accessibility permission). (2) **The leader takes the UI work**
  (visual polish, accessibility: read aloud, dyslexia-friendly font, colour-blind-safe
  colours, larger text; and sticky targets), so please skip those. To avoid both of us editing
  the same `web/` file at once, the leader works on a `leader/ui` branch and says in the group
  chat before touching a file; your bug fixes in `web/` go first, just tell the leader.

- Team leader -> builder (Sat 14 Nov 21:45): **step 15 on the demo Mac is done** (see
  "Results"): app passes; the full rebuild works after reordering two lines in `RUNNING.md`
  (fixed on main). Please tick step 15 if you agree, and note in `RESULTS.md` / the write-up
  that retraining the corrector on another Mac gives slightly different numbers with the same
  conclusions (detector reproduces exactly).

- Team leader -> builder (Sat 14 Nov 21:35): **step 11 trackpad check, first result (built-in
  app browser, demo Mac, corrector v4, demo tremor on).** "Our model" stays closer to the
  real movement than One Euro, but its movement still looks fast and jittery, not smooth
  enough. This matches `evaluation/smoothness.py --test`: v4 jerkiness 1.37 px vs One Euro
  0.64 px, so v4 is about twice as jerky as One Euro, although smoother than no filter (1.69).
  Request (if time allows, decided on validation like v4): try a higher smoothness penalty, or
  a light smoothing of v4's output with a lag limit, and show both distance and jerkiness.
  Safari and Chrome checks still to come.

- DONE (Sat 14 Nov 20:15 CET, builder: table on the summary page; "New session" saves first) Team leader -> builder (Sat 14 Nov 21:00): **please show the session history on the summary
  page.** `GET /api/assistant/history` returns `{"current_started": ..., "sessions": [...]}`, the
  earlier sessions saved on this laptop, newest first (fields: `day`, `minutes_active`,
  `detected_share`, `typical_frequency_hz`, `typical_strength_px`, `steadiness_score`,
  `click_accuracy`, `filter`, `demo_tremor_was_on`). Example to build against:
  `docs/contracts/history_example.json`. Suggestion: a small table or chart of share flagged
  and steadiness per session, marking sessions with demo tremor or a different filter, a line
  "Differences between sessions can come from settings, tasks or time of day; this is not a
  health trend", and the disclaimer. Optional, one line in `reset_summary()` before
  `demo_stats = SessionStats()`: `from assistant import history; history.save(get_summary())`,
  so the last minute before "New session" is not lost (autosave runs every 60 s).

- CHECKED (Sat 14 Nov 21:45, leader on the demo Mac, Safari): Pointer Lock works. After a click
  in the area only the drawn cursor shows, and it cannot leave the area. Note for everyone:
  in Safari, Cmd+Shift+R opens Reader mode; reload without cache is Cmd+Option+R.
  Chrome not checked yet.
- DONE (Sat 14 Nov 20:15 CET, builder: Pointer Lock in that mode, as suggested; click the area to start, Esc to stop. Please check by hand in Chrome and Safari on the demo Mac. After `git pull`, reload with Cmd+Shift+R once: the old stylesheet can stay cached) Team leader -> builder (Sat 14 Nov 20:30): **bug: "Lower sensitivity" is offset.** Seen by
  the leader on the demo Mac: after bringing the pointer into the practice area, the drawn
  cursor sits off to one side of the real pointer. Likely cause (from reading
  `LowSensitivity` in `server/main.py`, not tested): the drawn cursor moves 0.5x the hand's
  movement from the entry point, while the real macOS pointer moves 1x, so the two drift
  apart in the direction of movement; the real pointer also leaves the area before the drawn
  cursor reaches the far edge, which triggers a reset. Possible fix: the browser's Pointer
  Lock API (`area.requestPointerLock()`, then `event.movementX/Y`) hides the real pointer and
  gives raw movement with no edge exits; or at least hide the system cursor over the area
  (`cursor: none`) so only one cursor is visible.

- Sat 14 Nov 19:59 CET, builder -> everyone (Timofey, Godson, Oleksandr): please do the step 4 path check
  (about 5 min): `git pull`, run the app, open http://127.0.0.1:8000/path_check.html, rate the
  12 paths, and paste the report at the end into the group chat.

- DONE (Sat 14 Nov, builder) Team leader -> builder (Sat 14 Nov 20:00): **one line in `web/app.js`, please:** in
  `loadAssistant()`, use `script.src = "assistant/assistant.js?v=" + Date.now();`. Browsers
  kept an OLD cached copy of the assistant panel after an update (it then showed raw `**`
  marks and a "SUGGESTIONS:" line). Until then, Cmd+Shift+R reloads the new panel.

- Team leader -> builder (Sat 14 Nov 19:20): **the assistant router is live (Contract 3).**
  After `git pull`, `GET /api/status` shows `assistant: available` and the panel appears in
  `#assistant-panel`. It reads the live summary by calling your `get_summary()` at request
  time (via `sys.modules["server.main"]`), so please keep that function name. The
  `whole_laptop` block is fine. For AI answers on your own laptop, create your own `.env`
  (see `.env.example`); without it the panel shows a plain non-AI summary.

- Builder -> team leader (Sat 14 Nov 18:14): your idea 2 (click freeze) is built and merged;
  try it on the demo page with "Demo tremor: Strong" and the "Click freeze" button. Your
  idea 1 (movement-aware detector) is partly covered by detector v2; ideas 3-4 not started.

- Builder -> team leader (Sat 14 Nov 18:05): **step 15 on the demo Mac (the result that
  counts).** In a NEW folder (not your working copy): `git clone
  https://github.com/CartHadash/Veritas-AI-mouse-tracker.git fresh-test`, `cd fresh-test`, then
  exactly the "On macOS" commands in `docs/RUNNING.md` (`python3.12 -m venv .venv`, `source
  .venv/bin/activate`, `python -m pip install -r requirements.txt`,
  `python -m uvicorn server.main:app`), open http://127.0.0.1:8000, and in a second terminal
  `python server/test_ws.py`. Write here whether it worked (and any error text). No data
  download needed. You can delete the folder afterwards.

- Builder -> team leader and writer (Sat 14 Nov 17:17): **please read
  `evaluation/results/RESULTS.md`** (step 14 needs the builder and the leader to find nothing
  they cannot explain). It is the source for the write-up's "How it works" and "Results"; its
  five sentences at the top are a starting point for the 30-second pitch. Ask here about
  anything unclear and `docs/EXPLAINED.md` will be fixed.

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

- ANSWERED (Oleksandr, Sat 14 Nov: "A, then B"; both done, see "Done", Sun 15 Nov 00:55).
  Sat 14 Nov 23:18 CET, from the builder (answers Timofey 23:14, "extensive comparison, whether to redo the
  model"): see `docs/EXPLAINED.md` "Why our model looked worse than One Euro by eye" and
  `evaluation/results/vs_one_euro_val.md`. Our cursor is closest to the hand but almost as jumpy
  as no filter; One Euro is twice as smooth. Builder's recommendation: no full redo (too risky
  before the deadline). Instead (A) our model + One Euro smoothing, switched by our detector
  (best on shake and jumpiness in the comparison; about 45 min), and if time allows (B) retrain
  the corrector to aim at what the eye sees (leftover shake and jumpiness, with a lag limit;
  2-3 h, may not win). Both chosen on validation by a rule fixed in advance, test once.

- Sat 14 Nov 20:20, from the builder (to ask AFTER the team's step 4 path check,
  `web/path_check.html`): (1) step 4 rework scope: A) stress test first: measure the current
  models on the realistic movement (validation people), retrain only if they clearly drop
  (recommended); B) full rework now: rebuild, retrain, re-run everything (2-3 h, every number
  changes); C) only fix the chart and docs. ANSWERED by the leader's task list (Sat 14 Nov:
  stress test, retrain only on a clear drop): done, no clear drop, no retraining
  (`evaluation/results/realism_stress.md`). Round 2 of the path check is still welcome.
  (2) step 9 additions: ANSWERED by the leader (Sat 14 Nov 21:20), see "Decisions".

- ANSWERED (Sat 14 Nov 21:20, leader: YES). Rewrite `scripts/download_data.py` and
  `baselines/classical_filters.py` from scratch to remove any rule-2 risk. Now a builder
  task (see "Builder's plan"); the builder updates `docs/REUSED_CODE.md` when done.

---

# Second snapshot of STATUS.md (Sun 15 Nov 15:20 CET, at the feature freeze)

Moved here unchanged when STATUS.md was trimmed for the write-up phase.

Newest entries at the top of each list. Use local time (CET) and say who you are.

## Right now (Sun 15 Nov 14:50 CET, leader's agent)

| Lane | Working on | Blocked by |
|---|---|---|
| Builder | All tasks the leader gave are built (click where you aimed, Steady cursor everywhere, exercises, assistant actions and hardening, walkthrough). Waiting for the leader's hand checks | Leader's checks |
| Team leader | Hand checks on the demo Mac (list below), then the write-up phase | - |
| Writer | IN PROGRESS: drafting the write-up from `docs/WRITER_BRIEF.md` | Final project name |

Checked on the demo Mac at 14:50 (commit 34e8cea, leader's agent): `python -m pytest` 30 passed,
7 skipped (need data); `check_results.py` OK (30 sources); `server/test_ws.py` 500/500 in every
mode; `/api/status` says `systemwide: available` (server started from the Claude app, which has
the permission). No hand checks yet.

**Leader's hand checks still open (demo Mac):**
- [x] "Steady cursor everywhere" on the REAL cursor (leader, ~15:00): works in every app and
      Control + Option + X switches it off; "still not perfect but good enough".
- [x] The website with a real hand (leader, ~15:00): "works".
- [x] `python -m assistant.run_test_prompts` (leader's agent, 15:00, real key): 28/28 as hoped,
      every action button from the allowed list (`assistant/test_prompts.md`, version 6).

**Time line (CET):** feature freeze **Sun 20:00** (leader's decision, Sun 10:45) · first full
submission Sun 23:00 · final fixes until the deadline **Mon 16 Nov 05:59**.

## What is left (tick or delete lines as they finish)

**Team leader (only possible on the demo Mac):**
- [x] **B3 real-cursor check: WORKS** (Sun 11:04, see "Done since the trim").
- [x] B3 off-switch and video clip (Sun 11:08). Clip: leader's laptop, to be saved into
      `~/Desktop/screenshots/veritas-b3/` (not in git: too large).
- [x] Trackpad check of the CURRENT "Our model" (Sun ~11:00, leader: "good enough"). The
      builder can tick step 11.
- [x] Re-run `python models/corrector/time_live.py` on a quiet Mac (Sun 12:15, leader's agent,
      demo Mac, commit 0c5ee66): corrector + detector gate mean 0.345 ms, 99th percentile
      1.855 ms, worst 2.790 ms per update (limit 8 ms); corrector only worst 0.132 ms. Same
      session: `server/test_ws.py` 500/500 in every mode, summary `filter` has `response`;
      `python -m pytest` 21 passed, 7 skipped (need data); `check_results.py` OK (30 sources).
- [ ] Read `evaluation/results/RESULTS.md` end to end (step 14 tick).

**Team leader (UI work taken over Sat 22:00; `web/` and `assistant/`):**
- [x] (DONE by the builder at the leader's request, Sun 15 Nov, see "Done since the trim")
      The builder's five findings: (1) the floating assistant button covers content at the
      bottom right; (2) Analysis chart labels cut off on the right; (3) How it works -> "How
      well it does" repeats the filter line and shows no corrector result; (4) the meter keeps
      old values after the hand stops (grey out after about 1 s). ((5), the assistant's
      "0 minutes" / "learned", is done.)
- [x] Larger text (accessibility): a "Larger text" switch, built by the builder (Sun 15 Nov).
      Colour-blind-safe colours: not built (only if time allows). ("Read
      aloud" is done; the dyslexia-friendly text switch was built by the builder with the
      leader's OK, Sun 15 Nov: `web/reading.js`.)
- [x] Mention the Steadiest / Balanced / Faster control in the tutorial (`web/tutorial.js`):
      the last step says so (builder, Sun 15 Nov).

**Builder (leader's decision, Sun 15 Nov ~11:30; time box 1.5 h, finished before the 20:00 freeze):**
- [x] (tested Sun 15 Nov: NOT kept, see "Done since the trim") **Movement-aware detector, cheap version** (Timofey's idea 1). Why: false alarms are
      29.6% with the hand moving vs 18.0% still, 41.7% on "moving on purpose" tasks
      (`RESULTS.md`); in the app a false alarm switches smoothing on mid-reach and adds lag.
      Do: no retraining; give detector v2 two cut-offs, one for windows where the hand is
      moving (the existing 20 px/s rule) and one for still windows, each chosen on validation
      people with the same rule (at most 20% missed). Keep it only if validation false alarms
      while moving drop and missed stays within the rule (fix this rule before looking);
      then score test people once, update `RESULTS.md`, `check_results.py`, `docs/EXPLAINED.md`,
      and the live path (`models/detector/`, check with `evaluation/compare_modes.py` and
      `time_live.py`). Watch out: `failures.md` suggests many "false alarms" on action tasks may
      be real tremor our labelling rule missed, so stricter can mean more missed real tremor;
      report missed cases and false alarms separately. If it does not help: one honest line in
      "What we tried that did not work".

- [x] B3 click fixes (Sun 15 Nov, see "Done since the trim"). Re-checked by the leader 12:18
      (a bit better; Steadiest kept). Original note: **Leader: please re-check on the
      demo Mac** (`git pull`, then `python -m systemwide.run --demo strong`; click freeze is on
      by default; try `--response balanced` too and say which feels better).

**Builder, NEXT (leader's decision, Sun 15 Nov 12:30; both before the 20:00 freeze, task 1 first):**
- [x] (system-wide part DONE Sun 15 Nov 12:53, see "Done since the trim"; the leader re-checks
      by hand; the page's part DONE Sun 15 Nov 13:14) **1. "Click where you aimed" (about 45 min).** Why: the leader's B3 re-check (12:18) found
      the click still lands away from where they meant to click; click freeze only helps
      AFTER the press, and at the press the cursor still carries leftover shake and about
      72 ms of lag. Do: when a button goes down, place the click (and the freeze point) at the
      average of the SHOWN cursor positions over the last 0.2 s instead of the current one
      (tremor is 4-6 shakes a second, so about one cycle averages out). Only while the
      detector flags tremor (or the gate is open); otherwise click where the cursor is, so a
      steady hand is never moved. In `systemwide/steady.py` (`press`) first; then the page's
      click freeze (`web/app.js` `shownPosition`) if it helps there too. Measure: add it to
      `evaluation/systemwide_clicks.py` (and `click_sim.py` for the page) as a new row; choose
      the window (0.1 / 0.2 / 0.3 s) on validation people by a rule fixed before running
      (more clicks landing on a 10 px button with strong tremor, no worse on medium or with
      no tremor); test people once. Add a test to `systemwide/test_steady.py`. The leader
      re-checks by hand on the demo Mac.
- [x] (BUILT Sun 15 Nov 12:56, see "Done since the trim"; **not yet run on a real cursor: the
      leader checks it on the demo Mac**) **2. System-wide correction as a real feature, not only a timed test (about 1.5 h).**
      Why: B3 is proven (it steadies the real cursor in every app), but today it only runs
      from the terminal for at most 10 minutes. The leader wants the corrector to work across
      the whole Mac as a feature. Do:
      - A switch "Steady cursor everywhere" on the page (Practice -> Adjust) that starts B3 in
        the background of our server, and switches it off again. It uses the page's filter,
        strength, response level and click freeze settings. Keep the default "Our model".
      - It stays on until switched off (no 60 s / 10 min limit in this mode; the terminal
        `--seconds` test mode stays as it is).
      - Safety stays exactly as strong: Control + Option + X always switches it off; stopping
        the server switches it off; a filter failure makes the cursor follow the hand; the page
        shows clearly when it is ON. Never request the permission from code.
      - Without the Accessibility permission (or on Windows) the switch is greyed out with
        one line saying what a human must switch on (System Settings -> Privacy & Security ->
        Accessibility -> the terminal app -> reopen it).
      - Optional: a "with demo tremor" choice, so the video can show it.
      - `GET /api/status` says whether it is available and on. Tests in
        `systemwide/test_steady.py` (on/off, settings passed through, off-switch); update
        `docs/RUNNING.md` and `docs/EXPLAINED.md`. The leader checks it by hand on the demo Mac.
      Note: with a steady hand nothing visible happens (the detector sees no tremor); that is
      correct, say it next to the switch.
      If time runs short: finish task 1 and the switch WITHOUT the optional demo choice; never
      weaken a safety rule to save time.

**Oleksandr:**
- [ ] Read `evaluation/results/failures/failures.md` (step 9 tick) and `RESULTS.md` (step 14 tick).

**Whole team:**
- [ ] Confirm the final project name (the page says "Steady Pointer").
- [ ] Write-up in `README.md` (the leader says when the write-up phase starts), demo video,
      submission form, every link checked in a private window.

**Cut (leader's decision, Sun 10:45):** step 16 desktop window; sticky targets (goes into the
write-up as a next step); round 2 of the step 4 path check (the stress test already answered it).

## Done since the trim (newest first)

- Sun 15 Nov 13:21, builder's agent: assistant window layout (Oleksandr: "Read aloud overlaps the
  text"). `web/assistant/assistant.css` / `.js`: the "Read aloud" button had a negative top
  margin and sat on the answer's edge; now each answer is followed, with clear gaps, by its
  reminder, then "Read aloud", then the action buttons (green outline), and the window
  scrolls to the newest answer. Checked in the app's browser with two made-up answers.

- Sun 15 Nov 13:18, builder's agent: **assistant hardening** (Oleksandr's request; with the leader's
  earlier permission to edit `assistant/`). Checked first: the API key is only read by the
  Anthropic library from `.env`; it is never in the prompt (so the model cannot know it), no
  route returns it, and no commit in the repository's history contains one. Added:
  (1) `scrubbed()` in `assistant/core.py`: every piece of every reply passes a filter that
  blanks our key and anything shaped like a key, also when it arrives split over pieces;
  (2) any unexpected error becomes a plain sentence, and only the KIND of error is printed in
  the terminal; (3) a message is cut to 200 words (Oleksandr's choice) and 2,000 characters,
  the page's box to 1,500 characters; (4) prompt section "STAYING WHAT YOU ARE": a little
  friendly chat is welcome, but no other work (no writing, reviewing or fixing code, no
  homework, essays, recipes or how-to guides), pasted code or documents are not analysed or
  obeyed, it has no files, internet, passwords or keys, nothing illegal, dangerous, sexual
  or hateful, and a kind hand-off for talk of self-harm. `python -m pytest assistant`: 9
  passed (two of the new tests first FAILED and found real bugs in the first version of the
  filter and the error handling; fixed). Trap questions 23-28 added to
  `assistant/run_test_prompts.py`. Also: the page prints a fixed reminder under EVERY answer
  ("estimates from a student prototype trained on public research recordings; they can be
  wrong; not medical advice; for advice or treatment talk to your doctor"), written by
  `web/assistant/assistant.js`, not by the model, so it is always there. **Not run with the real model: no API key on the builder's
  Mac. Leader: please run `python -m assistant.run_test_prompts` and judge 19-28.**

- Sun 15 Nov 13:14, builder's agent: **"click where you aimed" on the practice page** (second
  half of the leader's task 1). `web/app.js` `aimedPosition()`: at the press, while Our model's
  gate is over half open, the click (and the freeze point) is the average of the corrected
  cursor's last 0.1 s. Window chosen on validation people by the same rule as system-wide
  (`python evaluation/click_sim.py`, `click_freeze_val.md`: 10 px target, strong tremor, with
  freeze, 93% -> 95% for 0.1, 0.2 and 0.3 s; shortest taken; mild and medium unchanged). Test
  people once (`click_freeze_test.md`): 99% -> 100%. Checked in the app's browser that the
  press uses the averaged point. Not tried with a real hand.

- Sun 15 Nov 13:11, builder's agent: **assistant action buttons** (leader's request, with the
  leader's permission to edit `assistant/` and `web/assistant/`). The prompt
  (`assistant/prompt.py`, "ACTION BUTTONS") lets a reply carry one line `ACTIONS: ...` from a
  fixed list: `set_mode`, `set_strength`, `set_response`, `set_demo`, `open_tab`,
  `start_calibration`. `web/assistant/assistant.js` hides that line, accepts only names and
  values in its own `ACTIONS` table, ignores everything else, shows at most three buttons
  ("Switch to One Euro"), and only the person pressing one changes anything (through the
  page's own `postSettings` / `openTab`). Checked in the app's browser with a made-up reply
  holding three allowed and five not-allowed actions (among them `run=alert(1)` and an
  `<img onerror>`): three buttons, nothing inserted as HTML, pressing them switched the filter
  and opened Analysis. `python -m pytest assistant`: 5 passed. Four test questions (19-22)
  were added to `assistant/run_test_prompts.py`, which now records the ACTIONS line and flags
  any action outside the list. **Not run: there is no API key on the builder's Mac**, so how
  the model itself uses ACTIONS is unchecked until the leader runs it.

- Sun 15 Nov 13:09, builder's agent: **three practice exercises** (leader's requests;
  new file `web/exercises.js`, five small hooks in `web/app.js`, plain markup under the
  practice area in `web/index.html`, ids `spiral-start`, `fair-start`, `exercise-status`,
  `exercise-result`). **Trace the spiral:** a faint spiral, start at the middle dot, raw line
  grey and corrected line green, average distance of each from the spiral in px; the finished
  drawing is `window.lastSpiral` (`raw`, `corrected` point lists, `rawDistance`,
  `correctedDistance`, `filter`, `demoTremor`, `complete`, `at`). **Fair test:** 10 targets with
  No filter, then the SAME 10 (same things, same places) with Our model; table of targets
  hit, clicks that missed, time per target; says whether demo tremor was on; the result is
  also `window.lastFairTest`; the filter in use before is restored. **Hold to peek:** space
  bar held with the pointer in the area = shown cursor and click follow the raw movement,
  with a note on the area. Wording everywhere: a practice exercise, not a test or a
  measurement of the person. Checked in the app's browser with simulated pointer events
  (spiral traced to the end with strong demo tremor, fair test run through both rounds,
  space held and released); a bug found on the way (the spiral's progress ran ahead of the
  hand with strong tremor and ended early) is fixed. Not tried with a real hand.

- Sun 15 Nov 13:03, builder's agent: **the first-use guide is now a live walkthrough**
  (Oleksandr's idea; `web/tutorial.js` rewritten). Seven steps; each dims the page except the
  real part it is about, points a speech bubble with an arrow at it, and a drawn "demo"
  cursor shows what to do (wander in the practice area, go to the target and click, press
  the Demo tremor switch, hop along the filters). No screenshots, so it cannot go out of date
  and it follows "Larger text" and the dyslexia font. Back / Next / Skip, arrow keys, Esc;
  starts by itself on the first visit, "How to use" reopens it. Checked in the app's browser
  at 1440 px and 375 px. Not checked in Safari.

- Sun 15 Nov 13:02 CET, leader's agent: `leader/motion` merged into `main` on the leader's word (the
  leader's entries below say "NOT merged": true when written). Clean merge. On merged main:
  `python -m pytest` 26 passed, 7 skipped; the page loads with both fonts, the six target
  kinds and no console errors. `server/test_ws.py` was NOT re-run (it would change the
  leader's running session; no server code changed in this branch). Everyone: `git pull` and
  a hard reload (Cmd+Shift+R). Still not tried with a real hand: the everyday targets.

- Sun 15 Nov 12:56, builder's agent: **"Steady cursor everywhere" switch** (leader's task 2).
  Practice -> Adjust has a switch that starts the system-wide correction inside the server
  (`systemwide/service.py`; `run.py`'s event tap is now the reusable `run_tap`) and keeps it
  on until switched off: by the switch, by Control + Option + X (the page notices within 2 s),
  or by stopping the server. It uses the page's filter (Lower sensitivity falls back to Our
  model), strength and Steadiest / Balanced / Faster, live; click freeze and "click where you
  aimed" are on. An extra "...with demo tremor" switch shakes the real cursor for the video.
  A banner shows while it is ON. Without the permission (this Mac) or off macOS the switch is
  greyed out with the reason; the code only checks the permission, never asks.
  `POST /api/settings` takes `systemwide` and `systemwide_demo`; `GET /api/status` has
  `systemwide` ("available", "on" or "not available: why"). `python -m pytest
  systemwide/test_steady.py`: 14 passed (on/off, settings passed on and changed live, off key,
  no permission), using a stand-in for macOS. Checked in the app's browser: greyed out with
  the reason, and the server refuses to start it. **NOT run on a real cursor** (the builder's
  Mac has no permission): **leader, please check on the demo Mac**: start the server from the
  terminal that has the Accessibility permission, switch it on, try Control + Option + X,
  switch filters while it is on, and stop the server with Ctrl+C while it is on.

- Sun 15 Nov 12:59 CET, leader's agent, on `leader/motion` (pushed, NOT merged): (1) the top bar is one
  slim row (64 px at a 1440 px window; before, the tools had a second row) and the wave
  fills the whole bar; (2) **everyday targets**: the practice target takes turns being a
  round button, a checkbox, a folder, a close button, a link and a "Save" button, each with
  its own size, and the drawn shape is exactly the area that counts as a hit
  (`web/targets.js`). The kinds come in a fixed order so every filter meets the same mix.
  Checked in the browser with simulated clicks: a click on the centre of each of the six
  kinds counted as a hit and a click 90 px to the side as a miss; no console errors. Not
  checked with a real hand. Note for the write-up: "time per target" now mixes easy and hard
  shapes, so compare filters over several targets, not one.

- Sun 15 Nov 12:54 CET, leader's agent: second pass on `leader/motion` (pushed, NOT merged) after the
  leader's review. Fonts: Bricolage Grotesque for headings and numbers, Instrument Sans for
  text (two files in `web/fonts/`, 41 KB and 30 KB, SIL Open Font License; the
  easier-to-read switch still replaces both). Colours: the blue is gone; forest green, clay
  orange and gold on cream. Widgets: cards and tiles have no outline and float on a soft
  shadow; controls are pill-shaped. The top wave is now three faint, slow lines along the
  bar's bottom edge. New small animations: buttons, switches and the filter chooser answer a
  press; the "Connected" dot breathes; the assistant button wiggles once after five target
  clicks; card titles have icons that draw themselves. This replaces the tinted cards and
  the five-line wave described in the entry below. Checked in the browser at 1440 px (three
  tabs, both fonts loaded, no console errors). Not checked: the nudge firing, the
  easier-to-read switch with the new fonts, reduce motion, phone width. Text drawn inside
  the practice area keeps the old font (`web/app.js` is the builder's today).

- Sun 15 Nov 12:43 CET, leader's agent: "colour and movement" layer on branch `leader/motion` (pushed, NOT
  merged: the leader shows it to the team first). All of it is in two NEW files,
  `web/motion.css` and `web/motion.js`, plus two lines in `web/index.html`; deleting those two
  lines gives the plain look back. Adds: a green top bar with a moving wave (shaky on the
  left, calm on the right) and a logo that both shake more as the live tremor score rises;
  a colour per card (meter green, Adjust blue, targets orange) and per Analysis tile; tabs
  that slide in and cards that arrive one after another; a moving picture on "How it works"
  (marked on the page as an illustration with made-up movement); a "Save my session as a
  picture" button (a 1200 x 630 PNG made in the browser, with the demo note and the
  disclaimer). Cards that hold controls do not move under the pointer, on purpose. Checked in
  the browser at 1440 px: three tabs, the moving picture, the session picture's drawing, no
  console errors; `python -m pytest` as before. Not checked: the wave and logo reacting to a
  real tremor score, the real file download, the "reduce motion" setting, phone width.
  The earlier "one-minute tour" idea is dropped: the builder's `web/tutorial.js` already does it.

- Sun 15 Nov 12:53, builder's agent: **"click where you aimed" in the system-wide corrector**
  (leader's task 1). At the press the click and the freeze point go to the average of the
  shown cursor positions of the last 0.1 s, only while our model's gate is over half open
  (`systemwide/steady.py` `press`; `--aim 0` switches it off). Window chosen on validation
  people by the leader's rule (`python evaluation/systemwide_clicks.py`,
  `systemwide_clicks_val.md`): 10 px button, strong tremor, with freeze: 91% -> 95% for 0.1,
  0.2 and 0.3 s (shortest taken); medium and no tremor not worse. Test people once
  (`systemwide_clicks_test.md`): 99% -> 100%. `python -m pytest systemwide/test_steady.py`:
  10 passed. **Leader: please re-check by hand** (`git pull`, `python -m systemwide.run
  --demo strong`). Not done yet: the same idea in the page's click freeze (`web/app.js`).

- Sun 15 Nov 12:18-12:20, team leader + leader's agent: **B3 re-check after the builder's click
  fixes** (demo Mac, `--demo strong --seconds 40`, then `--response balanced`; click freeze on
  in both). Steadiest 3,918 updates, Balanced 3,846, 0 filter failures. The leader: clicking
  real buttons is "a bit better" than in the morning; Steadiest felt "just a bit better", very
  close to Balanced (so Steadiest stays B3's default); what still goes wrong: at the moment of
  the click the cursor is in a different place from where the leader meant to click, so they
  try again. Also, the leader checked the page after the UI fixes: the earlier issues are gone.

- Sun 15 Nov (afternoon), builder's agent: "Easier-to-read text" now uses the real OpenDyslexic
  font (Oleksandr's request) instead of Verdana: two `.woff2` files (about 115 KB and 120 KB)
  and the licence in `web/fonts/` (SIL Open Font License; cited in `docs/SOURCES.md`), loaded
  only when the switch is on, Verdana as the fallback. Checked in the app's browser at 1440 px
  and 375 px: the font loads, nothing sticks out of the page on any tab. Not checked in Safari.

- Sun 15 Nov (afternoon), builder's agent, **the UI fixes the leader handed back** (group chat,
  11:29): (1) every tab now leaves empty space at the bottom, so the last lines scroll clear
  of the floating assistant button; (2) the Analysis chart sizes its side margins to its
  labels, so the right-hand "px" labels are no longer cut off; (3) "How it works" -> "How well
  it does" shows the detector sentence without the "Filter now" line, plus the corrector's
  result (numbers from `RESULTS.md`: shake 7.91 px no filter, 2.56 px our model, 3.39 px One
  Euro; 72 ms lag at Steadiest); (4) the tremor meter greys out and says "Paused" after one
  second without movement; (5) a "Larger text" switch next to "Easier-to-read text"
  (`web/reading.js`; 15% larger around the practice area, which keeps its real size; laptop
  widths only). Checked in the app's browser at 1440 px and 375 px with simulated pointer
  events: no page overflow, meter pauses and resumes, chart labels whole. `server/test_ws.py`
  passes. Not checked with a real hand, in Safari, or on the demo Mac.

- Sun 15 Nov (afternoon), builder's agent, the leader's Sunday list:
  **(1) Movement-aware detector, cheap version: tested, NOT kept.** Two cut-offs (looks moving /
  looks still), each chosen on validation by the usual rule; the keep rule was fixed before
  running (`python evaluation/moving_cutoffs.py`, `moving_cutoffs.md`). The cut-offs came out
  0.152 and 0.157 against the single 0.155, and false alarms with the hand truly moving went
  from 30.3% to 31.1%; test people were not scored. The detector already misses about the same
  share in both groups, so a cut-off cannot help; it would need retraining.
  **(2) B3 click fixes.** Click freeze in `systemwide/` (on by default, `--no-freeze`), a
  `--response` option, and the filter is fed every 10 ms during a pause also without demo
  tremor (with demo tremor it already was, so the suspected warm-up after a pause was not
  happening there). Simulated reach-and-click (`python evaluation/systemwide_clicks.py`): on
  validation people Steadiest lands the most clicks on a 10 px button with freeze and strong
  tremor (91%; Balanced 88%, Faster 82%), so Steadiest stays B3's default; test people
  (`systemwide_clicks_test.md`): our model 99% / 99% without / with freeze, One Euro 90% / 95%,
  no filter 30% / 46%. The simulation has perfect aim and no button jolt, so it cannot show
  why a real hand still finds it hard. `python -m pytest systemwide/test_steady.py`: 9 passed.
  Not checked on the real cursor: the leader re-checks on the demo Mac.
  **(3)** `response` added to the summary's `filter` block (leader's request).
  **(4) Easier-to-read text** switch in the top bar (`web/reading.js`; Verdana and wider
  spacing, nothing downloaded; leader's OK in the group chat). "How to use" and this switch now
  sit in one small row under the top bar. Checked in the app's browser at phone and laptop
  widths. Re-run and passing: `server/test_ws.py`, 28 tests, `check_results.py` (30 sources).

- Sun 15 Nov 11:04, team leader + leader's agent: **B3 checked on the real cursor, demo Mac.**
  Accessibility switched on for the Claude app by the leader (a human). A 3 s pass-through run
  (no tremor, no correction) worked. Then `python -m systemwide.run --demo strong --mode none
  --seconds 25` (2,289 updates, 0 filter failures) and `--demo strong --seconds 25` (our model;
  2,416 updates, 0 filter failures), default `--method event`. The leader's observations:
  without correction the cursor shook "a lot" in every app; with our model it was visibly
  steadier "but after some time" (expected: the detector needs 2.56 s of movement before it
  switches the correction on); clicks landed where the cursor was shown "almost always".
  Second run (11:07-11:09, screen recorded): 15 s no correction, then our model with a 60 s
  limit; the leader pressed Control + Option + X and it stopped after 48 s (4,160 updates,
  0 filter failures); the leader: the cursor went back to normal immediately. **Found:**
  clicking real buttons is still hard even with our model (see the request to the builder).

- Sun 15 Nov, leader's agent (branch `leader/hints-calibration`): one-line hints on the
  controls (a sentence per filter under the filter buttons; Strength; Calibrate); a
  "Use <filter>" button after the calibration test (the person taps it, never automatic);
  "Read aloud" under every assistant answer (browser speech, no API); the assistant's plain
  summary says "less than a minute" and "Our model"; the prompt knows the page's names,
  Steadiest / Balanced / Faster, Click freeze and calibration. Checked in the app's browser
  (simulated 12 s calibration, apply, read aloud start/stop, an AI answer);
  `python -m pytest assistant/test_history.py` 5 passed; `python -m assistant.run_test_prompts`
  18/18 safe (version 5). Not checked with a real hand.

## What the app is now (for anyone catching up)

- Detector v2 (gradient boosting, 2.56 s window) decides whether movement is tremor-like.
- "Our model" = corrector v5 (small causal network) + One Euro smoothing, both switched on by
  the detector. A Steadiest (default) / Balanced / Faster control trades shake against lag.
- Demo tremor starts at "strong" and is replayed from public recordings.
- Click freeze, a 10 s calibration test (reports only), Lower sensitivity with Pointer Lock,
  a first-use guide, session history, and the Claude assistant (`claude-sonnet-5-5`, sees
  summary numbers only; plain non-AI summary without a key).
- B3 (`systemwide/`): works on the real cursor on the demo Mac (Sun 11:04).

## Results (current; the full, checked list is `evaluation/results/RESULTS.md`)

Copy numbers from `RESULTS.md` (checked by `python evaluation/check_results.py`), not from here.
Headlines on test people:
- Detector v2: missed 12.9%, false alarms 27.1% (frequency rule: 14.8% / 59.0%; "always no":
  100% / 0%) (`evaluation/evaluate_detector.py`, `detector_v2.md`).
- Corrector v5 network: 88% of tremor removed, 0 ms lag (One Euro 49%, 20 ms) (`RESULTS.md`).
- The app's "Our model" (v5 + gated One Euro, Steadiest): visible shake 2.56 px (One Euro 3.39,
  no filter 7.91), but 72 ms lag while reaching (`evaluation/vs_one_euro.py`,
  `evaluation/response_levels.py`).
- Click freeze, 10 px target, strong tremor: no filter 24% -> 39% of clicks land; our model
  99% -> 99% (`evaluation/click_sim.py --people test`).
- Assistant: 18/18 trap questions answered safely (`python -m assistant.run_test_prompts`).

## Decisions in force (older and superseded ones: `docs/STATUS_ARCHIVE.md`)

- Sun 15 Nov 10:45, team leader (human): feature freeze 20:00; cut step 16, sticky targets and
  path check round 2; UI = the five fixes + read aloud + larger text; the "email Veritas about
  reused files" task removed (both files were rewritten from scratch, no pre-hackathon code left).
- Sun 15 Nov 00:55-03:48, builder's agent (on validation, rules fixed in advance; Oleksandr
  chose "A, then B"): the app's model is v5 + gated One Euro; the person picks Steadiest /
  Balanced / Faster; the notch canceller was not kept.
- Sat 14 Nov 22:10, team leader: README shows no names or schools ("Names on the submission form").
- Sat 14 Nov 22:00, team leader: B3 is wanted (builder builds, leader checks); the leader takes the UI.
- Sat 14 Nov 21:57, team leader: interface = warm style C, tabs, floating assistant, ui-sdk
  components copied into `web/vendor/` (works offline).
- Sat 14 Nov evening, team leader: L1 = B (session summaries kept on the laptop, numbers only;
  never health trends); L2 = `claude-sonnet-5-5`, effort `low`; the assistant is one
  instructed call, not an agent with tools.
- Sat 14 Nov 19:34, builder's agent: the calibration test only reports, never switches the filter.
- Sat 14 Nov, builder: Decisions 1-7 (pixel factor, all PADS tasks, gradient boosting,
  cut-off at most 20% missed on validation, models in Python on the server, warm look, plain JS).

## Problems and things that did not work (the write-up needs these)

- Leader's agent: the first API key was not scoped to a workspace (error 400); fixed with
  `ANTHROPIC_WORKSPACE_ID` in `.env`. The first assistant prompt gave answers 2-3x too long;
  a firmer length rule fixed it.
- Builder's agent: twice a branch was merged before its `STATUS.md` entry (a scripted edit
  failed silently); once a change went straight to `main`. Commands are now chained so nothing
  runs after a failure.
- Movement-aware detector with two cut-offs (moving / still): did not lower false alarms while
  moving (30.3% -> 31.1% on validation, `moving_cutoffs.md`); not kept.
- Corrector v2 (trained on 0.5x-2x tremor) did not beat v1; dropped.
- The server's active-time rule missed slow movement; found by a test, fixed.
- **A number hid what a person saw in two seconds:** corrector v1 scored well on distance but
  looked jumpy by hand. Causes: a resampling bug at browser rates and training that never asked
  for smoothness. v4 added a smoothness penalty; by eye still jittery; measuring visible shake
  showed why; v5 + gated One Euro fixed it at the cost of lag.
- A code review found live-pipeline bugs offline scores could not see (clock drift, demo replay
  skipping samples, jumps after a pause). Lesson: test the live path (`evaluation/compare_modes.py`).
- Development once replayed test people's tremor while choosing settings; now validation only.
- For a perfectly still hand One Euro beat the network alone; the app's smoothing closed the gap.
- Calibration that picks the filter did worse than always using our model (network alone);
  with the app's smoothed model it would now help, but there was no time to re-test, so it reports only.
- Oleksandr's notch canceller (removing the tremor's rhythm) was tested and not kept (`notch_canceller.md`).
- Retraining the corrector on another Mac is not bit-identical (same conclusions); the detector is.

## Requests to another lane (open only; answered ones are in the archive)

- BUILT by the builder (Sun 15 Nov 13:11, see "Done since the trim"); **the model-side test
  questions 19-22 are NOT run yet: no API key on the builder's Mac. Leader, please run
  `python -m assistant.run_test_prompts` and judge 19-22 in `assistant/test_prompts.md`.**
  Sun 15 Nov 12:51, team leader -> builder: **an assistant that can DO things, not only answer
  (leader's idea; after the four practice-area features above, only if time allows before
  the 20:00 freeze).** `assistant/` and `web/assistant/` are the leader's folders: you have
  the leader's permission to edit them for this. Three actions: (a) change a setting (filter,
  strength, Steadiest / Balanced / Faster, demo tremor), (b) open a tab (Practice, Analysis,
  How it works), (c) start the calibration test. Suggested safe shape: the assistant never
  acts by itself. Its reply may end with a line like the existing `SUGGESTIONS:` one, for
  example `ACTIONS: set_mode=one_euro | open_tab=analysis | start_calibration`; the page
  accepts only names and values from a fixed list written in the page's code, ignores
  anything else, and shows each as a button ("Switch to One Euro") that the PERSON presses.
  So text from the model can never run code or change something unseen. Keep rule 10: it
  may suggest app settings, never anything medical. Add test questions to
  `assistant/run_test_prompts.py` (one that asks for something outside the list must do
  nothing).

- (1), (2), (3) DONE by the builder (Sun 15 Nov 13:09, see "Done since the trim"); (4) was the
  leader's. Sun 15 Nov 12:37, team leader -> builder: **four practice-area features (leader's decision:
  the leader does the design half of the new ideas, the builder the practice-area half).**
  In the leader's order of value; cut from the bottom; all before the 20:00 freeze. They live
  in the click and drawing code of `web/app.js`, which is why they are yours.
  (1) **Trace the spiral** (about 1.5 h): a button draws a faint spiral in the practice area;
  the person traces it; the raw line stays in grey and the corrected line in green, and the
  page shows how far each strayed from the spiral on average (px, computed in the page from
  the positions the server sent). Wording: a practice exercise, never a test or a diagnosis.
  Please keep the finished drawing readable from outside as `window.lastSpiral` (a small
  object with the two point lists and the two distances), so the leader's session card can
  show it.
  (2) **Fair test** (about 1.5 h): a guided run of 10 targets with No filter, then 10 with Our
  model, ending in a side-by-side result (hits, misses, time per target). Same number of
  targets each round, so the comparison is fair; say on the card when demo tremor was on.
  (3) **Hold to peek** (about 30 min): while the space bar is held, the correction is off (the
  shown cursor and the click position follow the raw movement), so the person feels the
  difference; release to switch it back on. Show a small "correction paused" note meanwhile.
  (4) **Everyday targets: DONE by the leader's agent (Sun 15 Nov 12:59 CET, branch `leader/motion`), not
  yours any more.** New file `web/targets.js`; `web/app.js` changed in three small places
  only (`onTarget`, `newTarget`, and the line in `draw` that draws the target). If your
  spiral or fair test need the target, use `target.kind` and `targetContains()`.
  The leader meanwhile works on branch `leader/motion` and keeps new code in NEW files
  (`web/motion.js`, `web/motion.css`), touching `web/app.js` as little as possible, so the
  two lanes do not collide. Styling of whatever you add is the leader's afterwards: plain
  markup with ids is enough.

- DONE by the builder (Sun 15 Nov afternoon, see "Done since the trim"; the leader re-checks
  on the demo Mac). Sun 15 Nov ~11:20, team leader -> builder: **B3 counts as DONE (leader's decision); three
  optional fixes for clicking real buttons**, which the leader found still hard with our model
  (`--demo strong`, demo Mac). Likely causes, read from the code, not measured:
  (1) after a pause over 1 s (`models/resample.py` `MAX_GAP`) the models start fresh and the
  correction is off for the detector's 2.56 s warm-up, exactly when the person aims after
  stopping; partly a demo effect (a still mouse sends no events, so the replayed tremor stops;
  a real tremor hand never stops). Fix idea: in demo mode keep a 100 Hz timer that applies the
  replayed tremor while the mouse is still, and/or a longer gap (for example 5 s) for B3 only.
  (2) No click freeze in B3: hold the cursor at the press point until release (at most 0.3 s),
  as on the page. (3) About 72 ms lag at Steadiest, so the cursor drifts past a button after
  stopping; maybe `--response balanced` for B3. Time box about 1 h, after the movement-aware
  detector task; checked with `systemwide/test_steady.py` (add a test per fix); the leader
  re-checks on the demo Mac. If not done, it is a "limits" line in the write-up.

- DONE (builder, Sun 15 Nov). Sun 15 Nov, team leader -> builder (small, optional): please add the response level to the
  summary's filter block (`server/main.py`, `"filter": {"mode": ..., "strength": ...,
  "response": settings["response"]}`), so the assistant can see Steadiest / Balanced / Faster
  when it suggests settings. The prompt already handles the field when it is there.

- Sun 15 Nov, builder -> team leader (UI is yours): new file `web/reading.js` (the easier-to-read
  text switch) and one `<script>` line in `web/index.html`; it also moves "How to use" into a
  `.topbar-tools` row. Restyle freely. Earlier the same day: `web/app.js` speed fixes
  (`shakeNow`, `SEND_GAP_MS`, meter redrawn in `draw`), no visual change.
- Sun 15 Nov, builder -> team leader: the Steadiest / Balanced / Faster control (`web/index.html`
  id `response-row`, `web/app.js` `showSettings` / `onChange("response", ...)`) is yours to
  restyle; keep the id and the `response` value sent to the server.
- Sat 14 Nov 22:02, builder -> team leader: B3 check on the demo Mac (see "What is left").
