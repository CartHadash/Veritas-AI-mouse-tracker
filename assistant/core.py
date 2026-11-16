"""Talks to the Claude API: takes the session summary and the chat, streams back text.

Only the SUMMARY numbers (GET /api/summary) are sent to the API. Raw pointer samples never are.
Without an API key, the assistant is switched off and fixed_explanation() builds a plain,
clearly non-AI summary from the numbers with ordinary code.
"""

import os
import re
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from assistant.prompt import DISCLAIMER, SYSTEM_PROMPT, past_block, summary_block

MODEL = "claude-sonnet-5-5"      # Sonnet 5.5
EFFORT = "low"                   # recommended start for chat on this model: quick, cheap
MAX_TOKENS = 8000                # room for its thinking plus a short answer
MAX_MESSAGES = 20                # only the latest messages are sent
MAX_WORDS = 200                  # per message: enough for a real question,
                                 # no room to paste a long document or program for it to work on
MAX_CHARS = 2000                 # and never more characters than this, whatever the words are

# The key is read from the file .env (ignored by git) or the shell. It is never printed.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

EXPLAIN_REQUEST = ("Explain my session summary in two or three plain sentences. "
                   "Mention anything in the notes that matters.")


def ai_available():
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def shorten(text):
    """The first MAX_WORDS words of a message (its spacing kept), and at most MAX_CHARS characters."""
    first = re.match(r"\s*(?:\S+\s+){0,%d}\S+" % (MAX_WORDS - 1), text)
    return (first.group(0) if first else text)[:MAX_CHARS]


def clean_messages(messages):
    """Keep only well-formed user/assistant text messages, newest last, ending with the user."""
    cleaned = []
    for message in messages[-MAX_MESSAGES:]:
        if not isinstance(message, dict):
            continue
        role, content = message.get("role"), message.get("content")
        if role in ("user", "assistant") and isinstance(content, str) and content.strip():
            cleaned.append({"role": role, "content": shorten(content)})
    while cleaned and cleaned[0]["role"] != "user":       # must start with the user
        cleaned.pop(0)
    while cleaned and cleaned[-1]["role"] != "user":      # and end with the user
        cleaned.pop()
    return cleaned


# Anything that looks like an API key ("sk-" followed by a long run of key characters).
KEY_SHAPE = re.compile(r"sk-[A-Za-z0-9_\-]{16,}")
REMOVED = "[removed]"


def scrub(text):
    """Blank out our own API key and anything shaped like a key."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key and len(key) >= 8:
        text = text.replace(key, REMOVED)
    return KEY_SHAPE.sub(REMOVED, text)


# The end of some text that could be the beginning of a key still arriving: "s", "sk", or
# "sk-" followed by key characters right up to the end.
KEY_ARRIVING = re.compile(r"(sk-[A-Za-z0-9_\-]*|sk|s)$")


def scrubbed(pieces):
    """Pass a stream of text pieces on with every key-like string blanked out.

    The model is never shown the key, so it cannot know it. This is a second lock on the same
    door: whatever text comes back, nothing shaped like a key can reach the page. A key could
    arrive split over several pieces, so text that could be the start of one is held back
    until the next character shows whether it is (then it is removed) or not (then it is
    passed on). Ordinary words that end in "s" are held for only one piece."""
    key = os.environ.get("ANTHROPIC_API_KEY") or ""
    held = ""
    for piece in pieces:
        held += piece
        starts = []
        arriving = KEY_ARRIVING.search(held)
        if arriving:
            starts.append(arriving.start())
        for k in range(min(len(key) - 1, len(held)), 0, -1):     # the tail is the start of OUR key
            if key.startswith(held[-k:]):
                starts.append(len(held) - k)
                break
        cut = min(starts) if starts else len(held)
        if cut > 0:
            yield scrub(held[:cut])
            held = held[cut:]
    if held:
        yield scrub(held)


def stream_reply(summary, messages, past=None):
    """Yield the assistant's reply piece by piece. Never raises: problems become friendly text.
    Every piece goes through scrubbed(), so nothing shaped like an API key can come out.

    past: short versions of earlier sessions saved on this laptop (assistant/history.py)."""
    return scrubbed(_reply(summary, messages, past))


def _reply(summary, messages, past=None):
    messages = clean_messages(messages)
    if not messages:
        yield "Please type a question, or tap one of the buttons."
        return
    if not ai_available():
        yield ("The AI assistant is switched off (no API key on this laptop). "
               "Here is a plain summary made by ordinary code instead:\n\n")
        yield fixed_explanation(summary)
        return

    # A key made outside a workspace must say which workspace to bill. The workspace ID is
    # not a secret; put ANTHROPIC_WORKSPACE_ID=... in .env if the API asks for it.
    workspace = os.environ.get("ANTHROPIC_WORKSPACE_ID")
    try:
        client = anthropic.Anthropic(default_headers={"anthropic-workspace-id": workspace} if workspace else None)
        # Beta endpoint only for the refusal fallback ("fallbacks"): if Anthropic's safety
        # filter declines, the API may retry on another model automatically.
        with client.beta.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=[{"type": "text", "text": SYSTEM_PROMPT},
                    {"type": "text", "text": summary_block(summary)},
                    {"type": "text", "text": past_block(past or [])}],
            messages=messages,
            output_config={"effort": EFFORT},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        ) as stream:
            for text in stream.text_stream:
                yield text
            final = stream.get_final_message()
    except anthropic.AuthenticationError:
        yield "The assistant could not start: the API key in .env was not accepted."
        return
    except anthropic.RateLimitError:
        yield "The assistant is busy right now. Please wait a minute and try again."
        return
    except anthropic.APIConnectionError:
        yield "The assistant could not reach the internet. The rest of the app still works."
        return
    except anthropic.APIStatusError as error:
        # The details go to the terminal for us (they never contain the key), not to the user.
        print("assistant: API error %s: %s" % (error.status_code, error.message), file=sys.stderr)
        yield "The assistant had a problem (error %s). Please try again." % error.status_code
        return
    except Exception as error:
        # Anything unexpected: only the KIND of error goes to the terminal, never its text
        # (it could quote part of a request), and the person gets a plain sentence.
        print("assistant: unexpected error (%s)" % type(error).__name__, file=sys.stderr)
        yield "The assistant had a problem. The rest of the app still works; please try again."
        return

    if final.stop_reason == "refusal":
        yield ("\n\nI can't help with that one. I can explain your summary numbers or "
               "suggest settings to try.")
    elif final.stop_reason == "max_tokens":
        yield "\n\n(My answer was cut short. Please ask again in a shorter way.)"


# The filter names shown on the page (server/main.py uses the internal ones as keys).
FILTER_NAMES = {"none": "No filter", "low_sensitivity": "Lower sensitivity",
                "one_euro": "One Euro", "learned": "Our model"}


def fixed_explanation(summary):
    """A plain explanation built with ordinary code: used when the AI is switched off."""
    tremor = summary.get("tremor", {})
    usage = summary.get("usage", {})
    session = summary.get("session", {})
    lines = []

    minutes = session.get("minutes_active")
    if minutes is not None:
        if minutes < 1:      # "about 0 minutes" read like nothing happened
            lines.append("The pointer was moving for less than a minute.")
        else:
            lines.append("The pointer was moving for about %.0f minute%s."
                         % (minutes, "" if round(minutes) == 1 else "s"))

    share = tremor.get("detected_share")
    if share is None:
        lines.append("No movement has been analysed for shaking yet.")
    else:
        lines.append("Tremor-like shaking was flagged **about %d%% of the time**." % round(share * 100))
        freq, size = tremor.get("typical_frequency_hz"), tremor.get("typical_strength_px")
        if freq is not None and size is not None:
            lines.append("When flagged, it was typically about %.1f shakes per second and about "
                         "%.1f pixels on screen." % (freq, size))
        by_time = [m for m in tremor.get("by_time", []) if m.get("detected_share") is not None]
        if len(by_time) > 1:
            top = max(by_time, key=lambda m: m["detected_share"])
            lines.append("It was flagged most often **around minute %d**." % top["minute"])

    steadiness = usage.get("steadiness_score")
    if steadiness is not None:
        lines.append("Steadiness score: **%.2f** (0 = very shaky, 1 = very steady)." % steadiness)
    accuracy = usage.get("click_accuracy")
    if accuracy is not None:
        lines.append("%d%% of %d clicks hit the practice targets."
                     % (round(accuracy * 100), usage.get("clicks_in_app", 0)))
    filt = summary.get("filter", {})
    if filt.get("mode"):
        # The names the person sees on the page, not the internal ones ("learned", ...).
        name = FILTER_NAMES.get(filt["mode"], filt["mode"])
        lines.append("Cursor smoothing: %s, strength %s." % (name, filt.get("strength")))

    for note in summary.get("notes", []):
        lines.append("Note: %s" % note)
    lines.append(DISCLAIMER)
    return " ".join(lines)
