"""
test_ws.py - check the running server: send 500 pointer samples over /ws/cursor, expect 500
replies, and print the average reply time. Also checks /api/summary has Contract 2's shape.

First start the server in another terminal:
    python -m uvicorn server.main:app
Then:
    python server/test_ws.py
"""

import asyncio
import json
import math
import time
import urllib.request

import websockets

URL = "ws://127.0.0.1:8000/ws/cursor"
API = "http://127.0.0.1:8000"


def post(path, body):
    request = urllib.request.Request(API + path, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(request))


async def run(mode, demo):
    post("/api/settings", {"mode": mode, "demo_tremor": demo, "strength": 1.0})
    times, replies = [], []
    async with websockets.connect(URL) as ws:
        for i in range(500):
            t = i / 100
            sample = {"t": t, "x": 600 + 200 * math.sin(t), "y": 400 + 100 * math.cos(t)}
            start = time.perf_counter()
            await ws.send(json.dumps(sample))
            replies.append(json.loads(await ws.recv()))
            times.append((time.perf_counter() - start) * 1000)
        await ws.send(json.dumps({"type": "click", "hit": True}))
    times = sorted(times)
    last = replies[-1]
    print("%-15s demo tremor %-5s: %d replies; reply time mean %.2f ms, 99th percentile %.2f ms; "
          "last score %s, size %s px" % (mode, demo, len(replies), sum(times) / len(times),
                                        times[int(0.99 * len(times))], last["score"], last["size_px"]))
    return len(replies)


async def main():
    total = 0
    for mode in ["learned", "one_euro", "low_sensitivity", "none"]:
        total += await run(mode, demo=(mode == "learned"))
    summary = json.load(urllib.request.urlopen(API + "/api/summary"))
    expected = {"session", "tremor", "usage", "filter", "model_info", "notes"}
    print("Summary keys OK:", expected <= set(summary), "| detected share:",
          summary["tremor"]["detected_share"], "| clicks:", summary["usage"]["clicks_in_app"],
          "| notes:", summary["notes"])
    print("Status:", json.load(urllib.request.urlopen(API + "/api/status")))
    post("/api/settings", {"mode": "learned", "demo_tremor": False})
    assert total == 2000, "expected 2000 replies"


if __name__ == "__main__":
    asyncio.run(main())
