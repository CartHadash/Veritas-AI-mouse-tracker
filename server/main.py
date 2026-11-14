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
  GET  /api/summary  the session summary, exactly as Contract 2 in docs/PROJECT_PLAN.md
  GET  /api/settings and POST /api/settings: filter mode, strength, demo tremor, tracking
  GET  /api/status   which optional parts (leader's tracker and assistant) are loaded

The leader's modules are optional: if `tracker` or `assistant` is missing or fails to
import (for example the tracker on Windows), the server carries on without it and says so
in /api/status.

This project is a prototype and is not medical advice.
"""

import json
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from baselines.classical_filters import OneEuroFilter  # noqa: E402
from models.corrector.live import LiveCorrector, load_corrector  # noqa: E402
from models.detector.predict import THRESHOLD_FILE, VERSION, Detector, LiveDetector  # noqa: E402

RATE = 100
MODES = ["none", "low_sensitivity", "one_euro", "learned"]
DEMO_TREMOR_FILE = ROOT / "server" / "demo_tremor.npz"
DEMO_NOTE = "Tremor replay (demo mode) was ON for part of this session."

app = FastAPI(title="Tremor-aware pointer assistant (prototype, not medical advice)")

# ---------------------------------------------------------------- shared state

settings = {"mode": "learned", "strength": 1.0, "demo_tremor": False, "tracking": False}
settings_version = [0]          # bumped on every change, so open sessions rebuild their filter
status = {}

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
        by_time = []
        for minute in sorted({r[0] for r in results}):
            m = np.array([r[0] == minute for r in results])
            by_time.append({"minute": minute, "detected_share": round(float(tremor[m].mean()), 3),
                            "strength_px": round(float(np.median(sizes[m])), 2)})
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
            "filter": {"mode": settings["mode"], "strength": settings["strength"]},
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

    def __init__(self):
        data = np.load(DEMO_TREMOR_FILE)
        self.segments = data["xy"]
        self.info = [{"subject": str(s), "condition": str(c), "strength_px": round(float(p), 1)}
                     for s, c, p in zip(data["subject"], data["condition"], data["strength_px"])]
        self.start_t = None

    def offset(self, t):
        if self.start_t is None:
            self.start_t = t
        i = int((t - self.start_t) * RATE)
        segment = (i // self.segments.shape[1]) % len(self.segments)     # next recording every 10 s
        dx, dy = self.segments[segment, i % self.segments.shape[1]]
        return float(dx), float(dy), self.info[segment]


class LowSensitivity:
    """The cursor moves half as far as the hand (a baseline from step 6)."""

    def __init__(self, gain=0.5):
        self.gain = gain
        self.reset()

    def reset(self):
        self.anchor = None

    def update(self, x, y, t):
        if self.anchor is None:
            self.anchor = (x, y)
        return (self.anchor[0] + self.gain * (x - self.anchor[0]),
                self.anchor[1] + self.gain * (y - self.anchor[1]))


class CursorSession:
    """One open demo page: its filter, its detector and its demo tremor."""

    def __init__(self, stats):
        self.stats = stats
        self.detector = LiveDetector(DETECTOR)
        self.demo = DemoTremor()
        self.version = None
        self.build()

    def build(self):
        self.version = settings_version[0]
        self.mode = settings["mode"]
        self.strength = float(settings["strength"])
        self.detector.reset()
        if self.mode == "learned":
            self.filter = LiveCorrector(live_detector=self.detector, strength=self.strength, model=CORRECTOR_MODEL)
        elif self.mode == "one_euro":
            self.filter = OneEuroFilter()
        elif self.mode == "low_sensitivity":
            self.filter = LowSensitivity()
        else:
            self.filter = None
        if self.filter is not None:
            self.filter.reset()

    def update(self, t, x, y):
        if self.version != settings_version[0]:
            self.build()
        demo_info = None
        if settings["demo_tremor"]:
            dx, dy, demo_info = self.demo.offset(t)
            x, y = x + dx, y + dy
            self.stats.demo_used = True

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


# ---------------------------------------------------------------- routes

@app.get("/api/status")
def get_status():
    return {**status, "demo_tremor_segments": len(np.load(DEMO_TREMOR_FILE)["xy"]),
            "detector_threshold": round(DETECTOR.threshold, 3),
            "disclaimer": "This project is a prototype and is not medical advice."}


@app.get("/api/settings")
def get_settings():
    return settings


@app.post("/api/settings")
def post_settings(new: dict):
    """Change any of: mode (none / low_sensitivity / one_euro / learned), strength (0-1),
    demo_tremor (true/false), tracking (true/false)."""
    if "mode" in new:
        if new["mode"] not in MODES:
            return JSONResponse({"error": "mode must be one of %s" % MODES}, status_code=400)
        settings["mode"] = new["mode"]
    if "strength" in new:
        settings["strength"] = float(np.clip(float(new["strength"]), 0.0, 1.0))
    if "demo_tremor" in new:
        settings["demo_tremor"] = bool(new["demo_tremor"])
    if "tracking" in new:
        set_tracking(bool(new["tracking"]))
    settings_version[0] += 1
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
    demo_stats = SessionStats()
    return {"ok": True}


@app.websocket("/ws/cursor")
async def cursor_socket(websocket: WebSocket):
    await websocket.accept()
    session = CursorSession(demo_stats)
    try:
        while True:
            message = await websocket.receive_json()
            if session.stats is not demo_stats:          # the summary was reset
                session.stats = demo_stats
            kind = message.get("type", "sample")
            if kind == "click":
                demo_stats.add_click(message.get("hit", False))
            elif kind == "reset":
                session.build()
            else:
                reply = session.update(float(message["t"]), float(message["x"]), float(message["y"]))
                await websocket.send_json(reply)
    except WebSocketDisconnect:
        pass


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
