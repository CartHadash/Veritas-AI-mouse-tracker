"""The assistant's web routes (Contract 3). The builder's server includes `router` with one line.

    POST /api/assistant/chat       {"messages": [{"role": "user", "content": "..."}]} -> streamed text
    GET  /api/assistant/explain    the two-or-three-sentence explanation, streamed text
    GET  /api/assistant/status     {"ai": true/false, "model": ..., "past_sessions": n, "disclaimer": ...}
    GET  /api/assistant/history    {"current_started": ..., "sessions": [short past sessions, newest first]}
    POST /api/assistant/delete-my-data   empties local_logs/ (tracker files and saved sessions)
"""

import json
import sys
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from assistant import core, history
from assistant.prompt import DISCLAIMER

CONTRACTS = Path(__file__).resolve().parent.parent / "docs" / "contracts"
EXAMPLE_SUMMARY = CONTRACTS / "summary_example.json"
EXAMPLE_HISTORY = CONTRACTS / "history_example.json"

router = APIRouter()


def live_server():
    """The builder's running server module, or None (standalone test page).

    Looked up at request time, not import time, because the server imports this module:
    importing it back here would be circular.
    """
    server = sys.modules.get("server.main")
    return server if server is not None and hasattr(server, "get_summary") else None


def current_summary():
    """The live summary from the builder's server if it is running, else the example file."""
    server = live_server()
    if server is not None:
        return server.get_summary()
    with open(EXAMPLE_SUMMARY, encoding="utf-8") as f:
        return json.load(f)


def summary_and_past():
    """This session's summary, plus short versions of earlier sessions (saved on this laptop)."""
    summary = current_summary()
    if live_server() is None:                          # standalone: invented example history
        with open(EXAMPLE_HISTORY, encoding="utf-8") as f:
            return summary, json.load(f)["sessions"]
    history.save(summary)                              # keep this session's file up to date
    return summary, history.past_sessions(exclude_started=summary["session"]["started"])


# Inside the real app, save the live summary every minute in the background.
if "server.main" in sys.modules:
    history.start_autosave(lambda: sys.modules["server.main"].get_summary())


def text_stream(pieces):
    return StreamingResponse(pieces, media_type="text/plain; charset=utf-8")


@router.post("/api/assistant/chat")
def chat(body: dict):
    messages = body.get("messages", []) if isinstance(body, dict) else []
    if not isinstance(messages, list):
        messages = []
    summary, past = summary_and_past()
    return text_stream(core.stream_reply(summary, messages, past))


@router.get("/api/assistant/explain")
def explain():
    summary, past = summary_and_past()
    messages = [{"role": "user", "content": core.EXPLAIN_REQUEST}]
    return text_stream(core.stream_reply(summary, messages, past))


@router.get("/api/assistant/status")
def assistant_status():
    _, past = summary_and_past()
    return {"ai": core.ai_available(), "model": core.MODEL, "past_sessions": len(past),
            "disclaimer": DISCLAIMER}


@router.get("/api/assistant/history")
def session_history():
    """For the summary page: earlier sessions saved on this laptop, newest first."""
    summary, past = summary_and_past()
    return {"current_started": summary["session"]["started"], "sessions": past}


@router.post("/api/assistant/delete-my-data")
def delete_my_data():
    """Delete everything in local_logs/: tracker files and saved session summaries.
    The current session's numbers in memory are cleared with 'New session'."""
    from tracker.log import delete_all_logs
    history.do_not_save(current_summary()["session"]["started"])   # or autosave would re-save it
    return {"deleted_files": delete_all_logs()}
