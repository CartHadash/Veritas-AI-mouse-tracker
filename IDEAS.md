# Ideas per teammate (and what happened to each)

Status as of Sun 15 Nov 10:45 CET. Numbers and details: the files named; never copy a number
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
   `improvements.md`). Action tasks still cause the most false alarms (`failures/failures.md`):
   **Delegated to the builder (Sun 15 Nov):** a cheap version with separate cut-offs for a
   moving and a still hand, chosen on validation (task in `STATUS.md`).
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
   text). **Read aloud built** (assistant answers, browser speech, no API). Larger text,
   dyslexia-friendly font and colour-blind-safe colours: not yet.
4. **"Feels laggy" -> let the user choose.** **Built:** Steadiest / Balanced / Faster control
   (`evaluation/response_levels.py`).
