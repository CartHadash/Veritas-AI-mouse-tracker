# STATUS: where the project stands right now

**Every agent updates this file at the end of every work session** (rules in `CLAUDE.md`).
The writer builds the write-up from it, and teammates read it instead of asking.
Newest entries go at the top of each list. Use local time and say who you are.

## Right now

| Lane | Working on | Branch | Blocked by |
|---|---|---|---|
| Builder | Steps 1-2 done and confirmed on the demo Mac. Next: step 3, tremor library | main | - |
| Team leader | not started | - | - |
| Writer | not started | - | - |

## Done (newest first)

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

- `data_pipeline/look_at_data.py`: PADS 469 subjects (276 Parkinson's, 79 healthy, 60 other
  movement disorders, 28 essential tremor, 15 atypical Parkinsonism, 11 MS); ages 161 / 149 /
  159 (under 60 / 60-69 / 70+); 281 male, 188 female. PADS 060 right wrist Relaxed: peak
  4.30 Hz, 99% of power in 3-12 Hz. TremorDB rofh/s6rof.let: peak 4.88 Hz, 98% in 3-12 Hz.

## Decisions made along the way (what, why, who decided)

- None yet beyond `docs/PROJECT_PLAN.md`.

## Problems and things that did not work

- None yet. (Keep this honest; the write-up needs a "what didn't work" section.)

## Requests to another lane

- DONE (Sat 14 Nov, leader's Mac): builder's first cross-machine check. See "Done".

## Questions waiting for the team leader

- Sat 14 Nov 14:10, from the builder: rewrite `scripts/download_data.py` and
  `baselines/classical_filters.py` from scratch to remove any rule-2 risk? Builder's agent
  recommends yes (about 30-45 min). Changes the decision in `docs/REUSED_CODE.md`.
