Ideas per teammate:

#Godson
1. Personal calibration: Upon first use, the user follows a guided movement test lasting approximately 10 seconds with which the estimates the movement characteristics of the input device that allows it to adjusts its processing parameters.



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

