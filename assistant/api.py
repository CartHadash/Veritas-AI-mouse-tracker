"""The assistant's web routes (Contract 3). The builder's server includes `router` with one line.

    POST /api/assistant/chat       {"messages": [{"role": "user", "content": "..."}]} -> streamed text
    GET  /api/assistant/explain    the two-or-three-sentence explanation, streamed text
    GET  /api/assistant/status     {"ai": true/false, "model": ..., "disclaimer": ...}
    POST /api/assistant/delete-my-data   empties local_logs/ (the tracker's optional files)
"""

import json
import sys
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from assistant import core
from assistant.prompt import DISCLAIMER

EXAMPLE_SUMMARY = Path(__file__).resolve().parent.parent / "docs" / "contracts" / "summary_example.json"

router = APIRouter()


def current_summary():
    """The live summary from the builder's server if it is running, else the example file.

    We look the server up at request time (not import time) because the server imports
    this module: importing it back here would be circular.
    """
    server = sys.modules.get("server.main")
    if server is not None and hasattr(server, "get_summary"):
        return server.get_summary()
    with open(EXAMPLE_SUMMARY, encoding="utf-8") as f:
        return json.load(f)


def text_stream(pieces):
    return StreamingResponse(pieces, media_type="text/plain; charset=utf-8")


@router.post("/api/assistant/chat")
def chat(body: dict):
    messages = body.get("messages", []) if isinstance(body, dict) else []
    if not isinstance(messages, list):
        messages = []
    return text_stream(core.stream_reply(current_summary(), messages))


@router.get("/api/assistant/explain")
def explain():
    messages = [{"role": "user", "content": core.EXPLAIN_REQUEST}]
    return text_stream(core.stream_reply(current_summary(), messages))


@router.get("/api/assistant/status")
def assistant_status():
    return {"ai": core.ai_available(), "model": core.MODEL, "disclaimer": DISCLAIMER}


@router.post("/api/assistant/delete-my-data")
def delete_my_data():
    """Delete the tracker's saved pointer files (local_logs/). Memory is reset by 'New session'."""
    from tracker.log import delete_all_logs
    return {"deleted_files": delete_all_logs()}
