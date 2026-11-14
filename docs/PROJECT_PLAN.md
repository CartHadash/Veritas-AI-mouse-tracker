# Project plan

Decided by the team leader on Sat 14 Nov 2026, after reading the competition documents.
Changes to anything in "Decisions" go through the team leader.

## One sentence

Our project helps **a person with hand tremor who uses a laptop every day** by taking
**their mouse or trackpad movement** and giving back **a steadier cursor, plus a
plain-language picture of how their tremor is behaving**.

(This is the "quick test" sentence from the Hacker Guide. Keep it true.)

## What the finished thing does

1. **Watches** pointer movement across the whole laptop (read-only; positions only).
2. **Detects** whether the movement contains tremor, and how strong and how fast it is.
   This is a trained model, scored by missed cases and false alarms.
3. **Corrects** the cursor inside our app with a second trained model that removes the
   tremor while keeping the intended movement.
4. **Summarises** the session: tremor over time, steadiness, and general usage habits
   (how much the pointer moved, how accurate clicks were).
5. **Explains** it through a built-in assistant (Claude API) that turns the numbers into
   plain sentences, answers questions about them, and suggests settings.

The secondary audience is anyone curious about their own pointer habits; the same summary
works for them. In the write-up the *named user* stays the person with tremor.

## Decisions (do not reopen without the team leader)

| Topic | Decision |
|---|---|
| Track | AI + Health, "Our own idea" |
| Named user | A person with Parkinson's or essential tremor using a laptop at home |
| The AI at the centre | Two trained models: a tremor **detector** and a tremor **corrector** |
| Baselines | Detector: "always says no tremor" and a simple frequency rule. Corrector: no filter, lower pointer sensitivity, and the classical filters in `baselines/` |
| Training data | Real tremor from two public datasets + **synthetic** clean mouse movement. No recorded mouse data from team, friends or family is used for training or for reported results |
| Where it reads the mouse | Everywhere on the laptop (read-only) |
| Where it corrects the mouse | Inside our own app. Correcting the real cursor everywhere is a stretch goal |
| Interface | A local web app: Python runs the models in the background, the interface is a web page on the same laptop. Wrapping it as a desktop app is a last-step extra |
| Languages | Python for data, models and server. HTML/CSS/JavaScript for the interface |
| Assistant | Claude API. It sees only the app's summary numbers, never raw mouse data, and never gives medical advice |
| Write-up | `README.md`, official template, written at the end. Nobody edits README before then |
| Old code | Only the two files listed in `REUSED_CODE.md` |
| If time runs short | Cut either visual polish or system-wide correction first (team leader chooses at the time). Never cut: the two models, their honest evaluation, the write-up |

## Honest limits we already know (say them, don't hide them)

- No dataset of real mouse movement from people with tremor exists that we could find. Our
  tremor is real (wrist and fingertip recordings); the mouse movement it is added to is
  synthetic; the conversion to pixels is our assumption.
- No person with tremor has tested it.
- The detector tells "tremor-like movement" from "no tremor-like movement" in a cursor
  signal. It does **not** diagnose Parkinson's or anything else.

## Who does what

| Person | Tools | Owns |
|---|---|---|
| **Builder** | Claude Code (**MacBook**, Apple Silicon; not the demo machine) | Data pipeline, both models, evaluation, server, main interface, system-wide stretch goal (B3). Follows `BUILD_GUIDE_BUILDER.md` |
| **Team leader** | Claude Code (MacBook, **the demo machine**) | Whole-laptop pointer reader, the assistant, final decisions. Follows `BUILD_GUIDE_LEADER.md` |
| **Writer** | ChatGPT | Write-up text, sources list, demo video script and recording, submission form. Works from `STATUS.md`, `evaluation/results/` and `docs/` |

**Two machines.** The builder develops on their own Mac (until Sat 14 Nov afternoon the
plan was a Windows PC); the demo runs on the leader's Mac. All builder-lane code must still
run on macOS and Windows. The Mac-only parts (`tracker/`,
`systemwide/`) were put in the leader's lane for this reason; `systemwide/` (B3) moved to
the builder on Sat 14 Nov 21:20 (leader's decision), and the leader runs its Mac checks. The leader pulls and runs
the builder's work on the Mac at the checkpoints listed in `BUILD_GUIDE_BUILDER.md`.

### Folder ownership (this is what prevents overlap)

Only the owner's agent edits a folder. If you need a change in someone else's folder, ask
them (or write it in `STATUS.md` under "Requests").

| Folder / file | Owner | Contents |
|---|---|---|
| `data_pipeline/` | Builder | Tremor library, synthetic movement, training-set builder |
| `models/` | Builder | Detector and corrector: training code and saved weights |
| `evaluation/` | Builder | Benchmark scripts, results tables, charts, failure examples |
| `server/` | Builder | The Python web server that ties everything together |
| `web/` (except `web/assistant/`) | Builder | The interface: live demo and summary pages |
| `tracker/` | Team leader | Reads the pointer everywhere on the laptop; local log |
| `assistant/` | Team leader | Claude API code and prompts |
| `web/assistant/` | Team leader | The assistant's chat panel in the interface |
| `systemwide/` | Builder (moved from the leader, Sat 14 Nov 21:20) | Stretch goal: correcting the real cursor everywhere |
| `baselines/`, `scripts/` | Nobody (frozen) | Reused pre-hackathon files. Bug fixes only |
| `README.md` | Writer, at the end | The write-up. Empty until Sunday |
| `docs/`, `STATUS.md`, `CLAUDE.md`, guides | Everyone | Kept up to date by every agent (rules in `CLAUDE.md`) |

### The contracts (how the two lanes meet without waiting for each other)

Both sides build against these shapes from the start. To change one, tell the other side
first and update this section in the same commit.

**Contract 1: a stream of pointer samples** (tracker → server)

```
{"t": 12.345, "x": 812.0, "y": 440.5}
```
`t` is seconds since the tracker started; `x`, `y` are screen positions in points. About
100 samples per second. The tracker module (`tracker/reader.py`) offers
`tracker.reader.start(callback)`, which calls `callback(sample)` for every sample, and
`tracker.reader.stop()`.

**Contract 2: the session summary** (server → assistant and summary page)

Served at `GET /api/summary`. An example lives in `docs/contracts/summary_example.json`;
the leader's assistant is built against that file until the real one exists.

```
{
  "session": {"started": "2026-11-15T10:02:00", "minutes_active": 42.5},
  "tremor": {
    "detected_share": 0.31,          // share of active time the detector flagged
    "typical_frequency_hz": 4.9,
    "typical_strength_px": 6.2,
    "by_time": [{"minute": 0, "detected_share": 0.2, "strength_px": 4.1}, ...]
  },
  "usage": {
    "distance_px": 184000, "clicks_in_app": 57, "click_accuracy": 0.84,
    "steadiness_score": 0.62         // 0 = very shaky, 1 = very steady
  },
  "filter": {"mode": "learned", "strength": 0.7},
  "model_info": {"detector_version": "v1", "missed_cases_rate": null, "false_alarm_rate": null},
  "notes": ["Tremor replay (demo mode) was ON for part of this session."]
}
```

Optional addition (agreed with the leader, Sat 14 Nov): when the whole-laptop tracker has
data, the summary also has `"whole_laptop": {"session": ..., "tremor": ..., "usage":
{"distance_px": ..., "steadiness_score": ...}}` with the same meanings, from the tracker's
samples.

**Contract 3: the assistant** (interface → assistant)

`POST /api/assistant/chat` with `{"messages": [{"role": "user", "content": "..."}]}`.
The reply streams back as text. The assistant module offers
`assistant.router` (a FastAPI router), which the server includes with one line. It also
serves `GET /api/assistant/explain`, `GET /api/assistant/status` and
`GET /api/assistant/history` (earlier sessions saved on this laptop, newest first; example in
`docs/contracts/history_example.json`), `POST /api/assistant/delete-my-data`, and reads the live summary by calling the server's
`get_summary()` (so that name must stay).

## Timeline

Times are Central European Time (the official deadline is Sunday 23:59 US Eastern).

| By | Target (matches the official suggested schedule) |
|---|---|
| Sat 16:00 | Environment works; datasets downloaded; data loads and plots |
| Sat 20:00 | Tremor library and synthetic movement exist; baselines measured |
| Sat 24:00 | First detector and first corrector trained and scored on unseen subjects. An input goes in, a result comes out |
| Sun 02:00–09:00 | Sleep (the guide insists; so do we) |
| Sun 13:00 | One measured improvement to each model; interface shows the live demo end to end |
| Sun 18:00 | Summary page and assistant connected; failure examples collected |
| Sun 21:00 | **Feature freeze.** Only fixes after this |
| Sun 23:00 | Write-up in README; video recorded; **first submission sent** |
| Mon 03:00 | Final fixes, all links checked in a private window, final resubmission |
| Mon 05:59 | Deadline |

If a step is stuck for 30 minutes: simplify, write down what happened in `STATUS.md`, move on.

## "From web app to real app" (the leader's question)

Not hard, and safe to leave until last. The interface is already a web page served from
the laptop. A small library (`pywebview`) can open that same page in its own window with
its own title, so it looks and feels like a desktop app; that is roughly 20 lines of
Python. Building a double-clickable `.app` file that works on other people's Macs is the
harder part (packaging, security warnings) and is not needed for the demo or the judges.
