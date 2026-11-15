# Ideas per teammate (and what happened to each)

Status at the feature freeze, Sun 15 Nov 15:20 CET (no new ideas are built after this). Numbers and details: the files named; never copy a number
from here into the write-up without checking `evaluation/results/RESULTS.md`.

## Godson

1. **Personal calibration** (a 10 s guided test that tunes the processing to the user's device).
   **Built, reports only.** "Calibrate for my mouse (10 s)" on the Practice tab: hold a dot,
   then follow it; it reports each filter's distance from the dot, the samples per second and
   the shaking. Letting it choose the filter was tested in a simulation
   (`evaluation/calibration_sim.py`, validation) and, with the network alone, did worse than
   always using our model, so it never switches the filter by itself. Re-run with the app's
   current model, choosing would now help, so since Sun 15 Nov a "Use <filter>" button after the
   test lets the person switch with one tap (never automatic). Explained in
   `docs/EXPLAINED.md` "Calibration test".

## Timofey

1. **Movement-aware detector** (stricter during fast, deliberate movement). **Partly covered**
   by detector v2 (false alarms on pause-free movement fell from 45.3% to 20.4%,
   `improvements.md`). Action tasks still cause the most false alarms (`failures/failures.md`).
   A cheap version (separate cut-offs for a moving and a still hand) was **tested and not
   kept**: false alarms while moving went 30.3% -> 31.1% on validation (`moving_cutoffs.md`).
   A real fix needs retraining: a "what we'd do next" item.
2. **Click freeze** (hold the shown cursor still while the button is down). **Built** (at most
   0.3 s). Simulation: `evaluation/click_sim.py`, `click_freeze_test.md`.
3. **Sticky targets** (buttons gently pull the cursor in when tremor is detected). **Cut** for
   time (leader, Sun 10:45); a "what we'd do next" item for the write-up.
4. **Trends across days.** **Built as session history** (numbers only, kept on the laptop; the
   assistant may compare pointer numbers between sessions but never judges health trends).
   Shown in the Analysis tab.

## Oleksandr

1. **First-use guide** (it was unclear what to do on first sight). **Built:** `web/tutorial.js`.
2. **Notch canceller** (remove the tremor's own rhythm). **Tested, not kept:**
   `evaluation/results/notch_canceller.md`.
3. **Accessibility** (read aloud, dyslexia-friendly font, colour-blind-safe colours, larger
   text). **Built:** read aloud (assistant answers, browser speech, no API), a "Larger text"
   switch and an "Easier-to-read text" switch (OpenDyslexic font). Colour-blind-safe colours:
   not built (frozen).
4. **"Feels laggy" -> let the user choose.** **Built:** Steadiest / Balanced / Faster control
   (`evaluation/response_levels.py`).
5. **Live walkthrough** (the first-use guide shows each step on the real page). **Built:** `web/tutorial.js`.

## Built later on Sunday from team requests

- **Click where you aimed** (Timofey, after the real-cursor test): a click lands at the average
  of the last 0.1 s of the shown cursor while tremor is corrected. Built on the page and
  system-wide (`systemwide_clicks.md`, `click_freeze_test.md`).
- **Steady cursor everywhere** (Timofey): the correction on the real macOS cursor in every app,
  switched on from the page. Built and checked by hand.
- **Exercises** (Timofey): trace the spiral, a fair 10 + 10 test, hold Space to peek. Built.
- **Everyday targets** (Timofey): the practice target is a button, checkbox, folder, close
  button, link or "Save" button. Built.
- **Assistant action buttons** (Timofey) and **assistant hardening** (Oleksandr). Built; 28/28
  test questions (`assistant/test_prompts.md`).
