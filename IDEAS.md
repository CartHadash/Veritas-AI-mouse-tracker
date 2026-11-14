Ideas per teammate:

#Godson
1. Personal calibration: Upon first use, the user follows a guided movement test lasting approximately 10 seconds with which the estimates the movement characteristics of the input device that allows it to adjusts its processing parameters.
   How it could be built (discussed by Timofey with his agent, Sat 14 Nov):
   - The test, about 10 s: hold the pointer on a dot (4 s), follow a slowly moving dot
     (4 s), click 3 targets (2 s).
   - What it measures: the device's sample rate and timing gaps; the shake size (px) and
     peak frequency (Hz) during the still part; normal movement speed; how long a click is held.
   - What it changes: (a) a scale factor so the detector sees movement at the size it was
     trained on (step 7 showed false alarms go from 27.0% to 34.0% when the pixel factor
     doubles); (b) the correction strength (our model helps little on mild tremor and more on
     strong, `evaluation/results/demo_modes.md`); (c) the click-freeze time from the measured
     hold time. Note: measuring the user's tremor size on the still dot is exactly what the
     detector already does, so the first version can reuse its `size_px` output.
   - Rules: kept in memory for the session only (decision L1); never used for training
     (rule 9); worded as "settings for your device", never as a diagnosis.
   - How to prove it helps: in a simulation, calibrate on the first 10 s of each test-person
     recording at half / normal / double pixel scale, then score the rest, against no calibration.
   - Owner: server/ and web/ are the builder's folders.



#Timofey
1. Movement-aware detector: be stricter before flagging tremor during fast, deliberate
   movement. Why: `evaluation/find_failures.py` shows 43.5% false alarms on action-task
   segments vs 19.0% at rest.
2. Click freeze: hold the corrected cursor still for about 100 ms when the button goes
   down, so tremor at the moment of the click does not push it off the target.
3. Sticky targets: when tremor is detected, buttons and links gently pull the cursor in
   when it is close to them.
4. Trends across days: keep a local history so the user can see whether tremor-like
   movement changes over time (already noted as a future extension in decision L1).

Oleksandr
1.

