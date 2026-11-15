# STATUS: where the project stands right now

**Every agent updates this file at the end of every work session** (rules in `CLAUDE.md`).
Keep it short: only what is live. Finished requests, superseded results and the full history
up to Sun 15 Nov 10:45 CET are in `docs/STATUS_ARCHIVE.md` (move things there, never delete).
Newest entries at the top of each list. Use local time (CET) and say who you are.

## Right now (Sun 15 Nov 10:45 CET)

| Lane | Working on | Blocked by |
|---|---|---|
| Builder | Leader's Sunday tasks done (detector idea tested: not kept; B3 click fixes; summary field; easier-to-read text). Next: whatever the leader's re-check of B3 finds | - |
| Team leader | B3 off-switch check and video clip, then the UI fixes the leader took over | - |
| Writer | IN PROGRESS: drafting the write-up from `docs/WRITER_BRIEF.md` | Final project name |

**Time line (CET):** feature freeze **Sun 20:00** (leader's decision, Sun 10:45) · first full
submission Sun 23:00 · final fixes until the deadline **Mon 16 Nov 05:59**.

## What is left (tick or delete lines as they finish)

**Team leader (only possible on the demo Mac):**
- [x] **B3 real-cursor check: WORKS** (Sun 11:04, see "Done since the trim").
- [x] B3 off-switch and video clip (Sun 11:08). Clip: leader's laptop, to be saved into
      `~/Desktop/screenshots/veritas-b3/` (not in git: too large).
- [x] Trackpad check of the CURRENT "Our model" (Sun ~11:00, leader: "good enough"). The
      builder can tick step 11.
- [ ] Re-run `python models/corrector/time_live.py` on a quiet Mac (last loaded run: worst 7.4 ms).
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

- [x] B3 click fixes (Sun 15 Nov, see "Done since the trim"). **Leader: please re-check on the
      demo Mac** (`git pull`, then `python -m systemwide.run --demo strong`; click freeze is on
      by default; try `--response balanced` too and say which feels better).

**Oleksandr:**
- [ ] Read `evaluation/results/failures/failures.md` (step 9 tick) and `RESULTS.md` (step 14 tick).

**Whole team:**
- [ ] Confirm the final project name (the page says "Steady Pointer").
- [ ] Write-up in `README.md` (the leader says when the write-up phase starts), demo video,
      submission form, every link checked in a private window.

**Cut (leader's decision, Sun 10:45):** step 16 desktop window; sticky targets (goes into the
write-up as a next step); round 2 of the step 4 path check (the stress test already answered it).

## Done since the trim (newest first)

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
