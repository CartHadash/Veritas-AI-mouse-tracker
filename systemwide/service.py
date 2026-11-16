"""
service.py - "Steady cursor everywhere" as a switch: runs the system-wide correction (B3) in the
background of our server until it is switched off.

The terminal test mode (systemwide/run.py) stops by itself after a set time. This mode has no
time limit, so its safety rules matter even more:
  - Control + Option + X switches it off at once, from any app;
  - switching the page's switch off, or stopping the server, switches it off;
  - if the filter fails, the cursor follows the hand (systemwide/steady.py);
  - the macOS permission is only CHECKED, never requested: only a human may grant it.

The macOS part is the "backend" (QuartzBackend below, which uses run.py's event tap). The
logic around it (start, stop, pass the page's settings on) does not need macOS, so the tests
use a stand-in backend (systemwide/test_steady.py).
"""

import sys
import threading
import time

from systemwide.steady import MODES, SteadyCursor

PERMISSION_HINT = ("needs a permission only a human can give: System Settings -> Privacy & Security -> "
                   "Accessibility (and Input Monitoring) -> switch on the terminal app that runs the server "
                   "-> quit and reopen it")


class QuartzBackend:
    """The real thing: macOS's event tap (systemwide/run.py)."""

    def _quartz(self):
        import Quartz
        return Quartz

    def available(self):
        """(True, "") or (False, why not). Only checks; never asks macOS for anything."""
        if sys.platform != "darwin":
            return False, "works on macOS only"
        try:
            from systemwide.run import permission_ok
            if not permission_ok(self._quartz()):
                return False, PERMISSION_HINT
        except Exception as error:
            return False, "could not be loaded: %s" % error
        return True, ""

    def cursor(self):
        Q = self._quartz()
        here = Q.CGEventGetLocation(Q.CGEventCreate(None))
        return (here.x, here.y)

    def bounds(self):
        from systemwide.run import screen_bounds
        return screen_bounds(self._quartz())

    def run(self, state, on_idle):
        """Blocks until state["stop"] (also set by Control + Option + X)."""
        from systemwide.run import run_tap
        run_tap(self._quartz(), state, on_idle=on_idle)


def config_from(settings):
    """The page's settings -> what the system-wide corrector needs. "Lower sensitivity" only
    exists inside the practice area, so it falls back to our model."""
    mode = settings.get("mode")
    return {"mode": mode if mode in MODES else "learned",
            "strength": float(settings.get("strength", 1.0)),
            "response": settings.get("response", "steadiest"),
            "demo_level": settings.get("demo_level") if settings.get("systemwide_demo") else None}


class SystemwideService:
    def __init__(self, backend=None, models=None, on_stopped=None):
        """models: (detector, corrector network) already loaded by the server, so switching on
        is quick. on_stopped(): called when it stops for any reason (switch, off-key, error)."""
        self.backend = backend or QuartzBackend()
        self.models = models or (None, None)
        self.on_stopped = on_stopped
        self.thread = None
        self.state = None
        self.config = None          # what is running
        self.wanted = None          # what the page asked for last
        self.error = None

    def available(self):
        return self.backend.available()

    def is_on(self):
        return self.thread is not None and self.thread.is_alive()

    def build(self, config, start):
        return SteadyCursor(start, self.backend.bounds(), mode=config["mode"], demo_level=config["demo_level"],
                            strength=config["strength"], response=config["response"],
                            detector_model=self.models[0], corrector_model=self.models[1])

    def start(self, config):
        """Switch on. Returns True if it is running afterwards."""
        if self.is_on():
            self.update(config)
            return True
        ok, why = self.available()
        if not ok:
            self.error = why
            return False
        self.error = None
        self.config = self.wanted = dict(config)
        self.state = {"stop": False, "steady": self.build(config, self.backend.cursor())}
        self.thread = threading.Thread(target=self._run, args=(self.state,), daemon=True)
        self.thread.start()
        return True

    def update(self, config):
        """The page's settings changed: applied by the running loop within about 10 ms."""
        self.wanted = dict(config)

    def stop(self):
        """Switch off and wait (briefly) until the cursor is back to normal."""
        thread = self.thread
        if self.state is not None:
            self.state["stop"] = True
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=3.0)

    def _on_idle(self, state, now):
        wanted = self.wanted
        if wanted == self.config:
            return
        steady = state["steady"]
        if wanted["mode"] != self.config["mode"] or wanted["demo_level"] != self.config["demo_level"]:
            state["steady"] = self.build(wanted, steady.shown)     # another filter: start it where the cursor is
            steady.stop()
        elif steady.mode == "learned":
            steady.filter.strength = wanted["strength"]            # these two apply without a restart
            steady.filter.set_smoothing(self._smoothing(wanted["response"]))
        self.config = wanted

    @staticmethod
    def _smoothing(response):
        from models.corrector.live import RESPONSE_LEVELS
        return RESPONSE_LEVELS[response]

    def _run(self, state):
        try:
            self.backend.run(state, self._on_idle)
        except Exception as error:                 # e.g. macOS refused the tap: say why, change nothing
            self.error = str(error)
        finally:
            state["stop"] = True
            try:
                state["steady"].stop()
            finally:
                if self.on_stopped is not None:
                    self.on_stopped()


class FakeBackend:
    """A stand-in for macOS in tests: no real cursor, the same start/stop behaviour."""

    def __init__(self, ok=True, why=""):
        self.ok, self.why = ok, why
        self.state = None

    def available(self):
        return self.ok, self.why

    def cursor(self):
        return (700.0, 450.0)

    def bounds(self):
        return (0, 0, 1440, 900)

    def run(self, state, on_idle):
        self.state = state
        while not state["stop"]:
            on_idle(state, time.monotonic())
            time.sleep(0.002)

    def press_off_key(self):
        """What Control + Option + X does in the real backend."""
        self.state["stop"] = True
