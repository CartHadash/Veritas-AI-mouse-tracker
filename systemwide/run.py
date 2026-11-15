"""
run.py - B3: make the REAL macOS cursor steadier in every app (stretch goal, macOS only).

Written fresh during the hackathon (Sat 14 Nov); nothing from the pre-hackathon experiment.

    python -m systemwide.run                          # our model, 60 seconds
    python -m systemwide.run --demo strong            # add replayed tremor (to see the effect)
    python -m systemwide.run --demo strong --mode none    # the same tremor, no correction
    python -m systemwide.run --method warp            # if the cursor does not move with "event"
    python -m systemwide.run --response balanced      # less lag, a little more shake
    python -m systemwide.run --no-freeze              # without click freeze

SAFETY (built first): it switches itself off after --seconds (default 60, at most 600);
Control + Option + X switches it off at once from any app; Ctrl+C in the terminal stops it;
if the filter fails, the cursor follows the hand uncorrected.

It needs the Accessibility permission (and, on recent macOS, Input Monitoring) for the app
that runs Python (your terminal): System Settings -> Privacy & Security -> Accessibility (and
Input Monitoring) -> switch the terminal on -> quit and reopen the terminal. ONLY A HUMAN may
change this setting. The program only CHECKS it (no dialog pops up) and stops if it is missing.

How it works: a macOS "event tap" sees every mouse event before apps do. For each movement,
systemwide/steady.py works out where the hand is and where the corrected cursor should be, and
the event is changed to put the cursor there (or, with --method warp, the cursor is moved
directly). Clicks are moved to where the corrected cursor is shown, and click freeze holds the
cursor at the press point until the release (at most 0.3 s), as on the demo page. While the
hand is still the filter is still fed every 10 ms, so replayed shaking stays visible and the
correction does not have to warm up again after a pause.
Nothing is saved anywhere.

This project is a prototype and is not medical advice.
"""

import argparse
import signal
import sys
import time

from models.corrector.live import RESPONSE_LEVELS
from systemwide.steady import DEMO_LEVELS, MODES, SteadyCursor

KEY_X = 7                      # macOS key code of the X key
IDLE_UPDATE = 0.01             # s: while the mouse is still, feed the filter this often
DEFAULT_RESPONSE = "steadiest" # our model's smoothing level here (see evaluation/systemwide_clicks.py)
MAX_SECONDS = 600


def permission_ok(Q):
    """True if this terminal may watch and change mouse events. Only checks; never asks."""
    return bool(Q.CGPreflightListenEventAccess()) and bool(Q.CGPreflightPostEventAccess())


def screen_bounds(Q):
    """(left, top, right, bottom) around all active displays, in screen points."""
    error, ids, count = Q.CGGetActiveDisplayList(16, None, None)
    rects = [Q.CGDisplayBounds(d) for d in ids[:count]] or [Q.CGDisplayBounds(Q.CGMainDisplayID())]
    return (min(r.origin.x for r in rects), min(r.origin.y for r in rects),
            max(r.origin.x + r.size.width for r in rects), max(r.origin.y + r.size.height for r in rects))


def main():
    parser = argparse.ArgumentParser(description="Steadier real cursor in every app (macOS, prototype).")
    parser.add_argument("--mode", choices=MODES, default="learned")
    parser.add_argument("--demo", choices=["none"] + DEMO_LEVELS, default="none",
                        help="add replayed tremor of test people (to see the effect)")
    parser.add_argument("--strength", type=float, default=1.0)
    parser.add_argument("--seconds", type=float, default=60.0, help="switch off after this long (max 600)")
    parser.add_argument("--response", choices=list(RESPONSE_LEVELS), default=DEFAULT_RESPONSE,
                        help="our model's smoothing: steadiest, balanced or responsive (less lag, more shake)")
    parser.add_argument("--no-freeze", action="store_true",
                        help="switch click freeze off (it holds the cursor at the press point, at most 0.3 s)")
    parser.add_argument("--method", choices=["event", "warp"], default="event",
                        help="how to move the cursor: change the event (default) or move the cursor directly")
    args = parser.parse_args()
    if sys.platform != "darwin":
        raise SystemExit("System-wide correction works on macOS only.")
    import Quartz as Q

    if not permission_ok(Q):
        raise SystemExit(
            "This terminal does not have permission to watch and move the mouse.\n"
            "A human must switch it on: System Settings -> Privacy & Security -> Accessibility\n"
            "(and Input Monitoring) -> switch on this terminal app -> quit and reopen it.")

    seconds = min(max(args.seconds, 1.0), MAX_SECONDS)
    here = Q.CGEventGetLocation(Q.CGEventCreate(None))
    steady = SteadyCursor((here.x, here.y), screen_bounds(Q), mode=args.mode,
                          demo_level=None if args.demo == "none" else args.demo, strength=args.strength,
                          response=args.response, freeze=not args.no_freeze)
    state = {"stop": False, "last_move": time.monotonic(), "tap": None}

    moves = (Q.kCGEventMouseMoved, Q.kCGEventLeftMouseDragged, Q.kCGEventRightMouseDragged,
             Q.kCGEventOtherMouseDragged)
    downs = (Q.kCGEventLeftMouseDown, Q.kCGEventRightMouseDown)
    ups = (Q.kCGEventLeftMouseUp, Q.kCGEventRightMouseUp)
    buttons = downs + ups

    def show(x, y, event=None):
        if args.method == "event" and event is not None:
            Q.CGEventSetLocation(event, Q.CGPointMake(x, y))
        else:
            Q.CGWarpMouseCursorPosition(Q.CGPointMake(x, y))

    def callback(proxy, event_type, event, refcon):
        try:
            if event_type in (Q.kCGEventTapDisabledByTimeout, Q.kCGEventTapDisabledByUserInput):
                Q.CGEventTapEnable(state["tap"], True)        # macOS paused the tap: resume
            elif event_type == Q.kCGEventKeyDown:
                code = Q.CGEventGetIntegerValueField(event, Q.kCGKeyboardEventKeycode)
                flags = Q.CGEventGetFlags(event)
                if code == KEY_X and flags & Q.kCGEventFlagMaskControl and flags & Q.kCGEventFlagMaskAlternate:
                    state["stop"] = True                      # the off switch
                    return None                               # do not type the X
            elif event_type in moves:
                p = Q.CGEventGetLocation(event)
                now = time.monotonic()
                show(*steady.move_to(p.x, p.y, now), event=event)
                state["last_move"] = now
            elif event_type in buttons:
                Q.CGEventSetLocation(event, Q.CGPointMake(*steady.shown))   # click where it is shown
                if event_type in downs:
                    steady.press(time.monotonic())            # click freeze starts
                else:
                    steady.release()
        except Exception:
            pass                                              # never block the mouse
        return event

    mask = 0
    for kind in moves + buttons + (Q.kCGEventKeyDown,):
        mask |= Q.CGEventMaskBit(kind)
    tap = Q.CGEventTapCreate(Q.kCGSessionEventTap, Q.kCGHeadInsertEventTap, Q.kCGEventTapOptionDefault,
                             mask, callback, None)
    if tap is None:
        steady.stop()
        raise SystemExit("macOS refused the event tap (permission missing?). Nothing was changed.")
    state["tap"] = tap
    source = Q.CFMachPortCreateRunLoopSource(None, tap, 0)
    loop = Q.CFRunLoopGetCurrent()
    Q.CFRunLoopAddSource(loop, source, Q.kCFRunLoopCommonModes)
    Q.CGEventTapEnable(tap, True)
    Q.CGSetLocalEventsSuppressionInterval(0.0)                # moving the cursor must not freeze the mouse
    signal.signal(signal.SIGINT, lambda *a: state.update(stop=True))

    end = time.monotonic() + seconds
    print("Steady cursor ON: %s (%s), demo tremor %s, click freeze %s, method %s." % (
        args.mode, args.response, args.demo, "off" if args.no_freeze else "on", args.method))
    print("Switch off: Control + Option + X (any app), Ctrl+C here, or wait %.0f s." % seconds)
    try:
        while not state["stop"] and time.monotonic() < end:
            Q.CFRunLoopRunInMode(Q.kCFRunLoopDefaultMode, IDLE_UPDATE, False)
            now = time.monotonic()
            # While the mouse sends nothing, keep the filter fed every 10 ms. With demo tremor
            # this shows the replayed shaking; without it, it keeps the detector's 2.56 s of
            # history alive, so the correction does not have to warm up again after a pause.
            if steady.filter is not None or steady.demo is not None:
                if now - state["last_move"] >= IDLE_UPDATE:
                    before = steady.shown
                    after = steady.move_to(before[0], before[1], now)
                    if abs(after[0] - before[0]) + abs(after[1] - before[1]) > 0.01:
                        show(*after)                          # only move the cursor if it changed
                    state["last_move"] = now
    finally:
        Q.CGEventTapEnable(tap, False)
        Q.CFRunLoopRemoveSource(loop, source, Q.kCFRunLoopCommonModes)
        Q.CFMachPortInvalidate(tap)
        steady.stop()
        print("Steady cursor OFF. %d updates, %d filter failures (cursor followed the hand)." % (
            steady.updates, steady.failures))


if __name__ == "__main__":
    main()
