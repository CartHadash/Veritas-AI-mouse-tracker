# Build guide: BUILDER lane

For the builder (Oleksandr) and their AI agent (Claude Code on the builder's MacBook). This
lane owns the data, both models, their evaluation, the server, the main interface code and
the system-wide stretch goal (`systemwide/`). Folder ownership: `docs/PROJECT_PLAN.md`.

**Agent:** read `CLAUDE.md` first, then `STATUS.md` ("What is left"). Almost every step is
built; what remains is checks by people, fixes, and helping the write-up. The original
step-by-step instructions are in git history (this file before Sun 15 Nov 10:45 CET).

**Builder (human):** you will explain this project to judges. Read `docs/EXPLAINED.md` and
`evaluation/results/RESULTS.md`, and ask your agent to re-explain anything unclear.

When you come back after a break: *"Read STATUS.md and BUILD_GUIDE_BUILDER.md and continue."*

## Rules that still matter every session

- Code must run on macOS **and** Windows: `pathlib` paths, `encoding="utf-8"` on every text
  file, `num_workers=0` (or worker code inside `if __name__ == "__main__":`), weights saved
  from the CPU and loaded with `map_location="cpu"`. The server must start without the
  Mac-only folders (`tracker/`, `systemwide/`).
- Run tools as `python -m <tool>` inside the activated `.venv` (commands: `docs/RUNNING.md`).
- Anything that changes a number: choose on validation, score test once, re-run
  `python evaluation/check_results.py`, and update `RESULTS.md`.
- Timings on the builder's Mac do not prove the demo Mac; ask the leader to re-run them.
- Before editing `web/`, pull: the team leader also edits it (UI work since Sat 22:00).
- After each change: `docs/EXPLAINED.md` entry, `STATUS.md`, tick here, then merge per `CLAUDE.md`.

## Steps

| Step | State | Where / what was done |
|---|---|---|
| 1 Environment | [x] | `requirements.txt` (pinned), `models/device.py` |
| 2 Look at the data | [x] | `data_pipeline/look_at_data.py` |
| 3 Tremor library | [x] | `data_pipeline/tremor_library.py`: 13,764 segments of 10.24 s |
| 4 Synthetic intended movement | [x] | `data_pipeline/synthetic_paths.py`. Changed: a realistic version 2 was added after the team's blind path check; the stress test (`evaluation/realism_stress.py`) showed no drop, so no retraining. Round 2 of the path check was cut (leader, Sun 10:45) |
| 5 Train / validation / test split | [x] | `data_pipeline/build_dataset.py`, 340 / 72 / 72 people, seed 42, `split.json` |
| 6 Baselines | [x] | `evaluation/run_baselines.py` (filters rewritten from scratch, Sat 21:59) |
| 7 Detector v1 | [x] | `models/detector/`, `evaluation/evaluate_detector.py` |
| 8 Corrector v1 | [x] | `models/corrector/`, `evaluation/evaluate_corrector.py` |
| 9 Where it fails | [ ] waiting | `evaluation/find_failures.py`, `failure_extras.py` -> `evaluation/results/failures/`. Tick when Oleksandr has read `failures.md` |
| 10 Server | [x] | `server/main.py`, `server/test_ws.py` |
| 11 Live demo page | [x] | `web/`. Leader's trackpad check of the current model, Sun ~11:00: "good enough" |
| 12 One improvement per model | [x] | Detector v2 kept; then corrector v3, v4, and v5 + gated One Euro (the app now), with Steadiest / Balanced / Faster |
| 13 Summary page | [x] | Now the Analysis tab of `web/index.html` (`summary.html` forwards there) |
| 14 Results package | [ ] waiting | `evaluation/results/RESULTS.md`, `check_results.py`. Tick when Oleksandr and the leader have read it |
| 15 Fresh-clone test | [x] | Passed on both Macs (`docs/STATUS_ARCHIVE.md`) |
| 16 Desktop window | cut | Leader's decision, Sun 10:45: the demo uses the browser |
| B3 System-wide correction | [x] | `systemwide/` works on the real cursor on the demo Mac (leader, Sun 11:04): visibly steadier after the detector's 2.56 s warm-up. Off-switch check and video clip: leader. Sun 15 Nov: click freeze, `--response`, idle updates added (`evaluation/systemwide_clicks.py`); leader re-checks |

Extras built on team members' ideas: click freeze (`evaluation/click_sim.py`), calibration
test (`evaluation/calibration_sim.py`, reports only), first-use guide (`web/tutorial.js`),
notch canceller (tested, not kept).

## If things go wrong

| Problem | What to do |
|---|---|
| "Address already in use" on port 8000 | An old server is still running: close its terminal, or use `--port 8001` |
| Works on the builder's Mac, fails on the demo Mac | Read the error text the leader put in `STATUS.md`; usual causes: a missing `encoding`, a hard-coded path, weights saved from the GPU |
| A script crashes with `UnicodeDecodeError` | A file was opened without `encoding="utf-8"` |
| `check_results.py` says a number is "not found" | A results file changed; re-run the script that writes it and update `RESULTS.md` |
| Out of time | Stop at the feature freeze (Sun 20:00). An honest evaluation and a working page beat a half-finished feature |
