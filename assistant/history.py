"""Session history.

Saves a copy of each session's SUMMARY NUMBERS to local_logs/sessions/, one small JSON
file per session, named after the session's start time. Never raw pointer movement.
The folder is ignored by git, stays on this laptop, and "Delete my saved pointer data"
empties it (tracker.log.delete_all_logs).

    save(summary)          store or update this session's file (only once something was analysed)
    past_sessions(...)     short versions of earlier sessions, newest first, for the assistant
    start_autosave(get)    every minute, save whatever get() returns (the live summary)
"""

import json
import threading
from datetime import datetime
from pathlib import Path

from tracker.log import LOG_DIR

SESSIONS_DIR = LOG_DIR / "sessions"
AUTOSAVE_SECONDS = 60
MAX_PAST = 7                      # how many earlier sessions the assistant sees

_do_not_save = set()              # sessions the user deleted: never save them again


def _file_for(started):
    # "2026-11-15T10:02:00" -> "session_2026-11-15_10-02-00.json" (safe on Windows too)
    return SESSIONS_DIR / ("session_%s.json" % started.replace("T", "_").replace(":", "-"))


def save(summary):
    """Save this session's summary. Returns True if saved (skipped while nothing was analysed)."""
    started = summary.get("session", {}).get("started")
    if not started or started in _do_not_save or summary.get("tremor", {}).get("detected_share") is None:
        return False
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    path = _file_for(started)
    temporary = path.with_suffix(".%d.tmp" % threading.get_ident())   # one per thread: no clashes
    temporary.write_text(json.dumps(summary, indent=1, sort_keys=True), encoding="utf-8")
    temporary.replace(path)        # all-or-nothing: never a half-written file
    return True


def do_not_save(started):
    """After "delete my data": keep the current session out of the saved history."""
    _do_not_save.add(started)


def short_version(summary):
    """The few numbers the assistant needs about a past session."""
    started = summary["session"]["started"]
    tremor, usage = summary.get("tremor", {}), summary.get("usage", {})
    notes = summary.get("notes", [])
    return {
        "day": datetime.fromisoformat(started).strftime("%a %d %b, %H:%M"),
        "started": started,
        "minutes_active": summary["session"].get("minutes_active"),
        "detected_share": tremor.get("detected_share"),
        "typical_frequency_hz": tremor.get("typical_frequency_hz"),
        "typical_strength_px": tremor.get("typical_strength_px"),
        "steadiness_score": usage.get("steadiness_score"),
        "click_accuracy": usage.get("click_accuracy"),
        "filter": summary.get("filter"),
        "demo_tremor_was_on": any("demo" in note.lower() or "replay" in note.lower() for note in notes),
    }


def past_sessions(exclude_started=None, folder=None, limit=MAX_PAST):
    """Short versions of saved sessions, newest first, leaving out the current one."""
    folder = Path(folder) if folder else SESSIONS_DIR
    if not folder.exists():
        return []
    sessions = []
    for path in sorted(folder.glob("session_*.json"), reverse=True):
        try:
            summary = json.loads(path.read_text(encoding="utf-8"))
            if summary["session"]["started"] != exclude_started:
                sessions.append(short_version(summary))
        except (ValueError, KeyError, TypeError):
            continue               # a damaged file is skipped, never a crash
        if len(sessions) >= limit:
            break
    return sessions


_autosave_thread = None


def start_autosave(get_summary):
    """Save the live summary every minute in the background (started once, by assistant.api)."""
    global _autosave_thread
    if _autosave_thread is not None:
        return
    stop = threading.Event()

    def loop():
        while not stop.wait(AUTOSAVE_SECONDS):
            try:
                save(get_summary())
            except Exception:      # saving history must never break the app
                pass

    _autosave_thread = threading.Thread(target=loop, name="history-autosave", daemon=True)
    _autosave_thread.start()
