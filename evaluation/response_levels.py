"""
response_levels.py - what each choice of the page's "Steadier or more responsive" control does.
(The person picks between less shake and less lag; it starts at steadiest.)

The three levels (models/corrector/live.py RESPONSE_LEVELS) are three points of the tuning grid in
evaluation/results/tune_lag.md. This script checks them through the page's real path: it sets
server.settings["response"] exactly as the page does (POST /api/settings), then runs the demo
page's own server code with replayed tremor (mild/medium/strong x reaching/gliding/still,
browser-like timing), as evaluation/tune_lag.py does. Nothing is chosen here: it only reports.

It also checks that switching level while the cursor moves does not make it jump: the largest
single step of the shown cursor in a run that switches every 2 s, against runs that never switch.

Run from the repository folder (a few minutes):
    python evaluation/response_levels.py
Writes evaluation/results/response_levels.md.
"""

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import evaluation.compare_modes as cm  # noqa: E402
import server.main as server  # noqa: E402
from evaluation.vs_one_euro import measure  # noqa: E402
from models.corrector.live import RESPONSE_LEVELS  # noqa: E402

RESULT = ROOT / "evaluation" / "results" / "response_levels.md"
NAMES = {"steadiest": "Steadiest (default)", "balanced": "Balanced", "responsive": "Faster"}


def averages(level, people):
    """Average distance, shake, jerk over 9 situations and average lag over the moving ones."""
    server.DEMO_TREMOR_FILE = cm.DEMO_FILES[people]
    server.settings["response"] = level
    try:
        t, paths = cm.intended_paths(rate=60, uneven=True)
        rows, lags = [], []
        for tremor in ["mild", "medium", "strong"]:
            for name in ["reaches", "glide", "still"]:
                out, _ = cm.run("learned", t, paths[name], level=tremor)
                m = measure(out, paths[name], t, moving=(name != "still"))
                rows.append(m)
                if "lag" in m:
                    lags.append(m["lag"])
    finally:
        server.settings["response"] = "steadiest"
    result = {k: float(np.mean([r[k] for r in rows])) for k in ("distance", "shake", "jerk")}
    result["lag"] = float(np.mean(lags))
    return result


def biggest_step(switching, t, path):
    """Largest jump of the shown cursor between two samples (px), strong tremor, reaching.
    switching=True changes the level every 2 s, the way a person clicking the control would."""
    server.settings.update(mode="learned", strength=1.0, demo_tremor=True, demo_level="strong",
                           response=switching if isinstance(switching, str) else "steadiest")
    session = server.CursorSession(server.SessionStats())
    session.detector.pool = None
    order = list(RESPONSE_LEVELS)
    shown = []
    try:
        for ti, (x, y) in zip(t, path):
            if switching is True:
                server.settings["response"] = order[int(ti // 2) % len(order)]
            reply = session.update(float(ti), float(x), float(y))
            shown.append((reply["x"], reply["y"]))
    finally:
        server.settings["response"] = "steadiest"
    shown = np.array(shown)[t >= cm.WARMUP]
    return float(np.linalg.norm(np.diff(shown, axis=0), axis=1).max())


def table(results):
    lines = ["| Choice on the page | Lag while moving (ms) | Distance | Shake | Jerk |", "|---|---|---|---|---|"]
    for level, r in results.items():
        lines.append("| %s | %.0f | %.2f | %.2f | %.2f |" % (NAMES[level], r["lag"], r["distance"], r["shake"], r["jerk"]))
    return lines


def main():
    lines = ["# The page's \"Steadier or more responsive\" choice", "",
             "Produced by `python evaluation/response_levels.py`. Each choice set through `server.settings` as the "
             "page sets it, then the demo page's server code with replayed tremor, browser-like timing; averages "
             "over mild/medium/strong x reaching/gliding/still (lag: reaching and gliding only). Distance, shake "
             "and jerk in px, as in `vs_one_euro.py`.", ""]
    for people, title in [("val", "Validation people"), ("test", "Test people")]:
        results = {level: averages(level, people) for level in RESPONSE_LEVELS}
        lines += ["## %s" % title, ""] + table(results) + [""]
        print("\n".join(lines[-6:]))

    server.DEMO_TREMOR_FILE = cm.DEMO_FILES["val"]
    t, paths = cm.intended_paths(rate=60, uneven=True)
    steps = {level: biggest_step(level, t, paths["reaches"]) for level in RESPONSE_LEVELS}
    switched = biggest_step(True, t, paths["reaches"])
    lines += ["## Switching while moving (validation people, strong tremor, reaching)", "",
              "| Run | Largest single step of the cursor (px) |", "|---|---|"]
    lines += ["| Always %s | %.2f |" % (NAMES[level], s) for level, s in steps.items()]
    lines += ["| Switching level every 2 s | %.2f |" % switched, "",
              "This project is a prototype and is not medical advice.", ""]
    RESULT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[-9:]))


if __name__ == "__main__":
    main()
