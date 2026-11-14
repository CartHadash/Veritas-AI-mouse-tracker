"""A tiny server with ONLY the assistant, using docs/contracts/summary_example.json.

    python -m assistant.standalone        then open http://127.0.0.1:8001

Lets us build and test the assistant without the builder's server or models.
"""

from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from assistant import router

WEB_ASSISTANT = Path(__file__).resolve().parent.parent / "web" / "assistant"

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Assistant (standalone test)</title>
<style>body{font-family:system-ui,sans-serif;background:#fff8f0;color:#3b2314;
max-width:640px;margin:24px auto;padding:0 16px}</style></head>
<body><h1>Assistant test page</h1>
<p>Uses the EXAMPLE summary (invented numbers), not a real session.</p>
<div id="assistant-panel"></div>
<script src="assistant/assistant.js"></script></body></html>"""

app = FastAPI(title="Assistant (standalone)")
app.include_router(router)
app.mount("/assistant", StaticFiles(directory=WEB_ASSISTANT), name="assistant-files")


@app.get("/", response_class=HTMLResponse)
def page():
    return PAGE


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
