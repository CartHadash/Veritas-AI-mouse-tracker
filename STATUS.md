# STATUS: where the project stands right now

**Every agent updates this file at the end of every work session** (rules in `CLAUDE.md`).
Keep it short: only what is live. Everything older (all finished work, requests, superseded
results) is in `docs/STATUS_ARCHIVE.md`: moved, never deleted. Newest first; CET; say who you are.

## Right now (Sun 15 Nov 15:20 CET, leader's agent)

**FEATURE FREEZE since Sun 15 Nov 15:20 CET** (team leader's decision; it replaces the 20:00
freeze). The program is finished as it is:
- **Allowed:** bug fixes (a broken feature, a crash, wrong wording), the write-up, the video,
  documentation, re-running checks.
- **Not allowed:** new features, new models or retraining, new pages, new settings, design
  changes. A bug fix that needs more than about 30 lines: ask the leader first.
- Only the team leader can lift the freeze (if the team agrees to add something, the leader
  says so and this section is changed back).

**The write-up phase has started** (team leader, Sun 15 Nov 15:20): the writer may now edit
`README.md` (CLAUDE.md rule 13). Everything the writer needs: `docs/WRITER_BRIEF.md`.

| Lane | Working on | Blocked by |
|---|---|---|
| Builder | Frozen: bug fixes only. Read `failures.md` and `RESULTS.md` (steps 9 and 14) | - |
| Team leader | Write-up with the writer, the video, the submission | - |
| Writer | `README.md` from `docs/WRITER_BRIEF.md` | Final project name |

**Time line (CET):** first full submission Sun 23:00 · final fixes until the deadline
**Mon 16 Nov 05:59**.

## What is left (tick or delete lines as they finish)

- [ ] **Team:** confirm the final project name (the page says "Steady Pointer").
- [ ] **Writer + leader:** `README.md` from the official template, using `docs/WRITER_BRIEF.md`.
- [ ] **Leader:** record the demo video (script: `docs/VIDEO_SCRIPT.md`; outline in `docs/WRITER_BRIEF.md` section 6). Clips
      already recorded: B3 real cursor (leader's laptop, `~/Desktop/screenshots/veritas-b3/`).
- [ ] **Leader and Oleksandr:** read `evaluation/results/RESULTS.md` end to end (step 14);
      Oleksandr also `failures/failures.md` (step 9). Anything you cannot explain: ask.
- [ ] **Leader's agent:** a last fresh-clone test on the demo Mac after the freeze (step 15
      again: many files were added on Sunday).
- [ ] **Leader:** submission form; every link opened in a private browser window; first
      submission by Sun 23:00.

## What the app is now (frozen state, Sun 15 Nov 15:20)

Commit `f5d2cb1`. Run: `python -m uvicorn server.main:app`, open http://127.0.0.1:8000.
- **Detector v2** (gradient boosting on 19 measurements of the last 2.56 s) flags tremor-like
  movement; its score switches the correction on and off.
- **"Our model"** = corrector v5 (a small causal neural network) + One Euro smoothing, both
  switched on by the detector; Steadiest (default) / Balanced / Faster trades shake for lag.
- **Practice tab:** four filters (No filter, Lower sensitivity with Pointer Lock, One Euro,
  Our model), demo tremor replayed from public recordings (starts at Strong), everyday targets
  (button, checkbox, folder, close button, link, "Save"), click freeze, "click where you
  aimed", a 10 s calibration test with a "Use <filter>" button, three exercises (trace the
  spiral, a fair 10 + 10 test, hold Space to peek), a tremor meter with a live graph, one-line
  hints, a live first-use walkthrough.
- **"Steady cursor everywhere"** (macOS, Accessibility permission): the same correction on
  the real cursor in every app, until switched off; Control + Option + X always stops it.
- **Analysis tab:** session summary, minute-by-minute chart, earlier sessions on this laptop.
- **Assistant** (`claude-sonnet-5-5`): sees only summary numbers; never medical advice;
  action buttons the person presses; read aloud; a fixed reminder under every answer; a plain
  non-AI summary without a key.
- **Accessibility:** larger text, easier-to-read text (OpenDyslexic), read aloud.

## Checks done on the demo Mac (Sun 15 Nov)

Details of each: `docs/STATUS_ARCHIVE.md`.
- Automated, 14:50 (commit 34e8cea): `python -m pytest` 30 passed, 7 skipped (need data);
  `check_results.py` OK; `server/test_ws.py` 500/500 in every mode; `time_live.py` worst
  2.79 ms per update (12:15; limit 8 ms).
- By hand (leader): B3 real cursor steadier in every app, off key works (11:04-11:09); click
  fixes "a bit better" (12:18); "Steady cursor everywhere" works everywhere, off key works,
  "not perfect but good enough"; the website works; the trackpad check "good enough".
- Assistant with the real key (15:00): 28/28 test questions as hoped
  (`assistant/test_prompts.md`, version 6).

## Results (the full, checked list is `evaluation/results/RESULTS.md`)

Copy numbers from `RESULTS.md` (checked by `python evaluation/check_results.py`), never from here.

## Decisions in force (older ones: `docs/STATUS_ARCHIVE.md`)

- Sun 15 Nov 15:20, team leader: **feature freeze now** (replaces 20:00); **write-up phase started**.
- Sun 15 Nov 12:30, team leader: correction across the whole Mac as a page switch; "click where
  you aimed" (both built and checked).
- Sun 15 Nov 10:45, team leader: cut step 16 (desktop window), sticky targets, path check round 2.
- Sun 15 Nov 00:55-03:48, builder (on validation, rules fixed in advance): the app's model is
  v5 + gated One Euro; the person picks Steadiest / Balanced / Faster.
- Sat 14 Nov 22:10, team leader: README shows no names or schools ("Names on the submission form").
- Sat 14 Nov, team leader: L1 = B (session summaries kept on the laptop, numbers only, never
  health trends); L2 = `claude-sonnet-5-5`, effort `low`; the assistant is one instructed call.
- Sat 14 Nov, builder: Decisions 1-7 (pixel factor, all PADS tasks, gradient boosting, cut-off
  at most 20% missed on validation, models in Python on the server, warm look, plain JS).

## Problems and things that did not work (the write-up needs these)

The full list with numbers is `RESULTS.md` "What we tried that did not work". The stories:
- **A number hid what a person saw in two seconds:** corrector v1 scored well on distance but
  looked jumpy by hand (a resampling bug, and training that never asked for smoothness). v4
  added smoothness, v5 + gated One Euro fixed it by eye, at the cost of lag.
- Offline scores could not see live-pipeline bugs (clock drift, replay skipping samples);
  found by testing the live path and a code review.
- Not kept: corrector v2 (bigger/smaller tremor), the notch canceller, the movement-aware
  detector with two cut-offs (false alarms while moving 30.3% -> 31.1% on validation).
- Real buttons stayed harder to click than the simulation says (the simulation has perfect
  aim); click freeze and "click where you aimed" made it "a bit better".
- The first API key was not in a workspace (error 400); twice a merge went out before its
  STATUS entry. Both fixed; lessons in `CLAUDE.md`.

## Requests to another lane (open only)

- None open. (All earlier requests were answered; they are in `docs/STATUS_ARCHIVE.md`.)
