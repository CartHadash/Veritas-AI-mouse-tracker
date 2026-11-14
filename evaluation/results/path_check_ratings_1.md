# Step 4 path check, round 1 (the team's blind ratings)

Report produced by `web/path_check.html` (paths from `python data_pipeline/make_path_check.py`,
seed 2026: current generator vs realistic version 1), rated by Timofey (team leader) and pasted
into the group chat on Sat 14 Nov. Ratings only; no mouse data. One rater, 6 paths per
version: a small sample.

    Current generator (models trained on it): average 2.3 / 5 over 6 paths; problems: too smooth / robotic 5, odd shapes (wiggles, circles) 2, pauses look wrong 2, too straight 2, too slow 1, too fast 1
    Realistic version: average 1.5 / 5 over 6 paths; problems: too smooth / robotic 6, too straight 6, pauses look wrong 2, jumps 1, odd shapes (wiggles, circles) 1, shaky / jittery 1
    Per path:
    P1 (current): 3/5, too smooth / robotic, odd shapes (wiggles, circles)
    P2 (current): 2/5, too smooth / robotic, pauses look wrong, odd shapes (wiggles, circles)
    P3 (realistic): 1/5, too smooth / robotic, too straight, jumps
    P4 (realistic): 2/5, too smooth / robotic, too straight
    P5 (realistic): 1/5, too smooth / robotic, too straight, pauses look wrong
    P6 (realistic): 1/5, too smooth / robotic, too straight, pauses look wrong, odd shapes (wiggles, circles)
    P7 (current): 3/5, too straight
    P8 (current): 2/5, too smooth / robotic, pauses look wrong
    P9 (current): 2/5, too smooth / robotic, too straight, too slow
    P10 (current): 2/5, too smooth / robotic, too fast
    P11 (realistic): 1/5, too smooth / robotic, too straight, shaky / jittery
    P12 (realistic): 3/5, too smooth / robotic, too straight

What it told us: both versions look computer-made; realistic version 1 looked worse (too
straight on every path). Led to realistic version 2 (see `docs/EXPLAINED.md`, step 4).
