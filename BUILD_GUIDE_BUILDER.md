# Build guide: BUILDER lane

For the builder and their AI agent (Claude Code on a **MacBook, Apple Silicon**). This lane
builds the heart of the project: the data, the two models, their evaluation, the server and
the main interface.

**Two computers, one project.** The builder works on their own Mac. The final demo runs on
the team leader's MacBook, which is a different machine. Everything in this lane must still
work on **both** macOS and Windows (a teammate or judge may use Windows). The section
"Working on two machines" below says how.

Changed: the builder moved from a Windows PC to a MacBook on Sat 14 Nov; the guide was
written for Windows, so the setup and command sections below were updated.

**Agent:** read `CLAUDE.md` first. Work through the steps in order. Tick each box when its
"Done when" is true. Keep this file accurate: if you do a step differently, rewrite the
step (rules in `CLAUDE.md`, "Keeping the instructions up to date").

**Builder (human):** you do not need to understand code to steer this. Your jobs are:
(1) do the short "Human setup" below, (2) answer the agent's **DECISION** questions (each
comes with a recommendation; "go with your recommendation" is a fine answer),
(3) read `docs/EXPLAINED.md` as it grows, and ask the agent to re-explain anything unclear.
You will have to explain this project to judges, so do not skip (3).

Not in this lane (the team leader builds these, in parallel): reading the pointer across
the whole laptop (`tracker/`), the Claude assistant (`assistant/`, `web/assistant/`), and
correcting the real cursor everywhere (`systemwide/`). Do not build them. You connect to
them through the three contracts in `docs/PROJECT_PLAN.md`.

---

## Human setup on the Mac (about 20 minutes plus the download)

Do these yourself, once. Use the **Terminal** app for every command below.

1. **Install Python 3.12** from https://www.python.org/downloads/macos/ (the "macOS 64-bit
   universal2 installer"). The Python that comes with macOS (3.9) is too old for PyTorch.
   Git comes with Apple's command-line tools; if `git --version` asks to install them, say yes.
   Also install **Claude Code** (the desktop app, or the command-line version).
2. **Check they work.** Open a new Terminal window and run each line. Each should print a
   version number (the second must say 3.12):

   ```bash
   git --version
   python3.12 --version
   ```

3. **Get the project and its data:**

   ```bash
   mkdir -p ~/dev && cd ~/dev
   git clone https://github.com/CartHadash/Veritas-AI-mouse-tracker.git
   cd Veritas-AI-mouse-tracker
   python3.12 -m venv .venv
   source .venv/bin/activate
   python scripts/download_data.py
   ```

   After the `source` line, the prompt starts with `(.venv)`. The last line downloads
   1.5 GB (about 12,700 small files) and can take 10–30 minutes. Let it run. It finishes
   with "PADS: done, all files OK."
4. **Keep the Mac awake** while the agent works: keep the charger connected and the lid
   open (System Settings → Battery → Options → "Prevent automatic sleeping when the display
   is off" while on power). Set it back after the hackathon.
5. **Start Claude Code in the folder** `~/dev/Veritas-AI-mouse-tracker`. Allow it to edit
   files and run commands in this folder without asking each time, otherwise it stops at
   every step.
6. **Give it this first message:**

   > You are the BUILDER agent, working on a Mac. Read CLAUDE.md, then the files it
   > lists, then follow BUILD_GUIDE_BUILDER.md from the first unticked step. Explain each
   > step to me in simple words before you do it, and stop to ask me at every DECISION.

When you come back after a break, say: *"Read STATUS.md and BUILD_GUIDE_BUILDER.md and
continue from the first unticked step."*

Every time you open a new Terminal window for this project, run these two lines first:

```bash
cd ~/dev/Veritas-AI-mouse-tracker
source .venv/bin/activate
```

(On Windows the equivalents are `python -m venv .venv` and `.venv\Scripts\Activate.ps1`;
see `CLAUDE.md`, "Commands".)

---

## Working on two machines (agent: read carefully)

The builder's machine is a Mac; the demo machine is the team leader's Mac (a different
one). Code must also stay runnable on Windows. A project that only runs on the builder's
laptop cannot be demonstrated. Follow these rules in every step.

**Commands on this machine**

- Create the environment with `python3.12 -m venv .venv` and activate it with
  `source .venv/bin/activate`; inside it the command is `python`. Run tools as
  `python -m <tool>` (for example `python -m uvicorn`, `python -m pytest`) so the right
  environment is always used.
- Prefer doing file work in Python scripts, which behave the same on every system.
- In every `.md` file, show commands for **both** macOS and Windows when they differ.

**Code that works on both systems**

- Build file paths with `pathlib.Path` or `os.path.join`. Never write a backslash or a
  drive letter in code. Use forward slashes in anything the browser sees.
- Open text files with `encoding="utf-8"` every time (Windows defaults to a different
  encoding and will break on characters like "°" or "–").
- Anything that starts worker processes (PyTorch `DataLoader` with `num_workers` above 0,
  `multiprocessing`) must be inside `if __name__ == "__main__":`, or it crashes on Windows.
  Simplest: keep `num_workers=0`; our data is small.
- No macOS-only or Windows-only libraries anywhere in this lane. The Mac-only pieces
  (`tracker/`, `systemwide/`) belong to the leader; your server must run with them absent
  (the situation on Windows, and on this Mac until the leader's code is merged).
- Line endings: the repository's `.gitattributes` keeps all text files with Unix line
  endings. Do not change that file.

**The processor, not the graphics card**

- Both Macs have an Apple GPU (`mps`); a Windows PC may have an NVIDIA card (`cuda`) or none. Pick
  the device in one helper used everywhere: `cuda` if available, else `mps` if available,
  else `cpu`. Our models are small enough to train on the CPU in minutes; do not spend
  time installing GPU drivers.
- Save model weights so they load on any machine: move the model to the CPU before saving,
  and load with `map_location="cpu"`.
- Speed measured on the builder's Mac does not prove speed on the demo Mac. Wherever a step asks for a
  timing, record the builder's Mac number and add a line under "Requests" in `STATUS.md` asking
  the leader to run the same script on the Mac.

**Proving it works on the Mac (do this early and often)**

- After step 1, after step 8, after step 11 and at step 15, push your branch and ask the
  team leader (via `STATUS.md` "Requests" and the group chat) to pull it on the Mac and
  run the commands in `docs/RUNNING.md`. Do not wait until Sunday evening to find out.
- `docs/RUNNING.md` must have two clearly separated sections: "On Windows" and "On macOS".

---

## How every step works (agent)

For each step: (1) tell your human in plain words what it is and why; (2) do it on a
branch if it is a big addition; (3) **run it** and check the "Done when"; (4) write the
plain-language entry in `docs/EXPLAINED.md`; (5) update `STATUS.md`, tick the box here,
push, and merge to `main` if the merge conditions in `CLAUDE.md` hold.

Time targets are in `docs/PROJECT_PLAN.md`. If a step is stuck for 30 minutes, choose the
simpler fallback written in the step, note it in `STATUS.md`, and move on.

---

## Phase 1: foundations (target: Saturday 16:00 CET)

### - [x] Step 1. Environment

**In plain words:** install the Python libraries the project needs and write them down so
teammates get the same ones.

**Do:** create `requirements.txt` with: `numpy`, `pandas`, `scipy`, `scikit-learn`,
`matplotlib`, `torch`, `fastapi`, `uvicorn[standard]`, `anthropic`, `python-dotenv`,
`pytest`. Install them with `python -m pip install -r requirements.txt` (the plain `torch`
package works on Apple Silicon and on Windows; no GPU drivers needed). Add each to
`docs/SOURCES.md` with its link. If the leader's lane has already added a line ending in
`; sys_platform == "darwin"`, leave it: pip skips it on Windows automatically.

Write `models/device.py` with one function that returns the best available device
(`cuda`, else `mps`, else `cpu`) and print which one this Mac uses. Any of them is fine for
models this small.

If `pip` fails on `torch` with "no matching distribution", the Python version is too new
for PyTorch: tell your human to install Python 3.12 and recreate `.venv`.

**Done when:** `python -c "import numpy, pandas, scipy, sklearn, torch, fastapi, anthropic"`
prints nothing and exits cleanly on the builder's Mac, **and** the team leader has confirmed the same
command works on the Mac after pulling (first cross-machine check).

### - [x] Step 2. Look at the data with your own eyes

**In plain words:** before training anything, open a few recordings and plot them. The
hackathon guide says this is the easiest way to catch bad data, and it gives us a chart
that proves the tremor is really there.

**Do:** read `docs/DATASETS.md`. Write `data_pipeline/look_at_data.py` that:

- counts PADS subjects per diagnosis, and by age band (under 60, 60–69, 70 and over) and sex;
- loads PADS subject 060, right wrist, task `Relaxed`, and TremorDB `rofh/s6rof.let`;
- for each, saves a chart with the signal over time (plus a 3-second zoom) and its
  **frequency spectrum** (use `scipy.signal.welch`), into `evaluation/results/figures/`.

A frequency spectrum shows how much of the movement happens at each speed of repetition;
a tremor shows up as a tall narrow peak between 3 and 12 times per second.

**Done when:** the script prints 469 subjects (276 Parkinson's, 79 healthy, 28 essential
tremor), and the two charts show peaks near 4.3 Hz and 4.9 Hz. If the numbers differ, stop
and tell your human: the data may be incomplete.

---

## Phase 2: turning the datasets into training data (target: Saturday 20:00 CET)

Background for the human, because judges will ask: **nobody has published mouse recordings
from people with tremor.** So we build our examples: we take *real tremor* measured on
patients' wrists and fingertips, and add it on top of *computer-generated* mouse movement.
Because we built each example ourselves, we know the correct answer for it (how much
tremor is in it, and what the clean movement was). That is what lets us train and score
models. The weakness is that it is a construction, and we say so openly.

### - [x] Step 3. The tremor library

**In plain words:** go through both datasets, pull out the shaking part of each recording,
and store it in one tidy file, together with who it came from.

**Do:** write `data_pipeline/tremor_library.py`, producing `data/derived/tremor_library.npz`.

- **PADS:** use the gyroscope (rotation), which is less disturbed by gravity than the
  accelerometer. Two of its three axes become the cursor's left-right and up-down.
  Use every diagnosis group, including healthy controls; keep the `condition`, `age`,
  `gender`, task and subject id with each segment.
- **TremorDB:** the signal is velocity; add it up over time (integrate) to get position.
  It has one axis, so pair each recording with a copy of itself shifted by a few seconds.
- **Isolate the tremor band:** keep only movement between 3 and 12 Hz (a band-pass filter;
  `scipy.signal.butter` with `filtfilt` is fine here because this is offline preparation).
- **Keep real size differences.** Do **not** rescale every segment to the same size. Use
  **one conversion factor for the whole dataset** from sensor units to pixels, so a patient
  with strong tremor stays stronger than a healthy person's tiny natural tremor.
- **Mark which segments "contain tremor"** using a fixed rule on the original recording
  (for example: a clear spectral peak in 3–12 Hz and enough power there). Decide the rule
  **now, before any model is trained, and never change it after seeing model results.**
  Report how many segments, subjects and seconds are marked, per diagnosis.
- Save a chart of 8 example segments with their spectra.

**DECISION 1: the pixel conversion factor.** There is no "true" value, because a wrist
sensor is not a mouse. Recommended: choose the factor so that the middle (median)
tremor-marked Parkinson's segment has an on-screen size of about 6 pixels, and later test
everything again at half and at double that factor to show the results do not depend on
the choice. The alternative is to rescale every segment into a fixed pixel range, which is
simpler but throws away the real differences between people.

**DECISION 2: which task types to include.** Recommended: all of them, labelled by type
(rest / postural / action), so we can report results per type. Action tasks are closest to
using a mouse, but in those the patient's deliberate arm movement is mixed in; the
band-pass removes most of it.

Done (Sat 14 Nov): DECISION 1 = A (median tremor-marked Parkinson's segment = 6 px RMS),
DECISION 2 = A (all tasks, labelled). Segments are 10.24 s (1024 samples). PADS uses the two
main directions (PCA) of the integrated, band-passed gyroscope. The rule is written at the
top of `data_pipeline/tremor_library.py`.
Changed: the "enough power" part of the rule compares each segment with the 95th percentile
of healthy controls doing the same task type, because deliberate movement in action tasks
puts as much 3-12 Hz power in healthy people as tremor does in patients.

**Done when:** the script runs in one command, prints the counts, and the example chart
shows clearly rhythmic segments for tremor-marked patients and nearly flat ones for healthy
controls. Write the rule, the factor and the counts in `docs/EXPLAINED.md`.

### - [ ] Step 4. Synthetic "intended" mouse movement

**In plain words:** generate realistic-looking mouse movement with no tremor in it: reaches
toward targets, pauses, small corrections. This plays the role of "what the person meant to do".

**Do:** write `data_pipeline/synthetic_paths.py`.

- Reaches between random points using a smooth speed-up-then-slow-down shape (a
  "minimum-jerk" profile, which matches how people really point), distances 50–900 px,
  durations 0.3–1.2 s.
- Pauses, slow drifts, small corrective movements near the target, curved paths.
- **Tremor look-alikes with no tremor**, so the detector cannot cheat: deliberate quick
  back-and-forth wiggles, fast small circles, sudden direction changes, and a little random
  sensor jitter. These are the cases we expect false alarms on.
- 100 samples per second, in pixels. A fixed random seed so it is repeatable.
- Save a chart of a few generated paths.

Done (Sat 14 Nov): `generate_path(rng, n)` returns positions and a per-sample "kind"
(still / reach / correction / drift / wiggle / circle / zigzag) so step 5 can describe each
window. Chart sent to the builder for the plausibility check.

**Done when:** a human looking at the chart finds the paths plausible, and variety is
obvious (not all straight lines of the same length).

### - [x] Step 5. The training, validation and test sets

**In plain words:** combine steps 3 and 4 into labelled examples, and split the *people*
into three groups: one to learn from, one to tune on, one locked away for the final score.
Splitting by person matters: if the same patient appears in both learning and testing, the
model can recognise the person instead of the tremor, and the score is fake.

**Do:** write `data_pipeline/build_dataset.py`.

- Split subjects 70% / 15% / 15% (train / validation / test), keeping each diagnosis group
  proportionally represented. Fixed seed. Save the lists to `data_pipeline/split.json` and
  commit that file (it contains only subject numbers).
- **Detector examples:** windows of 2.56 seconds (256 samples).
  - *Positive* (tremor present) = synthetic movement + a tremor-marked segment.
  - *Negative* (no tremor) = synthetic movement alone; synthetic movement + a healthy
    control's segment (their tiny natural tremor); synthetic movement + a patient segment
    that was *not* marked as tremor.
  - Each example keeps: label, tremor size in pixels, tremor frequency, subject id,
    diagnosis, age band, sex, task type, and whether the hand was mostly moving or still.
- **Corrector examples:** longer sequences of (shaky input → clean target), mixing all
  tremor sizes and also sequences with no tremor at all (the corrector must leave a steady
  hand alone).
- Print a table: number of examples per split, per label, per group.

Done (Sat 14 Nov): 484 people (TremorDB subject v3 has no recordings). Detector windows take
all 4 windows of each tremor-marked segment, 2 per healthy segment, 1 per unmarked patient
segment, plus 20% synthetic-only. Corrector sequences are 512 samples. Healthy segments that
pass the tremor rule are left out. `--tremor-scale 0.5` / `2` builds the DECISION 1 check
sets with suffix `_x0.5` / `_x2`.

**Done when:** no subject id appears in more than one split (write a test in
`data_pipeline/test_split.py` that fails if one does, and run it), and the table is in
`docs/EXPLAINED.md`.

**Tell your human:** how many test subjects there are in each age band and sex. If a group
has fewer than about 10, say so now; results for that group will be unreliable and the
write-up must say that.

---

## Phase 3: baselines and first models (target: Saturday midnight CET)

A **baseline** is the simplest possible way to do the job. Judges want our model's score
shown next to it, so they can see how much the AI adds.

### - [x] Step 6. Measure the baselines

**Do:** write `evaluation/metrics.py` (shared scoring functions) and
`evaluation/run_baselines.py`. Results go to `evaluation/results/baselines.md`.

**Detector baselines**, scored on validation and test:

1. *Always "no tremor".* Its accuracy will look decent if most examples are negative,
   while it misses every single case. This is the baseline the briefs describe.
2. *Frequency rule.* Says "tremor" when enough of the window's movement power lies between
   3 and 12 Hz. Choose its threshold on validation only.

For each, report: **missed cases** (share of real tremor windows called "no tremor"),
**false alarms** (share of no-tremor windows called "tremor"), and overall accuracy, in
that order.

**Corrector baselines**, scored on test sequences:

1. No filter.
2. Lower pointer sensitivity (cursor moves half as far as the hand; also try a quarter).
   Compare fairly: measure error relative to the intended movement scaled the same way,
   and count the extra hand travel as its cost.
3. The three classical filters in `baselines/classical_filters.py`.

For each, report: average distance between the output and the intended path (while moving
and while still, separately), how much of the 3–12 Hz shake is removed, and **lag** (how
many milliseconds the output trails the intended movement).

Done (Sat 14 Nov): the frequency rule uses the window's velocity spectrum. It is reported
at two cut-offs (best balance; missed <= 10% on validation). Each classical filter is shown
with its pre-hackathon settings and with settings chosen on validation (lowest average
distance).
Changed: filters are also tuned on validation, because their old settings were chosen on
a fake sine-wave tremor and judges could call an untuned baseline unfair.

**Done when:** both tables exist, produced by one command. The frequency rule should do
well on still windows and worse on moving ones; if it scores near-perfect everywhere, the
task is too easy: tell your human and add harder look-alikes in step 4 before going on.

### - [x] Step 7. Detector, version 1

**In plain words:** train the first model that decides "tremor or not" for a 2.56-second
window of cursor movement, and estimates its strength.

**DECISION 3: what kind of model first.**
Option A (recommended): a classic machine-learning model from scikit-learn (for example
gradient boosting or a random forest) fed with about 20 hand-made measurements of each
window: power in several frequency bands, peak frequency and sharpness, speed statistics,
how often direction reverses. Trains in seconds, and we can show *which measurements
mattered*, which makes it easy to explain to judges.
Option B: a small neural network that reads the raw movement directly. More "AI-looking",
but slower to get right and harder to explain. We try this as version 2 in step 12.

**Do:** `models/detector/features.py`, `models/detector/train.py`,
`models/detector/predict.py`. Train on train, choose settings and the decision threshold
on validation, then score **once** on test.

**DECISION 4: where to set the alarm threshold.** The model outputs a score from 0 to 1;
we choose the cut-off. A low cut-off catches more tremor but raises more false alarms. For
our user a false alarm only means slightly more smoothing than needed, while a missed case
means the cursor stays shaky. Recommended: choose the cut-off that keeps missed cases under
about 10% on validation and report the false alarms that result. Show your human the
trade-off table and let them pick.

**Report** (`evaluation/results/detector_v1.md`): missed cases and false alarms on test,
next to both baselines; the same broken down by age band, sex, diagnosis (Parkinson's vs
essential tremor), tremor size (mild / medium / strong), task type, and moving vs still;
and the error of the strength estimate in pixels. Repeat the headline numbers at half and
double the pixel factor from DECISION 1.

Done (Sat 14 Nov): DECISION 3 = A (HistGradientBoosting on 19 features, plus a size
regressor). DECISION 4 = at most 20% missed on validation (cut-off 0.165, saved in
`models/detector/detector_v1_threshold.json`). Test scoring is a separate script,
`evaluation/evaluate_detector.py`, so `train.py` never touches test people. Half/double:
`build_dataset.py` and `train.py` with `--tremor-scale 0.5` / `2`.
Changed: the cut-off target is 20% missed, not 10%, because 10% gave 46.5% false alarms on
validation (the builder chose this).

**Done when:** the report exists and the model beats the frequency rule on at least the
moving windows. **If it does not beat the baseline, say so plainly** in `STATUS.md`; that
is an acceptable result to report, and step 12 is where we try to improve it.

### - [x] Step 8. Corrector, version 1

**In plain words:** train a small neural network that looks at the last half-second of
shaky cursor movement and outputs where the cursor *should* be right now.

**Do:** `models/corrector/model.py`, `train.py`, `live.py`.

- Input: the last 48–64 samples (about half a second) as movement steps (dx, dy), not
  screen positions, so it works anywhere on the screen.
- Output: the corrected current position, expressed as an offset from the raw position.
- **Causal:** it may never see future samples. This is what makes it usable live.
- Small: a few 1D convolution layers or a small GRU, a few tens of thousands of weights.
  Training must finish in under 20 minutes on the builder's Mac's CPU (use `models/device.py` and
  `num_workers=0`).
- Train to minimise the distance to the clean path. Save the best version by validation
  score to `models/corrector/weights.pt` (must be under 2 MB). Move the model to the CPU
  before saving, so the file loads on the Mac.
- `live.py` wraps it with the same `reset()` / `update(x, y, t)` shape as the classical
  filters, resampling the incoming samples to 100 per second.
- **Use the detector to control it:** when the detector's tremor score is low, blend back
  toward the raw cursor, so a steady hand gets no added lag. This is the point where the
  two models work as one system.
- Measure how long one live update takes on the CPU, with a script
  (`models/corrector/time_live.py`) the leader can also run on the Mac.

**Report** (`evaluation/results/corrector_v1.md`): the same measures as the corrector
baselines, side by side, on test subjects only.

Done on the builder's Mac (Sat 14 Nov): dilated causal 1-D CNN, 64-step input, 10,722
weights; trained 6,000 steps (119 s). Test scoring in `evaluation/evaluate_corrector.py`
(also scores One Euro switched by the detector gate). Leader's Mac check passed (worst
1.5 ms per update on the demo Mac).

**Done when:** one live update takes well under 8 ms on the builder's Mac, the report exists, the
loss-curve chart is saved, and the leader has loaded `weights.pt` and run the timing script
on the Mac (second cross-machine check). Beating One Euro is the hope, not the
requirement; report whatever is true.

### - [ ] Step 9. Where it fails

**In plain words:** the briefs require at least one example the model gets wrong, with our
best explanation. Good failure analysis scores higher than a suspiciously perfect result.

**Do:** `evaluation/find_failures.py`. Save to `evaluation/results/failures/`:

- 3 missed cases and 3 false alarms from the detector, each as a chart of the window and
  its spectrum, with one or two sentences on the likely reason (for example: mild tremor
  hidden under a fast reach; a deliberate wiggle that looks rhythmic).
- 2 sequences where the corrector does worse than no filter or than One Euro.
- A short `failures.md` summarising the patterns.

Done (Sat 14 Nov): `evaluation/find_failures.py` writes the charts plus `failure_facts.md`
(facts and failure counts per group); `failures.md` holds the explanations. Waiting for the
builder to read it before ticking.

**Done when:** the files exist and your human has read `failures.md`.

**Checkpoint (Saturday night):** update `STATUS.md` with the real numbers. This is the
official "baseline and first model work" milestone. Then sleep.

---

## Phase 4: the app (target: Sunday 13:00 CET for the live demo, 18:00 for the rest)

### - [x] Step 10. The server

**In plain words:** a small Python program that runs on the user's computer, keeps the two models
loaded, and talks to the interface in the browser.

**Do:** `server/main.py` using FastAPI. Run with `python -m uvicorn server.main:app`
(the same command works on Windows and macOS).

- Serves the interface files from `web/` at `http://127.0.0.1:8000`. Local only: bind to
  `127.0.0.1`, never `0.0.0.0`.
- **`/ws/cursor`** (a WebSocket, which is a connection that stays open so messages flow
  both ways quickly): the browser sends pointer samples from the demo page; the server
  replies to each with the corrected position, the detector's tremor score, and the
  estimated strength and frequency.
- **`GET /api/summary`**: returns the session summary exactly as in Contract 2 of
  `docs/PROJECT_PLAN.md`. Until the leader's tracker exists, build it from the demo page's
  samples.
- **Leader's modules, if present:** try to import `tracker` and `assistant`. If `tracker`
  is there, start it and feed its samples (Contract 1) into the detector and the summary.
  If `assistant.router` is there, include it. If either is missing **or fails to
  import** (the tracker cannot load on Windows), carry on without it and say so on the
  page. Test the "tracker missing" path by running without the leader's folders; the
  "tracker present" path can be tested on either Mac once the leader's code is merged
  (it may need the Accessibility permission: ask your human first). Never edit
  files inside `tracker/` or `assistant/`.
- `POST /api/settings` for the filter mode (none / low sensitivity / One Euro / learned),
  filter strength, and demo tremor on/off.
- Write `docs/RUNNING.md`: the exact commands to start the app from a fresh clone, in two
  sections, "On Windows" and "On macOS".

**DECISION 5: where the corrector runs.** Option A (recommended): in Python on the server,
with each sample making a round trip over the WebSocket; on one laptop this adds about a
millisecond and keeps one copy of the model. Option B: convert the model to run inside the
browser (ONNX); no round trip, but an extra conversion step that can eat hours.

Done (Sat 14 Nov): DECISION 5 = A. Also `POST /api/reset` (new session) and
`GET /api/status`. Demo tremor is replayed by the server from `server/demo_tremor.npz`
(test people only), so the app needs no dataset download. When the leader's tracker has
data, `/api/summary` adds an optional `whole_laptop` block.

**Done when:** a small test script can connect to `/ws/cursor`, send 500 samples and get
500 replies, and the average reply time is printed and noted in `STATUS.md`.

### - [ ] Step 11. The interface: live demo page

**In plain words:** the page judges will actually see. One look should show a shaky cursor
on one side and a steady one on the other.

**Do:** `web/index.html`, `web/app.js`, `web/styles.css`. Plain HTML, CSS and JavaScript,
no build tools.

- A practice area with small targets to click. The system cursor is hidden inside it; we
  draw two: a faint "raw" cursor and a solid "corrected" one.
- **Demo tremor switch:** since none of us has tremor, this adds a real patient's tremor
  (from the *test* subjects in the library) to the user's live movement. The page must say
  clearly, whenever it is on: "Demo mode: replaying recorded tremor from a public dataset."
- Filter mode buttons: none / lower sensitivity / One Euro / our learned model.
- A live tremor meter from the detector: tremor score, estimated frequency, strength.
- A running tally: targets hit, misses, average time per target, per filter mode.
- The footer line: "This project is a prototype and is not medical advice."
- Leave an empty container `<div id="assistant-panel"></div>` and, if the file exists,
  load `web/assistant/assistant.js`. That panel belongs to the leader.

**DECISION 6: the look.** Show your human two or three quick style directions (for example
calm and clinical, dark and technical, warm and friendly) as small mock-ups and let them
choose. The user is someone with tremor, often older: large text, large buttons, strong
contrast, nothing that requires precise clicking outside the practice area.

**DECISION 7: plain JavaScript or a framework.** Recommended: plain JavaScript; it needs
no installation and the builder can read it. A framework (React) only if your human
already knows it.

Test the page in **Safari and Chrome on the builder's Mac**, and write it with standard browser
features only, because on the Mac it will be opened in Safari or Chrome. Use the browser's
pointer events, which behave the same for a mouse and a trackpad.

Done on the builder's Mac (Sat 14 Nov): DECISION 6 = C (warm and friendly), DECISION 7 =
plain JavaScript. Tested in the Claude app's built-in browser with simulated pointer
movement. Waiting for the builder's own try and the leader's Mac/trackpad check before ticking.

**Done when:** your human can open the page, switch demo tremor on, and see the corrected
cursor visibly steadier than the raw one, switching between filter modes live; **and** the
leader has run the same page on the Mac with the trackpad (third cross-machine check).

### - [x] Step 12. One measured improvement to each model (Sunday morning)

**In plain words:** the official schedule asks for "one improvement, measured". Change one
thing, measure before and after on validation, keep it only if it helps, then score on test.

**Do, detector:** pick the most promising of: the small neural network from DECISION 3
option B; better features aimed at the failure patterns from step 9; more look-alike
negatives. **Do, corrector:** pick one of: a longer input window; a loss that also
penalises lag; training with more no-tremor sequences.

Record in `evaluation/results/improvements.md`: what was changed, why, validation score
before and after, test score of the kept version. If the change did not help, **keep the
record anyway**; "we tried X and it did not help" belongs in the write-up.

Done (Sat 14 Nov): detector = "more look-alike negatives" (pause-free movement windows,
`build_dataset.py --continuous`), kept as v2; corrector = trained on tremor 0.5x-2x (Godson's
DPI point), not kept. `evaluation/improvements.py`; `evaluate_detector.py --version v2`;
`evaluate_corrector.py --detector v2`. The live detector now runs on a background thread.
Changed: the corrector change was size mixing rather than one of the three listed options,
because it answered a teammate's question and could be measured at x0.5 / x1 / x2.

**Done when:** `improvements.md` exists with real before/after numbers for both models, and
the app loads whichever versions won.

### - [x] Step 13. The summary page

**In plain words:** turn a session's measurements into a few clear charts.

**Do:** `web/summary.html` (or a tab), fed by `GET /api/summary`.

- Tremor over the session (share of time detected, strength), typical frequency.
- Steadiness score, distance moved, clicks and click accuracy in the practice area.
- When the leader's tracker is running: the same from whole-laptop movement, labelled as such.
- Wording for a general reader. No medical language: "tremor-like movement was detected in
  about a third of your active time", never "your condition is worsening".
- Draw charts with the browser's canvas, or include one small chart library **as a file in
  the repo** (not from the internet), so the demo works offline. Cite it in `SOURCES.md`.

Done (Sat 14 Nov): `web/summary.html`, `summary.js`, `summary.css`; canvas charts, no library.
Checked with a 75 s simulated session through the server; numbers match `/api/summary`.

**Done when:** the page shows real values from a live session and the numbers match what
`/api/summary` returns.

---

## Phase 5: hand-over and finish (feature freeze Sunday 21:00 CET)

### - [ ] Step 14. Results package for the writer

**Do:** write `evaluation/results/RESULTS.md`, generated or checked against script output:

- One table for the detector: baselines vs our model: missed cases, false alarms, accuracy.
- The same per group (age band, sex, diagnosis), with the number of test subjects in each.
- One table for the corrector: no filter, lower sensitivity, classical filters, our model.
- The pixel-factor sensitivity check.
- Dataset facts: how many subjects and examples in each split, how the data was cleaned.
- Links to the 3 best charts and to the failure examples.
- A "what did not work" list.
- Five plain sentences a judge could be told in 30 seconds.

**Done when:** your human and the team leader have read it and found nothing they cannot
explain. If they cannot explain something, fix `docs/EXPLAINED.md` until they can.

### - [ ] Step 15. Fresh-clone test

**In plain words:** judges will open our link. Make sure someone starting from nothing can
run it.

**Do:** clone the repository into a new folder (for example `~/dev/fresh-test`), follow
the "On macOS" part of `docs/RUNNING.md` exactly, and confirm the app starts and the
evaluation scripts run (copy the existing `data` folder across instead of downloading
again). Fix anything that was missing. Check no file over a few MB and no `.env` is in git.
Then ask the leader to do the same on the Mac with the "On macOS" part. **The Mac result is
the one that counts**, because that is the demo machine.

**Done when:** it works from a fresh clone on both machines and `STATUS.md` says so.

### - [ ] Step 16 (only if everything above is done). Desktop-app window

**In plain words:** make the interface open in its own window instead of a browser tab.

**Do:** add `pywebview`; a short `desktop.py` starts the server in the background and opens
the page in a native window. `pywebview` works on both Windows and macOS but uses a
different built-in browser on each, so it must be tried on the Mac before anyone relies on
it for the demo. Do not attempt to build an installable `.exe` or `.app`.

**Done when:** `python desktop.py` opens the app in its own window on the builder's Mac, and the
leader has tried it on the Mac. If it misbehaves on the Mac, the demo uses the browser.

---

## If things go wrong

| Problem | What to do |
|---|---|
| PADS will not download | Use TremorDB only (16 subjects). Results will be weak for group checks; say so. Tell the team leader at once |
| The detector cannot beat the frequency rule | Report it honestly. Focus the story on moving windows and on the strength estimate, and on what we learned |
| The corrector is worse than One Euro | Ship One Euro controlled by the detector as the live filter, and present the learned corrector as an experiment with its real numbers |
| "running scripts is disabled on this system" | The human runs `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once (Human setup, step 3) |
| `python` opens the Microsoft Store or is "not recognized" | Python is not on the PATH: re-run the installer, "Modify", tick the PATH option, reopen PowerShell (Windows only; on the Mac use `python3.12`) |
| A script crashes with `UnicodeDecodeError` or `charmap` | A file was opened without `encoding="utf-8"`; add it |
| Training crashes with a "freeze_support" or "spawn" error | Something starts worker processes outside `if __name__ == "__main__":`; set `num_workers=0` |
| "Address already in use" on port 8000 | An old server is still running: close its terminal window, or start on another port with `--port 8001` |
| It works on the builder's machine but fails on the demo Mac | Read the Mac's error text from `STATUS.md`; the usual causes are a backslash in a path, a missing `encoding`, or weights saved from a GPU |
| WebSocket feels laggy | Send samples in small batches, or lower the rate to 60 per second. Measure before and after |
| Out of time on Sunday evening | Stop at the feature freeze. A working detector with an honest evaluation and a plain page beats a half-finished app |
