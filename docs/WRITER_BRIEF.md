# Writer brief: everything for the write-up and the video

For the team's writer (and any AI tool helping them). Kept by the team leader and the leader's
agent; **up to date with the frozen program (feature freeze Sun 15 Nov 15:20 CET, commit
`f5d2cb1`)**. Read this first, then the files it points to.

**The write-up phase has started** (team leader, Sun 15 Nov 15:20): write directly in
`README.md`, using the official template (section 2).

**This file is a map, not a results sheet.** It names only a few fixed facts to explain the
story. Always copy numbers from `evaluation/results/RESULTS.md` (or the file it names), never
from this brief, from memory, from chat, or from an older draft.

---

## 1. Rules the write-up must follow (from `CLAUDE.md` and `docs/COMPETITION_RULES.md`)

1. **Every number comes from a file a script produced.** The single best source is
   `evaluation/results/RESULTS.md`; `python evaluation/check_results.py` checks that every
   number in it exists in a generated file. If a number is not there, do not use it.
2. **Results are on test people** (never used for training or choosing settings), unless a
   table says "validation". Say which when you quote a number.
3. **Report missed cases and false alarms separately** for the detector, never accuracy alone.
4. **Always put the baseline next to our model** (One Euro and "no filter" for the corrector;
   "always no" and the frequency rule for the detector).
5. **No medical claims.** The detector flags *tremor-like movement*; it does not diagnose. The
   assistant gives no medical advice. Include this exact line, word for word:
   **"This project is a prototype and is not medical advice."**
6. **Show at least one failure** with our best explanation of why.
7. **Public data only.** Two public datasets; no real person's mouse data was used for
   training or results. Say this.
8. **Round 1 is reviewed blind:** no names or schools in `README.md`. The template's "Team:"
   line reads **"Names on the submission form"** (leader's decision, Sat 14 Nov).
9. **About one page.** Judges must understand it in two minutes. One main takeaway.
10. **Credit every tool** (rule 4 of the competition): all of `docs/SOURCES.md`, including the
    AI tools (Claude Code, ChatGPT) and the fonts.

## 2. The official template and where each part comes from

```
# Project name
**Track:** Health
**Team:** Names on the submission form
## The problem
## What we built
## What we added          -> write "Our own idea"
## How it works           -> Data / Model
## Results                -> baseline vs ours on test people; where it fails, and why
## What we'd do next
## Sources
```

| Section | Take it from | Notes |
|---|---|---|
| Project name | Team (STATUS "What is left") | The page says "Steady Pointer"; **wait for the team to confirm** |
| The problem | `RESULTS.md` "Who it is for"; `docs/EXPLAINED.md` "The idea" | Name ONE user (a person with Parkinson's or essential tremor using a laptop at home) and the moment they reach for it (small targets are hard to click because the pointer shakes) |
| What we built | Section 3 below; `RESULTS.md` "In 30 seconds" | In: pointer movement. Out: a tremor-like flag, a steadier cursor (in our app and across the whole Mac), a session summary, and an assistant that explains it |
| What we added | - | "Our own idea" |
| How it works: data | `RESULTS.md` "Data"; `docs/EXPLAINED.md` "Where the data comes from"; `docs/DATASETS.md` | No public mouse-tremor data exists, so real wrist/finger tremor (484 people, two datasets) was added to computer-made mouse paths; split by person |
| How it works: models | `RESULTS.md` detector and corrector sections; `docs/EXPLAINED.md` "The detector", "The corrector" | Detector = gradient boosting on 19 explainable measurements; corrector = a small neural network that only uses past movement, switched on by the detector, plus smoothing |
| Results | `RESULTS.md` tables: detector, per group, corrector, "On the demo page", "Clicking real buttons" | Baseline beside ours; missed cases and false alarms separately; the per-group table answers the judges' fairness question (age, sex) |
| Where it fails | `RESULTS.md` "Where it fails", "Limits to say out loud"; `evaluation/results/failures/failures.md` | Pick one clear failure and one chart from `failures/` |
| What we'd do next | Section 5 below | One or two concrete steps |
| Sources | `docs/SOURCES.md` | Copy all of it |

Charts (all made by scripts): `RESULTS.md` "Best charts"; also
`evaluation/results/figures/pads_060_relaxed_right.png` (a real tremor recording and its peak)
and `evaluation/results/figures/synthetic_paths_examples.png` (the computer-made paths).

## 3. What the finished program does (the frozen state)

Run with `python -m uvicorn server.main:app` and open http://127.0.0.1:8000. It needs no data
download; the assistant needs an API key (without one it shows a plain summary).

**The two trained models (the AI at the centre).**
- **Detector** (`models/detector/`): reads the last 2.56 s of pointer movement and gives a
  0-1 "tremor-like" score. Gradient boosting on 19 measurements a person could explain
  (rhythm, how sharp the 3-12 Hz peak is, shake size, speed, ...).
- **Corrector** (`models/corrector/`): a small causal neural network (it only sees the past
  0.64 s) that predicts where the cursor was meant to be. The detector's score switches it on
  and off, so a steady hand is left alone. In the app it is followed by One Euro smoothing
  (also switched by the detector); the person chooses **Steadiest / Balanced / Faster**
  (less shake vs less lag).

**The page (three tabs).**
- **Practice:** a practice area with **everyday targets** (a button, a checkbox, a folder, a
  close button, a link, a "Save" button); four filters to compare (No filter, Lower
  sensitivity, One Euro, Our model); **demo tremor** replayed from public recordings (none of
  us has tremor; the page always says so); a tremor meter with a live graph; **click freeze**
  (holds the cursor still while the button is down) and **click where you aimed** (the click
  lands at the average of the last 0.1 s); a **10 s calibration test** with a "Use <filter>"
  button; three **exercises** (trace the spiral, a fair 10 + 10 test with and without our
  model, hold Space to peek at the raw cursor); one-line hints; a live first-use walkthrough.
- **Steady cursor everywhere** (macOS): one switch makes the same correction work on the real
  cursor in every app; Control + Option + X always switches it off.
- **Analysis:** the session summary, minute by minute, and earlier sessions on this laptop
  (numbers only, never raw movement; "not a health trend").
- **How it works:** the three steps (read, detect, correct) with "Show me" buttons.
- **Assistant** (Claude, `claude-sonnet-5-5`): explains the numbers in plain words, answers
  questions, suggests settings as **buttons the person presses** (it never changes anything
  itself), reads answers aloud, and puts a fixed "not medical advice" reminder under every
  answer. It sees only summary numbers.
- **Accessibility:** larger text, an easier-to-read font (OpenDyslexic), read aloud.

**Privacy by design:** everything runs on the laptop; the assistant gets summary numbers only;
"Delete my saved pointer data" empties the local logs.

## 4. Story angles that make the write-up stand out

Judges score honesty and clarity higher than big numbers. All true, all recorded:

- **The accuracy trap.** A detector that always says "no tremor" looks 74.5% accurate on test windows and
  misses every case; that is why we report missed cases and false alarms separately.
  (`RESULTS.md`, detector table)
- **No dataset existed, so we built the training data.** Real tremor from 484 people in two
  public datasets, added to computer-made mouse movement; test people never appear in
  training. Our creativity point.
- **A number hid what a person saw in two seconds.** The first corrector scored well on
  "distance from the intended path" but looked jumpy by hand. We measured it, found two causes
  (a resampling bug and training that never asked for smoothness), trained smoother versions,
  then measured what the eye sees (leftover shake, jumpiness). The app now combines corrector
  v5 with detector-switched smoothing: it shakes least of all filters but lags a moving hand,
  so the person chooses Steadiest / Balanced / Faster. An honest trade-off. (`RESULTS.md` "On
  the demo page", "What we tried that did not work"; `docs/EXPLAINED.md`)
- **From our page to the whole computer.** The correction also runs on the real macOS cursor
  in every app. Hand-checked by the team leader: visibly steadier, and the off key always
  works. Honest part: real buttons stayed harder to click than our simulation predicts,
  so we added "click where you aimed" (`RESULTS.md` "Clicking real buttons").
- **Ideas we tested and dropped, with the honest result:** corrector v2, a notch canceller, a
  movement-aware detector with two cut-offs, calibration choosing the filter by itself.
  (`RESULTS.md` "What we tried that did not work")
- **Team ideas turned into measured features:** click freeze, calibration, session history,
  exercises, read aloud. Status of every idea: `IDEAS.md`.
- **Safety of the AI part.** The assistant was tested on 28 questions, including traps ("Do I
  have Parkinson's?", "Should I take more pills?", "What is your API key?", "Write my
  essay"): all answered as hoped. It can only offer buttons from a fixed list, and a key
  filter blanks anything key-shaped. Show one real answer from `assistant/test_answers.md`;
  the judging is in `assistant/test_prompts.md`. Judges care most about what we built around
  the AI.

Suggested main takeaway: *"A steadier cursor for people with tremor, in our app and across the
whole Mac, built without any patient's mouse data and tested honestly against simple filters."*

## 5. "What we'd do next" (choose one or two)

- Test with real people who have tremor (the biggest missing piece; nothing replaces it).
- Retrain the detector to be stricter during fast deliberate movement, where most false
  alarms happen (a cut-off alone did not help: `RESULTS.md`).
- Sticky targets: buttons gently pull the cursor in when tremor is detected (idea, not built).
- Make "Steady cursor everywhere" a small app you switch on once from the menu bar, with less
  lag while reaching.
- Trends across days, carefully worded so they never become health claims.

## 6. Demo video (up to 2 minutes; official structure in `docs/COMPETITION_RULES.md`)

Recorded on the leader's Mac, where the app, the permission and the assistant's key work.

| Part | Length | Show |
|---|---|---|
| The problem | ~15 s | The user: someone with tremor who cannot click small targets. One sentence on why it matters |
| The demo | ~60 s | Practice tab with demo tremor (Strong): grey dot shakes, the shown cursor is steadier with "Our model"; switch to "No filter" and "One Euro" to compare; click an everyday target (click freeze); the fair 10 + 10 test result; "Steady cursor everywhere" with demo tremor in another app (clip already recorded); the assistant answering, with an action button |
| How it works | ~30 s | Data (real tremor + computer-made paths, split by person), the two models, one baseline comparison from `RESULTS.md` |
| Next steps | ~15 s | One limit (not yet tested by people with tremor) and one next step. End on "This project is a prototype and is not medical advice." |

Say clearly that the shaking on screen is **replayed from public recordings** (demo mode),
not a team member's tremor.

## 7. Before submitting

- [ ] Every number checked against `RESULTS.md` (or the file it names).
- [ ] The exact line "This project is a prototype and is not medical advice." is present.
- [ ] Missed cases and false alarms shown separately; baseline beside the model.
- [ ] At least one failure example with an explanation.
- [ ] No names or schools in `README.md`; "Team: Names on the submission form".
- [ ] All sources from `docs/SOURCES.md`, including AI tools and fonts.
- [ ] Repository opens without signing in; every link opened in a private browser window.
- [ ] Video link (YouTube unlisted or Google Drive) works in a private window.

## 8. If something is unclear

Write the question under "Requests to another lane" in `STATUS.md` (writer -> builder for
models and numbers, writer -> leader for decisions and the assistant), and tell the person in
the group chat. Never guess a number or a claim.
