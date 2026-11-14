# STATUS: where the project stands right now

**Every agent updates this file at the end of every work session** (rules in `CLAUDE.md`).
The writer builds the write-up from it, and teammates read it instead of asking.
Newest entries go at the top of each list. Use local time and say who you are.

## Right now

| Lane | Working on | Branch | Blocked by |
|---|---|---|---|
| Builder | Step 1 done on the builder's Mac; waiting for the Mac check. Data download finishing; then step 2 | main | Leader's Mac check of step 1 (see Requests) |
| Team leader | not started | - | - |
| Writer | not started | - | - |

## Done (newest first)

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

- None yet.

## Decisions made along the way (what, why, who decided)

- None yet beyond `docs/PROJECT_PLAN.md`.

## Problems and things that did not work

- None yet. (Keep this honest; the write-up needs a "what didn't work" section.)

## Requests to another lane

- Builder → team leader (Sat 14 Nov 14:05): first cross-machine check. On your Mac:
  `git pull`, then `python3.12 -m venv .venv` (if not done), `source .venv/bin/activate`,
  `python -m pip install -r requirements.txt`, then
  `python -c "import numpy, pandas, scipy, sklearn, torch, fastapi, anthropic"` and
  `python models/device.py`. Write the result (or the error text) here.

## Questions waiting for the team leader

- None.
