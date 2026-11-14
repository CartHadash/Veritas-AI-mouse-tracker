# How to run the project

Two parts:

- **The app** (server + interface): needs only this repository. The trained models
  (`models/detector/detector_v1.joblib`, `models/corrector/weights.pt`) and a few recorded
  demo tremors (`server/demo_tremor.npz`) are included, so no dataset download is needed.
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

### Check the whole-laptop tracker (team leader's lane, macOS only)

```bash
python -m tracker.demo                    # move the pointer in any app for 10 s
python -m pytest tracker/test_reader.py   # 5 automatic checks, no mouse needed
```

The demo should print a "Rate while moving" near 100 samples per second. No permission
prompt should appear. In the app, tracking stays off until it is switched on
(`POST /api/settings {"tracking": true}`).

### Rebuild the data and re-score everything (optional)

```bash
python scripts/download_data.py               # once; 1.5 GB, 10-30 minutes
python data_pipeline/look_at_data.py          # step 2: counts and two charts
python data_pipeline/tremor_library.py        # step 3: about 30 s
python data_pipeline/build_dataset.py         # step 5: about 20 s
python -m pytest data_pipeline/test_split.py  # checks no person is in two splits
python evaluation/run_baselines.py            # step 6: about 4 minutes
python models/detector/train.py               # step 7: about 30 s
python evaluation/evaluate_detector.py --missed-target 0.2
python models/corrector/train.py              # step 8: about 2 minutes
python evaluation/evaluate_corrector.py       # about 1 minute
python models/corrector/time_live.py          # live speed on this machine
python evaluation/find_failures.py            # step 9
python data_pipeline/build_dataset.py --continuous              # step 12
python models/detector/train.py --version v2 --with-continuous
python models/corrector/train.py --version v2 --scale-augment   # (needs the _x0.5/_x2 sets)
python evaluation/improvements.py --test
python evaluation/evaluate_detector.py --missed-target 0.2 --version v2
python evaluation/evaluate_corrector.py --detector v2
python models/corrector/train.py --version v3 --loss distance   # the corrector the app uses
python data_pipeline/make_demo_tremor.py      # the demo page's replayed tremor (test people)
python evaluation/compare_modes.py            # filter modes on the demo page (no data needed)
```

For the pixel-factor check in `evaluate_detector.py`, first run
`python data_pipeline/build_dataset.py --tremor-scale 0.5` and `--tremor-scale 2`, then
`python models/detector/train.py --tremor-scale 0.5` and `--tremor-scale 2`.

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

### Rebuild the data and re-score everything (optional)

The same commands as on macOS, with `\` instead of `/` in the paths, for example
`python scripts\download_data.py` and `python data_pipeline\tremor_library.py`.
