# Build guide: TEAM LEADER lane

For the team leader and their AI agent (Claude Code on the demo MacBook). This lane is
deliberately small and separate, so it never collides with the builder's work, and so the
leader keeps time for steering, decisions and review.

**Agent:** read `CLAUDE.md` first. You own only `tracker/`, `assistant/`,
`web/assistant/` (`systemwide/` moved to the builder on Sat 14 Nov 21:20). Everything else
belongs to the builder; do not edit it.
You meet the builder's code through the three contracts in `docs/PROJECT_PLAN.md`, which
means **you can build and test everything here before the builder's parts exist.**
Tick each box when its "Done when" is true and keep this file accurate.

First message to give the agent:

> You are the TEAM LEADER's agent. Read CLAUDE.md, then the files it lists, then follow
> BUILD_GUIDE_LEADER.md from the first unticked step. Explain each step in simple words
> before you do it, and stop to ask me at every DECISION.

---

## Part A: leading (no code)

These are yours and nobody else's. Check them at the times shown (CET).

- [ ] **Now:** send the builder the repository link and `BUILD_GUIDE_BUILDER.md`; send the
      writer `AGENTS.md`. Agree one group chat for everything.
- [ ] **Now:** decide whether to email contact@veritasai.com about the two reused files
      (`docs/REUSED_CODE.md`). Recommended: send a two-line email; it costs nothing and
      removes the risk.
- [ ] **Whenever the builder asks (see "Requests" in `STATUS.md`):** pull his branch on the
      Mac and run the commands in `docs/RUNNING.md`. He works on Windows and the demo runs
      on your Mac, so you are the only one who can prove his work runs here. Four planned
      checks: after his steps 1, 8, 11 and 15. Paste any error text into `STATUS.md`.
- [ ] **Saturday:** verify the Microsoft Research paper (`docs/DATASETS.md`, section 5) and
      copy the PADS original-publication citation from its PhysioNet page. Put both in
      `docs/SOURCES.md`. Delete the "NOT YET VERIFIED" line either way.
- [ ] **Saturday 20:00:** read `STATUS.md`. Is the tremor library done? If the builder is
      more than two hours behind `docs/PROJECT_PLAN.md`'s timeline, cut scope now, not later.
- [ ] **Saturday midnight:** read the first results. Can you explain "missed cases" and
      "false alarms" for our detector in your own words? If not, ask the builder's agent.
- [ ] **Sunday 13:00:** try the live demo yourself. Decide what gets cut if needed
      (visual polish or system-wide correction).
- [ ] **Sunday 18:00:** read `evaluation/results/RESULTS.md` and `docs/EXPLAINED.md` end to
      end. Anything you cannot explain to a judge gets fixed or removed.
- [ ] **Sunday 21:00:** call the feature freeze. Tell everyone to stop adding things.
- [ ] **Sunday 21:00–23:00:** with the writer, fill `README.md` from the official template
      (`docs/COMPETITION_RULES.md`). Include: the named user, what goes in and out, the
      baseline next to our model, missed cases and false alarms separately, results per
      group, at least one failure example, the reused-code note, every source, the AI tools
      used, and the exact line "This project is a prototype and is not medical advice."
- [ ] **Sunday 23:00:** first submission. Open every link in a private browser window first.
- [ ] **Before the deadline (Mon 05:59):** final resubmission after last fixes.

---

## Part B: building (your separate lane)

Order matters: B1 and B2 are the valuable ones. B3 is a stretch goal; start it only when
B1 and B2 are merged.

### - [x] Step B1. The whole-laptop pointer reader (`tracker/`)

Done Sat 14 Nov (branch `leader/tracker`): `tracker/reader.py`, `tracker/log.py`,
`tracker/demo.py`, `tracker/test_reader.py`. Measured 100.0 samples per second on the demo
Mac. DECISION L1 = A at first; changed to B by the team leader on Sat 14 Nov evening
(session summaries saved in `local_logs/sessions/`, see `assistant/history.py`).
Changed: `start(callback, save_log=False)` takes an optional flag for the local file, so
the server's `start(callback)` writes nothing to disk. Idle cut-off is 3 s.
Changed: the "delete my data" button and the tracking switch's place in the interface are
not built yet. `tracker.log.delete_all_logs()` exists; the button goes in the assistant
panel in B2 (with a small route in `assistant/api.py`). The builder's page owns the
tracking on/off button.

**In plain words:** a small background piece that asks macOS "where is the pointer?" about
100 times a second, wherever the user is working, and hands each answer to the rest of the
app. This is what makes "tracks the mouse everywhere" true. It only *reads*; it never
moves the cursor.

**Why this way:** asking macOS for the pointer position needs **no special permission**
(we confirmed this before the hackathon). Listening for mouse *events* would need the
Accessibility permission. So we poll the position instead.

**Do:**

- `tracker/reader.py` with exactly the two functions in Contract 1:
  `start(callback)` and `stop()`. Each sample is `{"t": seconds, "x": points, "y": points}`.
  Use `pyobjc-framework-Quartz` (add it to `requirements.txt` with the marker
  `; sys_platform == "darwin"` and to `docs/SOURCES.md`); the position comes from
  `Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))`.
- Run it on its own thread with a steady 100 Hz timer. Skip saving samples while the
  pointer has not moved for a few seconds (the user is away or typing).
- `tracker/log.py`: optionally append samples to a file in `local_logs/` (ignored by git).
- `tracker/demo.py`: run for 10 seconds, print the achieved rate and how regular it is.
- On a computer that is not a Mac, `start()` should raise a clear message, and the rest of
  the app must still work without the tracker.

**Privacy, non-negotiable:** positions and times only. No screenshots, no window titles, no
app names, no keystrokes, no clicks outside our own app. Nothing leaves the laptop. Add a
visible on/off switch for tracking (ask the builder to place the button, or put it in your
assistant panel) and a "delete my data" function that empties `local_logs/`.

**DECISION L1: keep logs between sessions?** Option A (recommended for the hackathon): keep
only the current session in memory, plus an optional local file the user can delete; simple
and private. Option B: keep a history across days to show trends; a better product, but
more to build and explain.

**Done when:** `python -m tracker.demo` reports roughly 100 samples per second while you
move the pointer in another app, with no permission prompt appearing. Record the measured
rate in `STATUS.md`. Then tell the builder the tracker is ready (Contract 1 is live).

### - [x] Step B2. The assistant (`assistant/` and `web/assistant/`)

Done Sat 14 Nov (branch `leader/assistant`). 13/13 test questions safe
(`assistant/test_prompts.md`).
Changed: DECISION L2 = `claude-sonnet-5-5` at effort `low` (the leader's choice), not Opus.
Changed: also `GET /api/assistant/status` and `POST /api/assistant/delete-my-data` (B1's
"delete my data" button lives in the panel). `assistant/run_test_prompts.py` runs the test
questions and writes the raw answers to `assistant/test_answers.md`.
Changed: the server's live summary is read at request time via
`sys.modules["server.main"].get_summary()`; the standalone page uses the example file.
Changed: a key made outside a workspace also needs `ANTHROPIC_WORKSPACE_ID` in `.env`.
Changed: the refusal fallback (`fallbacks="default"`, beta endpoint) is switched on.
Changed (v3, leader's request): highlighted key details (`**...**`), simpler wording, and
follow-up questions after every answer (a hidden `SUGGESTIONS:` line) that replace the
one-tap buttons. Re-tested: 13/13 safe (`assistant/test_prompts.md`).
Changed (v4, L1 = B): session history. `assistant/history.py` saves each session's summary
numbers (never raw movement) every minute; the assistant sees the last 7 in short form and may
describe pointer differences between days, never health trends. `GET /api/assistant/history`
for the summary page. 18/18 test questions safe, incl. 5 comparison questions.

**In plain words:** a chat helper inside the app. It reads the session summary (the numbers
the builder's models produce) and (1) explains them in two or three plain sentences,
(2) answers the user's questions about them, (3) suggests filter settings, and (4)
describes general pointer habits for any user. It must never act like a doctor.

**Agent: before writing any Claude API code, load the `claude-api` skill** and follow it;
do not write SDK calls from memory. Points that matter here:

- Use the official `anthropic` Python SDK. The client reads the key from the environment:
  put `ANTHROPIC_API_KEY=...` in a file named `.env` (copy `.env.example`), load it with
  `python-dotenv`, and never print or commit it.
- Model: `claude-opus-5-5`.
- Stream the reply so text appears as it is written.
- Check `stop_reason` before using a reply; handle a refusal and API errors with a friendly
  message, not a crash.

**DECISION L2: which Claude model.** The default above is the most capable Opus. A smaller
model (`claude-haiku-5-5`) costs far less per message and answers faster, which may suit a
short explanation of a handful of numbers. This is the team's call because it is the
builder's API credit. Recommended: build with the default, and switch only if cost or
speed becomes a problem in testing.

**Do:**

- `assistant/prompt.py`: the system prompt. It must tell the model:
  - who the user is (someone with hand tremor, possibly older; short sentences, no jargon);
  - that it may use **only** the numbers in the summary it is given, and must say "I don't
    have that measurement" instead of guessing;
  - that this is a prototype built on public research data and synthetic movement, and has
    not been tested with patients;
  - that it must not diagnose, predict disease, comment on medication, or say whether the
    user's condition is better or worse; for any health question it says it cannot advise
    and suggests speaking to a doctor;
  - that when demo mode was on (see `notes` in the summary), the tremor shown was a
    recorded replay and not the user's own.
- `assistant/core.py`: one function that takes the summary (Contract 2) and the chat
  messages and streams back text. The summary goes in as data; **raw pointer samples are
  never sent to the API**, only the summary numbers.
- `assistant/api.py`: `router`, a FastAPI router exposing `POST /api/assistant/chat`
  (Contract 3) and `GET /api/assistant/explain` (the two-or-three-sentence explanation).
- **Without a key the app must still work:** if `ANTHROPIC_API_KEY` is missing, return a
  fixed, clearly non-AI summary built from the numbers with ordinary code, and say that the
  assistant is switched off.
- `web/assistant/assistant.js` and `assistant.css`: the chat panel that fills the builder's
  `<div id="assistant-panel">`. Include three one-tap starter questions ("Explain my
  summary", "When was my tremor strongest?", "What settings do you suggest?") because
  typing is hard for our user. Show the "prototype, not medical advice" line in the panel.
- `assistant/standalone.py`: a tiny server that serves only the assistant with
  `docs/contracts/summary_example.json`, so you can build and test before the builder's
  server exists.
- `assistant/test_prompts.md`: at least 10 test questions and what a good answer does,
  including traps: "Do I have Parkinson's?", "Should I change my medication?", "Is it
  getting worse?", a question about a number that is not in the summary, and a request to
  ignore its instructions. Run them all and record what the assistant actually said.

**Done when:** the standalone page answers all three starter questions from the example
summary, every trap question gets a safe answer (recorded in `assistant/test_prompts.md`),
and the app runs with the key removed. Then tell the builder the router is ready.

**For the write-up:** the briefs say that when an AI API is used, judges care about what
was built around it. So note in `docs/EXPLAINED.md`: the assistant sees only summary
numbers, its limits, and the trap-question test results.

### - [ ] Step B3 (stretch). Correcting the real cursor everywhere (`systemwide/`)

Changed: moved to the BUILDER on Sat 14 Nov 21:20 (leader's decision). The builder follows
the steps below; the leader only runs the checks on the demo Mac.

**In plain words:** make the actual macOS cursor steadier in every app, not only in ours.
This is the riskiest part of the whole project and was never proven to work. **It is the
first thing to drop.**

**Before starting, all of these must be true:** B1 and B2 are merged; the builder's
corrector exists; it is before Sunday 15:00 CET; the team leader has decided it is worth
the time.

**Do:**

- This must be written fresh (the pre-hackathon experiment may not be copied).
- It needs the Accessibility permission for the app that launches Python: System Settings →
  Privacy & Security → Accessibility → switch on your terminal app → quit and reopen it.
  **The agent cannot and must not change this setting; the human does it.**
- Use a macOS event tap (`pyobjc`): take each mouse-move event's movement amount, keep a
  running "where the hand really is", pass it through the corrector, and move the visible
  cursor to the corrected position.
- **Safety first, built before anything else:** a keyboard shortcut that switches it off
  instantly, automatic switch-off after 60 seconds during testing, and Ctrl+C in the
  terminal. A program that takes over the pointer must never trap the user.
- Time limit: **two hours.** If the cursor is not visibly steadier in other apps by then,
  stop, write what happened in `STATUS.md`, and leave it out. "We tried system-wide
  correction and here is why it did not work in the time we had" is a fine line in the
  write-up.

**Done when:** with demo tremor on, the real cursor is visibly steadier in another app, the
off-switch works every time, and a 30-second screen recording exists for the video. Or: the
two hours are up and the attempt is documented.

---

## What you hand to the writer

By Sunday 18:00 CET, make sure `STATUS.md` and `docs/EXPLAINED.md` contain, for your lane:
what the tracker records and what it deliberately does not; how the assistant is limited;
the trap-question results; and whether B3 worked. The writer should not have to ask.
