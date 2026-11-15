# STATUS: where the project stands right now

**Every agent updates this file at the end of every work session** (rules in `CLAUDE.md`).
Keep it short: only what is live. Finished requests, superseded results and the full history
up to Sun 15 Nov 10:45 CET are in `docs/STATUS_ARCHIVE.md` (move things there, never delete).
Newest entries at the top of each list. Use local time (CET) and say who you are.

## Right now (Sun 15 Nov 10:45 CET)

| Lane | Working on | Blocked by |
|---|---|---|
| Builder | All build steps done except the human checks below. Waiting for the leader's B3 and trackpad results | Leader's demo-Mac checks |
| Team leader | Demo-Mac checks (B3 first, by 15:00), then the UI fixes the leader took over | - |
| Writer | IN PROGRESS: drafting the write-up from `docs/WRITER_BRIEF.md` | Final project name |

**Time line (CET):** feature freeze **Sun 20:00** (leader's decision, Sun 10:45) · first full
submission Sun 23:00 · final fixes until the deadline **Mon 16 Nov 05:59**.

## What is left (tick or delete lines as they finish)

**Team leader (only possible on the demo Mac):**
- [ ] **B3 real-cursor check, by Sun 15:00.** Grant the Accessibility permission (a human
      does this), then `docs/RUNNING.md` "System-wide correction": `--demo strong --mode none`,
      then `--demo strong`. Report here: does the cursor move (else `--method warp`), is it
      visibly steadier, does Control + Option + X always stop it, do clicks land where shown.
      If it works: a 30 s screen recording for the video. If not: write why; it becomes a
      "we tried" line.
- [ ] Trackpad check of the CURRENT "Our model" (v5 + gated One Euro, Steadiest / Balanced /
      Faster) in Safari and Chrome: smooth enough? lag acceptable? Then the builder ticks step 11.
- [ ] Re-run `python models/corrector/time_live.py` on a quiet Mac (last loaded run: worst 7.4 ms).
- [ ] Read `evaluation/results/RESULTS.md` end to end (step 14 tick).

**Team leader (UI work taken over Sat 22:00; `web/` and `assistant/`):**
- [ ] The builder's five findings: (1) the floating assistant button covers content at the
      bottom right; (2) Analysis chart labels cut off on the right; (3) How it works -> "How
      well it does" repeats the filter line and shows no corrector result; (4) the meter keeps
      old values after the hand stops (grey out after about 1 s). ((5), the assistant's
      "0 minutes" / "learned", is done.)
- [ ] Larger text (accessibility). Dyslexia-friendly font and colour-blind-safe colours only
      if time allows. ("Read aloud" is done.)
- [ ] Mention the Steadiest / Balanced / Faster control in the tutorial (`web/tutorial.js`).

**Oleksandr:**
- [ ] Read `evaluation/results/failures/failures.md` (step 9 tick) and `RESULTS.md` (step 14 tick).

**Whole team:**
- [ ] Confirm the final project name (the page says "Steady Pointer").
- [ ] Write-up in `README.md` (the leader says when the write-up phase starts), demo video,
      submission form, every link checked in a private window.

**Cut (leader's decision, Sun 10:45):** step 16 desktop window; sticky targets (goes into the
write-up as a next step); round 2 of the step 4 path check (the stress test already answered it).

## Done since the trim (newest first)

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
- B3 (`systemwide/`): built and logic-tested, not yet checked on a real cursor.

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

- Sun 15 Nov, team leader -> builder (small, optional): please add the response level to the
  summary's filter block (`server/main.py`, `"filter": {"mode": ..., "strength": ...,
  "response": settings["response"]}`), so the assistant can see Steadiest / Balanced / Faster
  when it suggests settings. The prompt already handles the field when it is there.

- Sun 15 Nov, builder -> team leader: the Steadiest / Balanced / Faster control (`web/index.html`
  id `response-row`, `web/app.js` `showSettings` / `onChange("response", ...)`) is yours to
  restyle; keep the id and the `response` value sent to the server.
- Sat 14 Nov 22:02, builder -> team leader: B3 check on the demo Mac (see "What is left").
