# Build guide: TEAM LEADER lane

For the team leader (Timofey) and their AI agent (Claude Code on the demo MacBook). The leader
owns `tracker/`, `assistant/`, `web/assistant/`, the UI work in `web/` taken over on Sat 22:00
(coordinate with the builder before editing a `web/` file), and every final decision.
The original step-by-step instructions are in git history (this file before Sun 15 Nov 10:45 CET).

First message to give the agent:

> You are the TEAM LEADER's agent. Read CLAUDE.md, then STATUS.md and BUILD_GUIDE_LEADER.md,
> and continue from the first unticked item. Explain each step in simple words before you do
> it, and stop to ask me at every decision.

---

## Part A: leading (Sunday, CET)

- [x] Saturday: sources verified, scope checked, first results read, rewrite of the two
      pre-hackathon files ordered (no reused code is left, so no email to the organisers is needed).
- [ ] **By 15:00: the demo-Mac checks** listed in `STATUS.md` ("What is left"): B3 real
      cursor, trackpad check of the current model in Safari and Chrome, `time_live.py` on a
      quiet Mac. You are the only one with the demo Mac; paste results and error text into `STATUS.md`.
- [ ] **By 18:00:** read `evaluation/results/RESULTS.md` and `docs/EXPLAINED.md` end to end.
      Anything you cannot explain to a judge gets fixed or removed.
- [ ] **20:00: feature freeze.** Tell everyone to stop adding things; only fixes after this.
- [ ] **20:00-23:00:** tell the writer the write-up phase has started; fill `README.md` from the
      official template (`docs/COMPETITION_RULES.md`) using `docs/WRITER_BRIEF.md`. Record the video.
- [ ] **23:00: first submission.** Open every link in a private browser window first.
- [ ] **Before Mon 05:59:** final resubmission after last fixes.

## Part B: building

### - [x] B1. The whole-laptop pointer reader (`tracker/`)

Reads the pointer position about 100 times a second everywhere on the laptop (positions and
times only; no permission needed). Contract 1. Measured 100.0 samples per second on the demo
Mac. `start(callback, save_log=False)`; idle after 3 s still. Explained in `docs/EXPLAINED.md`.

### - [x] B2. The assistant (`assistant/`, `web/assistant/`)

One instructed Claude call (`claude-sonnet-5-5`, effort `low`, streamed) that sees only the
summary numbers (Contract 2/3), never raw movement, and never gives medical advice. Plain
non-AI summary without a key. Session history (L1 = B) in `local_logs/sessions/`, compared
as pointer numbers only, never health trends. 18/18 trap questions safe
(`assistant/test_prompts.md`). Before changing any Claude API code, load the `claude-api` skill.

### - [x] B3 check (built by the builder in `systemwide/`; the leader runs the check)

Done Sun 11:04: works (results in `STATUS.md`). Left: an off-switch press during a run, and the clip.

Makes the real macOS cursor steadier in every app. Needs the **Accessibility permission**
for the terminal app (System Settings → Privacy & Security → Accessibility; a human switches
it on, never the agent; quit and reopen the terminal). Commands and what to report:
`docs/RUNNING.md` "System-wide correction" and `STATUS.md`. Safety: auto-off after 60 s,
Control + Option + X, Ctrl+C.

**Done when:** with demo tremor on, the real cursor is visibly steadier in another app, the
off-switch works every time, and a 30-second recording exists. Or: by 15:00 it does not, and
`STATUS.md` says why (a fine "we tried" line for the write-up).

### - [ ] UI work (taken over Sat 22:00)

The list is in `STATUS.md` ("What is left"): the builder's five findings, read aloud and
larger text, the response control in the tutorial. Cut: sticky targets (a "next step" in the
write-up). Controls are ui-sdk web components (see `CLAUDE.md` "Things we learned").

## What you hand to the writer

By 18:00, `STATUS.md` and `docs/EXPLAINED.md` must say, for this lane: what the tracker records
and deliberately does not; how the assistant is limited; the trap-question results; whether
B3 worked. The writer should not have to ask.
