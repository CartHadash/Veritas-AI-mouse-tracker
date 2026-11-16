"""Reads where the pointer is, anywhere on the laptop, about 100 times a second.

What it offers:
    start(callback)  -> calls callback({"t": seconds, "x": points, "y": points}) per sample
    stop()

How it works, in plain words:
- A background thread wakes up every 10 ms and asks macOS "where is the pointer now?".
  Asking for the position needs NO special permission (listening to mouse events would
  need the Accessibility permission, so we deliberately do not do that).
- If the pointer has not moved for IDLE_SECONDS, we stop passing samples on until it moves
  again (the user is away or typing). This keeps the summary about real movement.
- It only READS the position. It never moves the cursor, and it records nothing else:
  no clicks, no keys, no window titles, no app names, no screenshots.

Only works on macOS. On other systems start() raises a clear error and the rest of the app
carries on without the tracker (server/main.py handles that).
"""

import sys
import threading
import time

RATE_HZ = 100                  # samples per second we aim for
IDLE_SECONDS = 3.0             # pointer still this long -> stop sending samples until it moves

_thread = None                 # the background thread while running, else None
_stop_event = threading.Event()


def read_position():
    """Ask macOS where the pointer is. Returns (x, y) in screen points (top-left is 0, 0)."""
    import Quartz  # imported here so that importing this file never fails on Windows
    point = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))
    return float(point.x), float(point.y)


def start(callback, save_log=False):
    """Start reading the pointer in the background and call callback(sample) for each sample.

    save_log=True also appends every sample to a file in local_logs/ (see tracker/log.py).
    By default nothing is written to disk (the session lives in memory).
    """
    global _thread
    if sys.platform != "darwin":
        raise RuntimeError("The whole-laptop tracker only works on macOS; "
                           "the rest of the app works without it.")
    if _thread is not None:
        raise RuntimeError("The tracker is already running; call stop() first.")
    read_position()            # fail now, with the real error, if Quartz is missing

    log = None
    if save_log:
        from tracker.log import SampleLog
        log = SampleLog()

    _stop_event.clear()
    _thread = threading.Thread(target=_run, args=(callback, log), name="pointer-tracker", daemon=True)
    _thread.start()


def stop():
    """Stop reading. Safe to call when the tracker is not running."""
    global _thread
    if _thread is None:
        return
    _stop_event.set()
    _thread.join(timeout=1.0)
    _thread = None


def is_running():
    return _thread is not None


def _run(callback, log):
    """The background loop: one sample every 1/RATE_HZ seconds until stop() is called."""
    period = 1.0 / RATE_HZ
    t0 = time.perf_counter()        # perf_counter: a precise clock that never jumps
    next_tick = t0
    last_xy = None
    last_move_time = t0
    callback_failed = False

    try:
        while not _stop_event.is_set():
            now = time.perf_counter()
            x, y = read_position()

            # Idle check: only pass samples on while the pointer has moved recently.
            if (x, y) != last_xy:
                last_move_time = now
                last_xy = (x, y)
            if now - last_move_time <= IDLE_SECONDS:
                sample = {"t": round(now - t0, 4), "x": x, "y": y}
                try:
                    callback(sample)
                except Exception as error:   # a bug in the receiver must not kill the tracker
                    if not callback_failed:
                        print("tracker: callback failed (shown once):", repr(error), file=sys.stderr)
                        callback_failed = True
                if log is not None:
                    log.write(sample)

            # Steady timer: aim at fixed tick times so small delays do not add up.
            next_tick += period
            wait = next_tick - time.perf_counter()
            if wait > 0:
                _stop_event.wait(wait)       # sleeps, but wakes at once if stop() is called
            elif wait < -0.1:                # fell far behind (laptop was busy): start afresh
                next_tick = time.perf_counter()
    finally:
        if log is not None:
            log.close()
