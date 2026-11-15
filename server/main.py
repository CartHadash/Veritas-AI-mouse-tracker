"""
main.py - step 10: the local web server that ties everything together.

It runs on the user's own laptop, keeps both models loaded, and talks to the interface
(the web page in web/) in the browser.

Start it from the repository folder (same command on macOS and Windows):
    python -m uvicorn server.main:app
then open http://127.0.0.1:8000 . It only listens on this computer (127.0.0.1), never on
the network.

What it offers:
  /                  the interface files from web/ (when that folder exists)
  /ws/cursor         WebSocket (a connection that stays open so messages flow both ways
                     quickly). The page sends {"t", "x", "y"} for every pointer sample; the
                     server replies with the corrected position, the detector's tremor score,
                     and the estimated size and frequency. The page can also send
                     {"type": "click", "hit": true/false} and {"type": "reset"}.
                     Calibration test (Godson's idea): {"type": "calibrate_start"}, then
                     samples carrying "dot_x"/"dot_y", then {"type": "calibrate_end"}; the
                     server tries every filter in CANDIDATES on the recorded test and replies
                     {"type": "calibration", ...} with each one's distance from the dot. It
                     does not switch the filter (see calibration_val.md). Kept in memory only.
                     {"type": "calibrate_cancel"} drops the test.
  GET  /api/summary  the session summary, exactly as Contract 2 in docs/PROJECT_PLAN.md
  GET  /api/settings and POST /api/settings: filter mode, strength, demo tremor, tracking
  GET  /api/status   which optional parts (leader's tracker and assistant) are loaded

The leader's modules are optional: if `tracker` or `assistant` is missing or fails to
import (for example the tracker on Windows), the server carries on without it and says so
in /api/status.

This project is a prototype and is not medical advice.
"""

import asyncio
import json
import math
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

import numpy as np
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from baselines.classical_filters import OneEuroFilter  # noqa: E402
from models.corrector.live import RESPONSE_LEVELS, LiveCorrector, load_corrector  # noqa: E402
from models.detector.predict import THRESHOLD_FILE, VERSION, Detector, LiveDetector  # noqa: E402

RATE = 100
MODES = ["none", "low_sensitivity", "one_euro", "learned"]
DEMO_TREMOR_FILE = ROOT / "server" / "demo_tremor.npz"
DEMO_NOTE = "Tremor replay (demo mode) was ON for part of this session."

app = FastAPI(title="Tremor-aware pointer assistant (prototype, not medical advice)")


def is_local(host_header, origin_header):
    """Only this computer's own pages may talk to the server. Blocks other websites the user
    visits (their Origin is not local) and 'DNS rebinding' tricks (their Host is not local)."""
    host = (host_header or "").rsplit(":", 1)[0].strip("[]")
    if host not in LOCAL_HOSTS:
        return False
    return origin_header is None or urlsplit(origin_header).hostname in LOCAL_HOSTS


@app.middleware("http")
async def only_local_pages(request: Request, call_next):
    if not is_local(request.headers.get("host"), request.headers.get("origin")):
        return JSONResponse({"error": "only pages served by this computer may use this server"}, status_code=403)
    response = await call_next(request)
    # "no-cache" = the browser must ask the server whether a file changed before reusing its
    # copy. Without it, a browser kept running an old app.js after `git pull` (Sun 15 Nov).
    response.headers.setdefault("Cache-Control", "no-cache")
    return response

# ---------------------------------------------------------------- shared state

# Demo tremor starts at "strong": with medium tremor the correction is hard to see by eye
# (Oleksandr's hand check, Sat 14 Nov; evaluation/results/demo_modes_test.md, medium, reaching).
# response: how quickly "Our model" follows a moving hand (steadiest / balanced / responsive,
# models/corrector/live.py RESPONSE_LEVELS). Starts at the steadiest (team's choice, Sun 15 Nov).
# systemwide: "Steady cursor everywhere" (the real cursor, in every app; systemwide/service.py).
# systemwide_demo: also add the replayed tremor to the real cursor (for showing it on video).
settings = {"mode": "learned", "strength": 1.0, "demo_tremor": False, "demo_level": "strong",
            "response": "steadiest", "tracking": False, "systemwide": False, "systemwide_demo": False}
# Whether "Our model" adds gated One Euro smoothing (option A). Not a user setting: evaluations
# switch it off to measure the network alone (evaluation/vs_one_euro.py). Evaluations may also
# put fixed One Euro settings under "settings"; those then win over the page's choice.
SMOOTH_OUTPUT = {"on": True}
DEMO_LEVELS = ["mild", "medium", "strong"]
# The filters the calibration test tries on the user's own movement: (mode, strength).
CANDIDATES = [("none", 1.0), ("one_euro", 1.0), ("learned", 0.5), ("learned", 1.0)]
CANDIDATE_NAMES = ["No filter", "One Euro", "Our model (half strength)", "Our model"]
status = {}
LOCAL_HOSTS = {"127.0.0.1", "localhost"}

# The models are loaded once and shared (they are only read, never changed).
DETECTOR = Detector()
CORRECTOR_MODEL = load_corrector()
with open(THRESHOLD_FILE, encoding="utf-8") as f:
    _detector_info = json.load(f)


# ---------------------------------------------------------------- session statistics

class SessionStats:
    """Collects what the summary needs. Thread-safe: the tracker calls it from its own thread."""

    def __init__(self):
        self.lock = threading.Lock()
        self.started = datetime.now()
        self.start_clock = time.time()
        self.active_seconds = 0.0
        self.distance_px = 0.0
        self.clicks = 0
        self.hits = 0
        self.results = []             # (minute, tremor, size_px, frequency_hz) per detector update
        self.last = None              # (t, x, y) of the previous sample
        self.last_result = None
        self.demo_used = False

    def add_sample(self, t, x, y, result):
        with self.lock:
            if self.last is not None:
                dt = t - self.last[0]
                step = float(np.hypot(x - self.last[1], y - self.last[2]))
                self.distance_px += step
                if 0 < dt < 0.5 and step > 0:        # moved since the last sample: active time
                    self.active_seconds += dt
            self.last = (t, x, y)
            # Record each NEW detector result once (the detector updates every 0.1 s).
            if result is not None and result is not self.last_result:
                minute = int((time.time() - self.start_clock) // 60)
                self.results.append((minute, bool(result["tremor"]), result["size_px"], result["frequency_hz"]))
                self.last_result = result

    def add_click(self, hit):
        with self.lock:
            self.clicks += 1
            self.hits += int(bool(hit))

    def summary(self):
        """Contract 2 (docs/PROJECT_PLAN.md)."""
        with self.lock:
            results = list(self.results)
            minutes = self.active_seconds / 60
        tremor = np.array([r[1] for r in results], bool)
        sizes = np.array([r[2] for r in results], float)
        freqs = np.array([r[3] for r in results], float)
        # Per minute. Results are stored in time order, so each minute is one run of rows:
        # find where each run starts instead of searching the whole list once per minute
        # (that took half a second after a two-hour session).
        minutes_of = np.array([r[0] for r in results], int)
        starts = np.flatnonzero(np.diff(minutes_of, prepend=-1)) if len(results) else []
        ends = list(starts[1:]) + [len(results)]
        by_time = [{"minute": int(minutes_of[a]), "detected_share": round(float(tremor[a:b].mean()), 3),
                    "strength_px": round(float(np.median(sizes[a:b])), 2)} for a, b in zip(starts, ends)]
        # Steadiness: 1 = no shaking, 0 = typical shaking of 10 px or more (simple, explainable).
        steadiness = None if len(sizes) == 0 else round(float(np.clip(1 - np.median(sizes) / 10, 0, 1)), 3)
        notes = [DEMO_NOTE] if self.demo_used else []
        if len(results) == 0:
            notes.append("No movement analysed yet.")
        return {
            "session": {"started": self.started.isoformat(timespec="seconds"),
                        "minutes_active": round(minutes, 2)},
            "tremor": {
                "detected_share": None if len(tremor) == 0 else round(float(tremor.mean()), 3),
                "typical_frequency_hz": None if not tremor.any() else round(float(np.median(freqs[tremor])), 2),
                "typical_strength_px": None if not tremor.any() else round(float(np.median(sizes[tremor])), 2),
                "by_time": by_time},
            "usage": {"distance_px": round(self.distance_px), "clicks_in_app": self.clicks,
                      "click_accuracy": None if self.clicks == 0 else round(self.hits / self.clicks, 3),
                      "steadiness_score": steadiness},
            "filter": {"mode": settings["mode"], "strength": settings["strength"],
                       "response": settings["response"]},   # leader's request, Sun 15 Nov
            "model_info": {"detector_version": VERSION,
                           "missed_cases_rate": _detector_info.get("test_missed_cases_rate"),
                           "false_alarm_rate": _detector_info.get("test_false_alarm_rate")},
            "notes": notes,
        }


demo_stats = SessionStats()      # movement from the demo page
laptop_stats = SessionStats()    # whole-laptop movement from the leader's tracker (if running)


# ---------------------------------------------------------------- demo tremor and filters

class DemoTremor:
    """Replays recorded tremor of TEST people (server/demo_tremor.npz) on top of live movement."""

    def __init__(self, level="medium"):
        data = np.load(DEMO_TREMOR_FILE)
        keep = data["level"] == level          # only the recordings of the chosen strength
        self.segments = data["xy"][keep]
        self.info = [{"subject": str(s), "condition": str(c), "strength_px": round(float(p), 1), "level": level}
                     for s, c, p in zip(data["subject"][keep], data["condition"][keep], data["strength_px"][keep])]
        self.start_t = None

    def offset(self, t):
        """The recorded tremor at time t, blended between the two nearest recorded samples.
        (Taking int(...) of the position used to repeat or skip about 7% of samples because of
        rounding, and at browser rates made a staircase: both put fake jerks into the demo.)"""
        if self.start_t is None:
            self.start_t = t
        position = (t - self.start_t) * RATE
        i = int(math.floor(position + 1e-6))                 # whole sample, robust to rounding
        share = min(max(position - i, 0.0), 1.0)
        n = self.segments.shape[1]

        def sample(k):                                        # next recording every 10.24 s
            return self.segments[(k // n) % len(self.segments), k % n]
        a, b = sample(i), sample(i + 1)
        dx, dy = a + share * (b - a)
        return float(dx), float(dy), self.info[(i // n) % len(self.segments)]


class LowSensitivity:
    """
    The cursor moves half as far as the hand (a baseline from step 6). It adds up the hand's
    movements step by step (times 0.5) and stays inside the practice area, so every part of
    the area can still be reached, just with more hand travel. After a pause or when the
    pointer comes back into the area, it does not jump.
    """

    def __init__(self, gain=0.5, area=None):
        self.gain = gain
        self.area = area              # (width, height) of the practice area in px, if known
        self.reset()

    def reset(self):
        self.prev = None
        self.out = None

    def update(self, x, y, t):
        if self.out is None:
            self.out = [x, y]
        elif t - self.prev[0] < 0.1:              # a normal step (not a pause or a re-entry)
            self.out[0] += self.gain * (x - self.prev[1])
            self.out[1] += self.gain * (y - self.prev[2])
            if self.area is not None:
                self.out[0] = min(max(self.out[0], 0.0), self.area[0])
                self.out[1] = min(max(self.out[1], 0.0), self.area[1])
        self.prev = (t, x, y)
        return self.out[0], self.out[1]


class CursorSession:
    """One open demo page: its filter, its detector and its demo tremor.

    fixed: None (normal use) follows the shared settings. A settings dict instead gives a
    session of its own for replaying recorded samples (the calibration test); it runs the
    detector in line and never touches the live settings."""

    def __init__(self, stats, fixed=None):
        self.stats = stats
        self.fixed = fixed
        self.detector = LiveDetector(DETECTOR, background=fixed is None)
        self.demo = None
        self.area = None
        self.calibration = None       # while a calibration test runs: [(t, x, y, dot_x, dot_y)]
        self.build()

    def conf(self):
        return settings if self.fixed is None else self.fixed

    def build(self):
        """(Re)create the filter. Only needed when the mode or the demo level changes, so
        moving the strength slider does not throw away the detector's 2.56 s of history."""
        conf = self.conf()
        self.key = (conf["mode"], conf["demo_level"])
        self.mode = conf["mode"]
        self.strength = float(conf["strength"])
        if self.demo is None or self.demo.info[0]["level"] != conf["demo_level"]:
            self.demo = DemoTremor(conf["demo_level"])
        self.detector.reset()
        if self.mode == "learned":
            self.response = conf.get("response", "steadiest")
            self.filter = LiveCorrector(live_detector=self.detector, strength=self.strength, model=CORRECTOR_MODEL,
                                        smooth_output=SMOOTH_OUTPUT["on"], smoothing=self.smoothing())
        elif self.mode == "one_euro":
            self.filter = OneEuroFilter()
        elif self.mode == "low_sensitivity":
            self.filter = LowSensitivity(area=self.area)
        else:
            self.filter = None
        if self.filter is not None:
            self.filter.reset()

    def smoothing(self):
        """One Euro settings for "Our model": an evaluation's fixed ones, else the page's choice."""
        return SMOOTH_OUTPUT.get("settings") or RESPONSE_LEVELS[self.response]

    def set_area(self, width, height):
        self.area = (width, height)
        if isinstance(self.filter, LowSensitivity):
            self.filter.area = self.area

    def update(self, t, x, y, dot=None):
        conf = self.conf()
        if self.key != (conf["mode"], conf["demo_level"]):
            self.build()
        self.strength = float(conf["strength"])          # strength changes apply immediately
        if self.mode == "learned":
            self.filter.strength = self.strength
            if conf.get("response", "steadiest") != self.response:   # responsiveness: applies at once
                self.response = conf.get("response", "steadiest")
                self.filter.set_smoothing(self.smoothing())
        demo_info = None
        if conf["demo_tremor"]:
            dx, dy, demo_info = self.demo.offset(t)
            x, y = x + dx, y + dy
            self.stats.demo_used = True
        if self.calibration is not None and dot is not None:
            self.calibration.append((t, x, y, dot[0], dot[1]))   # what the hand did (+ demo tremor)

        if self.mode == "learned":
            cx, cy = self.filter.update(x, y, t)            # also feeds the detector
            result, gate = self.detector.result, self.filter.gate
        else:
            result = self.detector.update(x, y, t)
            gate = None
            if self.filter is None:
                cx, cy = x, y
            else:
                fx, fy = self.filter.update(x, y, t)
                cx, cy = x + self.strength * (fx - x), y + self.strength * (fy - y)
        self.stats.add_sample(t, x, y, result)
        return {"t": t, "raw_x": x, "raw_y": y, "x": cx, "y": cy, "mode": self.mode, "gate": gate,
                "score": None if result is None else round(result["score"], 3),
                "tremor": None if result is None else bool(result["tremor"]),
                "size_px": None if result is None else round(result["size_px"], 2),
                "frequency_hz": None if result is None else round(result["frequency_hz"], 2),
                "demo": demo_info}


# ---------------------------------------------------------------- calibration test (Godson's idea)

CALIBRATION_SKIP = 2.56       # s; score after the detector's first full window (as the evaluations do)
CALIBRATION_MIN_SECONDS = 8.0  # a shorter test (pointer left the area, ...) is not scored


def replay(mode, strength, samples):
    """Run recorded samples [(t, x, y), ...] through a fresh session with one filter, in line.
    Returns the server's replies (shown cursor, detector result) for every sample."""
    session = CursorSession(SessionStats(), fixed={"mode": mode, "strength": strength,
                                                   "demo_tremor": False, "demo_level": settings["demo_level"],
                                                   "response": settings["response"]})
    return [session.update(t, x, y) for t, x, y in samples]


def score_calibration(record):
    """
    record: [(t, x, y, dot_x, dot_y), ...] from the calibration test (x, y include demo tremor).
    Tries every filter in CANDIDATES on it and returns each one's distance from the dot, the
    closest one, and what was measured. Kept in memory only (decision L1).
    """
    rows = np.array(record, float)
    t, xy, dot = rows[:, 0], rows[:, 1:3], rows[:, 3:5]
    seconds = float(t[-1] - t[0])
    if seconds < CALIBRATION_MIN_SECONDS:
        return {"ok": False, "message": "The test was too short (%.1f s). Keep the pointer in the area "
                "until the dot stops." % seconds}
    keep = t - t[0] >= CALIBRATION_SKIP
    distances, results = [], None
    for mode, strength in CANDIDATES:
        replies = replay(mode, strength, list(zip(t, xy[:, 0], xy[:, 1])))
        shown = np.array([[r["x"], r["y"]] for r in replies])
        distances.append(float(np.linalg.norm(shown[keep] - dot[keep], axis=1).mean()))
        if (mode, strength) == ("learned", 1.0):
            results = [r for r, k in zip(replies, keep) if k and r["score"] is not None]
    best = int(np.argmin(distances))
    return {
        "ok": True,
        "chosen": CANDIDATE_NAMES[best], "mode": CANDIDATES[best][0], "strength": CANDIDATES[best][1],
        "distances": [{"name": n, "px": round(d, 2)} for n, d in zip(CANDIDATE_NAMES, distances)],
        "samples_per_second": round(len(t) / seconds, 1),
        "tremor_share": None if not results else round(float(np.mean([r["tremor"] for r in results])), 2),
        "size_px": None if not results else round(float(np.median([r["size_px"] for r in results])), 2),
        "frequency_hz": None if not results else round(float(np.median([r["frequency_hz"] for r in results])), 2),
    }


# ---------------------------------------------------------------- leader's optional modules

def load_tracker():
    """Contract 1: tracker.start(callback) / tracker.stop(). Optional."""
    try:
        try:
            from tracker import reader as tracker_module
        except ImportError:
            import tracker as tracker_module
        if not hasattr(tracker_module, "start"):
            raise ImportError("tracker has no start(callback)")
        status["tracker"] = "available (off until switched on)"
        return tracker_module
    except Exception as error:     # missing, or cannot load on this system (e.g. Windows)
        status["tracker"] = "not available: %s" % error
        return None


tracker = load_tracker()
laptop_detector = LiveDetector(DETECTOR)
_last_tracker_t = [None]
TRACKER_GAP_SECONDS = 1.0    # the tracker goes quiet after 3 s of a still pointer


def tracker_callback(sample):
    """Called by the tracker (on its own thread) for every whole-laptop pointer sample."""
    # After a pause (no samples for over a second), start the detector afresh so it does not
    # treat the gap as the pointer sitting perfectly still.
    if _last_tracker_t[0] is not None and sample["t"] - _last_tracker_t[0] > TRACKER_GAP_SECONDS:
        laptop_detector.reset()
    _last_tracker_t[0] = sample["t"]
    result = laptop_detector.update(sample["x"], sample["y"], sample["t"])
    laptop_stats.add_sample(sample["t"], sample["x"], sample["y"], result)


def set_tracking(on):
    if tracker is None:
        settings["tracking"] = False
        return
    try:
        if on and not settings["tracking"]:
            laptop_detector.reset()
            tracker.start(tracker_callback)
            status["tracker"] = "running"
        elif not on and settings["tracking"]:
            tracker.stop()
            status["tracker"] = "available (switched off)"
        settings["tracking"] = bool(on)
    except Exception as error:
        settings["tracking"] = False
        status["tracker"] = "failed to start: %s" % error


try:
    from assistant import router as assistant_router  # noqa: E402
    app.include_router(assistant_router)
    status["assistant"] = "available"
except Exception as error:
    try:
        from assistant.api import router as assistant_router  # noqa: E402
        app.include_router(assistant_router)
        status["assistant"] = "available"
    except Exception:
        status["assistant"] = "not available: %s" % error


# ---------------------------------------------------------------- steady cursor everywhere (B3)

def _systemwide_stopped():
    """Called when the system-wide correction stops for any reason (the switch, Control +
    Option + X, an error), so the page's switch always shows the truth."""
    settings["systemwide"] = False


try:
    from systemwide.service import SystemwideService, config_from
    systemwide = SystemwideService(models=(DETECTOR, CORRECTOR_MODEL), on_stopped=_systemwide_stopped)
except Exception as error:         # the folder is missing or cannot load: the app works without it
    systemwide = None
    status["systemwide"] = "not available: %s" % error


def systemwide_status():
    if systemwide is None:
        return status.get("systemwide", "not available")
    if systemwide.is_on():
        return "on"
    ok, why = systemwide.available()
    return "available" if ok else "not available: %s" % why


def set_systemwide(on):
    if systemwide is None:
        settings["systemwide"] = False
    elif on:
        settings["systemwide"] = systemwide.start(config_from(settings))
    else:
        systemwide.stop()
        settings["systemwide"] = False


@app.on_event("shutdown")
def stop_systemwide():
    """Stopping the server always gives the cursor back."""
    if systemwide is not None:
        systemwide.stop()


# ---------------------------------------------------------------- routes

DEMO_SEGMENT_COUNT = len(np.load(DEMO_TREMOR_FILE)["xy"])


@app.get("/api/status")
def get_status():
    return {**status, "systemwide": systemwide_status(), "demo_tremor_segments": DEMO_SEGMENT_COUNT,
            "detector_threshold": round(DETECTOR.threshold, 3),
            "disclaimer": "This project is a prototype and is not medical advice."}


@app.get("/api/settings")
def get_settings():
    return settings


@app.post("/api/settings")
def post_settings(new: dict):
    """Change any of: mode (none / low_sensitivity / one_euro / learned), strength (0-1),
    demo_tremor (true/false), demo_level (mild / medium / strong), response (steadiest /
    balanced / responsive), tracking (true/false), systemwide (true/false: steady cursor
    everywhere), systemwide_demo (true/false: add replayed tremor to the real cursor).
    Everything is checked first; if anything is invalid, nothing is changed."""
    if "mode" in new and new["mode"] not in MODES:
        return JSONResponse({"error": "mode must be one of %s" % MODES}, status_code=400)
    if "response" in new and new["response"] not in RESPONSE_LEVELS:
        return JSONResponse({"error": "response must be one of %s" % list(RESPONSE_LEVELS)}, status_code=400)
    if "demo_level" in new and new["demo_level"] not in DEMO_LEVELS:
        return JSONResponse({"error": "demo_level must be one of %s" % DEMO_LEVELS}, status_code=400)
    if "strength" in new:
        try:
            strength = float(new["strength"])
        except (TypeError, ValueError):
            strength = float("nan")
        if not math.isfinite(strength):
            return JSONResponse({"error": "strength must be a number from 0 to 1"}, status_code=400)
    for key in ("mode", "demo_level", "response"):
        if key in new:
            settings[key] = new[key]
    if "strength" in new:
        settings["strength"] = float(np.clip(strength, 0.0, 1.0))
    if "demo_tremor" in new:
        settings["demo_tremor"] = bool(new["demo_tremor"])
    if "tracking" in new:
        set_tracking(bool(new["tracking"]))
    if "systemwide_demo" in new:
        settings["systemwide_demo"] = bool(new["systemwide_demo"])
    if "systemwide" in new:
        set_systemwide(bool(new["systemwide"]))
    if systemwide is not None and systemwide.is_on():
        systemwide.update(config_from(settings))      # filter, strength, level changes apply at once
    return settings


@app.get("/api/summary")
def get_summary():
    summary = demo_stats.summary()
    if laptop_stats.results:
        whole = laptop_stats.summary()
        summary["whole_laptop"] = {"session": whole["session"], "tremor": whole["tremor"],
                                   "usage": {"distance_px": whole["usage"]["distance_px"],
                                             "steadiness_score": whole["usage"]["steadiness_score"]}}
        summary["notes"].append("whole_laptop: movement across the whole laptop from the tracker.")
    return summary


@app.post("/api/reset")
def reset_summary():
    """Start a new session summary (the demo page's 'new session' button)."""
    global demo_stats
    try:                       # keep the last minute before "New session" (leader's history)
        from assistant import history
        history.save(get_summary())
    except Exception:          # no assistant, or saving failed: never block a new session
        pass
    demo_stats = SessionStats()
    return {"ok": True}


def read_sample(message):
    """(t, x, y) as finite numbers, or None if the message is not a valid sample."""
    try:
        values = tuple(float(message[k]) for k in ("t", "x", "y"))
    except (KeyError, TypeError, ValueError):
        return None
    return values if all(math.isfinite(v) for v in values) else None


def read_dot(message):
    """The calibration dot's position sent with a sample during the test, or None."""
    try:
        dot = (float(message["dot_x"]), float(message["dot_y"]))
    except (KeyError, TypeError, ValueError):
        return None
    return dot if all(math.isfinite(v) for v in dot) else None


@app.websocket("/ws/cursor")
async def cursor_socket(websocket: WebSocket):
    if not is_local(websocket.headers.get("host"), websocket.headers.get("origin")):
        await websocket.close(code=1008)                 # another website: refuse
        return
    await websocket.accept()
    with demo_stats.lock:
        demo_stats.last = None                           # a new page: do not join its path to the old one
    session = CursorSession(demo_stats)
    try:
        while True:
            message = await websocket.receive_json()
            if not isinstance(message, dict):
                continue
            if session.stats is not demo_stats:          # the summary was reset
                session.stats = demo_stats
            kind = message.get("type", "sample")
            if kind == "click":
                demo_stats.add_click(message.get("hit", False))
            elif kind == "reset":
                session.build()
            elif kind == "calibrate_start":
                session.calibration = []
            elif kind == "calibrate_cancel":
                session.calibration = None
            elif kind == "calibrate_end":
                record, session.calibration = session.calibration or [], None
                if len(record) < 2:
                    outcome = {"ok": False, "message": "No movement was recorded during the test."}
                else:
                    # A few seconds of work: on a worker thread, so the server stays responsive.
                    outcome = await asyncio.to_thread(score_calibration, record)
                # The filter is NOT switched to the closest one: on validation people, choosing
                # it from one 10 s test did worse than always using our model
                # (evaluation/results/calibration_val.md). The test only reports.
                await websocket.send_json({"type": "calibration", **outcome})
            elif kind == "area":
                try:
                    session.set_area(float(message["width"]), float(message["height"]))
                except (KeyError, TypeError, ValueError):
                    pass
            else:
                sample = read_sample(message)
                if sample is None:
                    continue                             # skip a broken message, keep the connection
                await websocket.send_json(session.update(*sample, dot=read_dot(message)))
    except WebSocketDisconnect:
        pass
    finally:
        if session.detector.pool is not None:
            session.detector.pool.shutdown(wait=False)


# The interface files. Mounted last so the /api and /ws routes above take priority.
WEB = ROOT / "web"
if WEB.exists():
    app.mount("/", StaticFiles(directory=WEB, html=True), name="web")
else:
    @app.get("/")
    def no_interface_yet():
        return {"message": "Server is running. The interface (web/) is not built yet.",
                "disclaimer": "This project is a prototype and is not medical advice."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
