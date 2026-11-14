"""Talks to the Claude API: takes the session summary and the chat, streams back text.

Only the SUMMARY numbers (Contract 2) are sent to the API. Raw pointer samples never are.
Without an API key, the assistant is switched off and fixed_explanation() builds a plain,
clearly non-AI summary from the numbers with ordinary code.
"""

import os
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from assistant.prompt import DISCLAIMER, SYSTEM_PROMPT, summary_block

MODEL = "claude-sonnet-5-5"      # DECISION L2 (team leader): Sonnet 5.5
EFFORT = "low"                   # recommended start for chat on this model: quick, cheap
MAX_TOKENS = 8000                # room for its thinking plus a short answer
MAX_MESSAGES = 20                # only the latest messages are sent
MAX_CHARS = 2000                 # per message; typing is hard for our user anyway

# The key is read from the file .env (ignored by git) or the shell. It is never printed.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

EXPLAIN_REQUEST = ("Explain my session summary in two or three plain sentences. "
                   "Mention anything in the notes that matters.")


def ai_available():
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def clean_messages(messages):
    """Keep only well-formed user/assistant text messages, newest last, ending with the user."""
    cleaned = []
    for message in messages[-MAX_MESSAGES:]:
        if not isinstance(message, dict):
            continue
        role, content = message.get("role"), message.get("content")
        if role in ("user", "assistant") and isinstance(content, str) and content.strip():
            cleaned.append({"role": role, "content": content[:MAX_CHARS]})
    while cleaned and cleaned[0]["role"] != "user":       # must start with the user
        cleaned.pop(0)
    while cleaned and cleaned[-1]["role"] != "user":      # and end with the user
        cleaned.pop()
    return cleaned


def stream_reply(summary, messages):
    """Yield the assistant's reply piece by piece. Never raises: problems become friendly text."""
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
    client = anthropic.Anthropic(default_headers={"anthropic-workspace-id": workspace} if workspace else None)
    try:
        # Beta endpoint only for the refusal fallback ("fallbacks"): if Anthropic's safety
        # filter declines, the API may retry on another model automatically.
        with client.beta.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=[{"type": "text", "text": SYSTEM_PROMPT},
                    {"type": "text", "text": summary_block(summary)}],
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

    if final.stop_reason == "refusal":
        yield ("\n\nI can't help with that one. I can explain your summary numbers or "
               "suggest settings to try.")
    elif final.stop_reason == "max_tokens":
        yield "\n\n(My answer was cut short. Please ask again in a shorter way.)"


def fixed_explanation(summary):
    """A plain explanation built with ordinary code: used when the AI is switched off."""
    tremor = summary.get("tremor", {})
    usage = summary.get("usage", {})
    session = summary.get("session", {})
    lines = []

    minutes = session.get("minutes_active")
    if minutes is not None:
        lines.append("The pointer was moving for about %.0f minutes." % minutes)

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
        lines.append("Cursor smoothing: %s, strength %s." % (filt["mode"], filt.get("strength")))

    for note in summary.get("notes", []):
        lines.append("Note: %s" % note)
    lines.append(DISCLAIMER)
    return " ".join(lines)
