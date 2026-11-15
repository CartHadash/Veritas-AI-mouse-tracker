# STATUS: where the project stands right now

**Every agent updates this file at the end of every work session** (rules in `CLAUDE.md`).
Keep it short: only what is live. Finished requests, superseded results and the full history
up to Sun 15 Nov 10:45 CET are in `docs/STATUS_ARCHIVE.md` (move things there, never delete).
Newest entries at the top of each list. Use local time (CET) and say who you are.

## Right now (Sun 15 Nov 10:45 CET)

| Lane | Working on | Blocked by |
|---|---|---|
| Builder | NEXT: "click where you aimed", then system-wide correction as a page switch (tasks below) | - |
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
- [ ] **1. "Click where you aimed" (about 45 min).** Why: the leader's B3 re-check (12:18) found
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
- [ ] **2. System-wide correction as a real feature, not only a timed test (about 1.5 h).**
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

- Sun 15 Nov 12:51, team leader -> builder: **an assistant that can DO things, not only answer
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

- Sun 15 Nov 12:37, team leader -> builder: **four practice-area features (leader's decision:
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
  (4) **Everyday targets** (about 1.5-2 h, first to cut): instead of circles, things that are
  hard in real life: a small close button, a checkbox, a link inside a sentence.
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
