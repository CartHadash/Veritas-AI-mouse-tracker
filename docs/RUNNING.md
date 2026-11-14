# How to run the project

Two parts:

- **The app** (server + interface): needs only this repository. The trained models the app
  uses (`models/detector/detector_v2.joblib` with `detector_v2_threshold.json`, and
  `models/corrector/weights_v4_s0.5.pt`) and 12 recorded demo tremors from test people
  (`server/demo_tremor.npz`) are included, so no dataset download is needed.
- **Rebuilding data and re-scoring the models**: needs the datasets (1.5 GB download).

This project is a prototype and is not medical advice.

---

## On macOS

### Run the app from a fresh clone

```bash
git clone https://github.com/CartHadash/Veritas-AI-mouse-tracker.git
cd Veritas-AI-mouse-tracker
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn server.main:app
```

Open http://127.0.0.1:8000 in Safari or Chrome. Stop the server with Ctrl+C.
(The built-in `python3` on macOS is 3.9, too old: install Python 3.12 from python.org.)

Check the server (with the server running, in a second terminal window, after
`source .venv/bin/activate`):

```bash
python server/test_ws.py
```

It sends 500 pointer samples in each filter mode and prints the reply time.

### The step 4 path check (any teammate, about 5 minutes)

With the app running, open http://127.0.0.1:8000/path_check.html . It replays 12
computer-generated mouse paths (10 s each) and asks how much each looks like a real person
using a mouse (1-5) and what looks wrong. Half come from the generator the models were
trained on, half from a more realistic version; you are told which only at the end. Copy the
report at the end into the group chat. Nothing is saved or sent anywhere.

### Check the whole-laptop tracker (team leader's lane, macOS only)

```bash
python -m tracker.demo                    # move the pointer in any app for 10 s
python -m pytest tracker/test_reader.py   # 5 automatic checks, no mouse needed
```

The demo should print a "Rate while moving" near 100 samples per second. No permission
prompt should appear. In the app, tracking stays off until it is switched on
(`POST /api/settings {"tracking": true}`).

### The assistant (team leader's lane; any system)

For AI answers, copy `.env.example` to `.env` and put the API key after
`ANTHROPIC_API_KEY=` (add `ANTHROPIC_WORKSPACE_ID=wrkspc_...` if the API asks for a
workspace). Never commit `.env`. Without it the panel shows a plain non-AI summary.

```bash
python -m assistant.standalone            # assistant alone, example summary: http://127.0.0.1:8001
python -m assistant.run_test_prompts      # the 13 test questions (costs a few cents)
```

### Rebuild the data and re-score everything (optional)

```bash
python scripts/download_data.py               # once; 1.5 GB, 10-30 minutes
python data_pipeline/look_at_data.py          # step 2: counts and two charts
python data_pipeline/tremor_library.py        # step 3: about 30 s
python data_pipeline/build_dataset.py         # step 5: about 20 s
python data_pipeline/build_dataset.py --tremor-scale 0.5         # half / double tremor sets: needed by
python data_pipeline/build_dataset.py --tremor-scale 2           #   evaluate_detector.py, so build them here
python -m pytest data_pipeline/test_split.py  # checks no person is in two splits
python evaluation/run_baselines.py            # step 6: about 4 minutes
python models/detector/train.py               # step 7: about 30 s
python evaluation/evaluate_detector.py --missed-target 0.2
python models/corrector/train.py              # step 8: about 2 minutes
python evaluation/evaluate_corrector.py       # about 1 minute
python models/corrector/time_live.py          # live speed on this machine
python evaluation/find_failures.py            # step 9
python data_pipeline/build_dataset.py --continuous               # step 12: pause-free movement
python models/detector/train.py --version v2 --with-continuous   # detector the app uses
python evaluation/evaluate_detector.py --missed-target 0.2 --version v2
python models/corrector/train.py --version v2 --scale-augment    # step 12 attempt (not kept)
python models/corrector/train.py --version v3 --loss distance    # after step 12
python evaluation/improvements.py --test      # needs detector v2 and correctors v2, v3
python evaluation/evaluate_corrector.py --detector v2
python models/corrector/train.py --version v4_s0.5 --loss distance --smooth 0.5   # corrector the app uses
python models/corrector/train.py --version v4_s2 --loss distance --smooth 2
python models/corrector/train.py --version v4_s8 --loss distance --smooth 8
python evaluation/smoothness.py --test        # chooses the v4 penalty on validation
python data_pipeline/make_demo_tremor.py               # demo page's replayed tremor (test people)
python data_pipeline/make_demo_tremor.py --people val  # the same for validation people
python evaluation/compare_modes.py            # filter modes on the demo page (validation people)
python evaluation/compare_modes.py --people test   # the final figure (test people, once)
python evaluation/data_facts.py               # step 14: dataset counts
python evaluation/check_results.py            # step 14: every number in RESULTS.md is sourced
# Note: check_results.py matches only with the committed model files. Retraining the corrector
# on another Mac gives slightly different numbers (training is not bit-identical across
# machines), so after a full rebuild elsewhere it reports those corrector numbers as not found.
python evaluation/click_sim.py                # click freeze, validation people's tremor
python evaluation/click_sim.py --people test  # click freeze, final figure (test people)
python evaluation/calibration_sim.py          # calibration test, validation people (about 7 min)
```

For the pixel-factor check in `evaluate_detector.py` (detector v1), also run
`python models/detector/train.py --tremor-scale 0.5` and `--tremor-scale 2` before it.

---

## On Windows

Use PowerShell. Install Python 3.12 from python.org and tick "Add python.exe to PATH". If
"Activate" fails with "running scripts is disabled", run
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.

### Run the app from a fresh clone

```powershell
git clone https://github.com/CartHadash/Veritas-AI-mouse-tracker.git
cd Veritas-AI-mouse-tracker
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn server.main:app
```

Open http://127.0.0.1:8000 in Chrome or Edge. Stop the server with Ctrl+C. On Windows the
whole-laptop tracker is not available (it is Mac-only); the app says so and works without it.

Check the server (second PowerShell window, after activating):

```powershell
python server\test_ws.py
```

The step 4 path check works the same way on Windows: open
http://127.0.0.1:8000/path_check.html (instructions in the macOS section).

### Rebuild the data and re-score everything (optional)

The same commands as on macOS, with `\` instead of `/` in the paths, for example
`python scripts\download_data.py` and `python data_pipeline\tremor_library.py`.
