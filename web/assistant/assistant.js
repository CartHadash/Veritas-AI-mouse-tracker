// The assistant's chat panel (team leader's lane). It fills <div id="assistant-panel">.
// Plain JavaScript, no libraries. Replies stream in from POST /api/assistant/chat.
//
// Safety: the model's text is never inserted as HTML. The only formatting we honour is
// **highlight**, which we turn into <strong> elements ourselves, so the text cannot run code.
//
// Each reply ends with a line "SUGGESTIONS: question | question | question" (see
// assistant/prompt.py). We hide that line and turn it into the one-tap buttons.
//
// A reply may also carry a line "ACTIONS: set_mode=one_euro | open_tab=analysis" (builder,
// Sun 15 Nov, the team leader's idea). The assistant never does anything itself: each action
// becomes a button, and only the PERSON pressing it changes something. The page accepts only
// the names and values in ACTIONS below and ignores everything else, so text from the model
// can never run code or change something that is not on this list.

(function () {
  const panel = document.getElementById("assistant-panel");
  if (!panel) return;

  const css = document.createElement("link");
  css.rel = "stylesheet";
  css.href = "assistant/assistant.css?v=" + Date.now();   // never an old cached copy
  document.head.appendChild(css);

  // The first one-tap questions (typing is hard with a tremor). After each answer the
  // assistant's own follow-up suggestions replace them.
  const STARTERS = ["Explain my summary", "When was my tremor strongest?", "What settings do you suggest?"];
  const COMPARE = "How does today compare with before?";   // added when earlier sessions exist
  const MARKER = "SUGGESTIONS:";
  const ACTION_MARKER = "ACTIONS:";

  // The ONLY things an action button can do. name -> the values allowed, the button's words,
  // and what pressing it does (all through the page's own functions, as if the person had
  // used the control themselves). MODE_NAMES, postSettings and openTab are app.js's.
  const RESPONSE_NAMES = { steadiest: "Steadiest", balanced: "Balanced", responsive: "Faster" };
  const TAB_NAMES_SHOWN = { practice: "Practice", analysis: "Analysis", how: "How it works" };
  const ACTIONS = {
    set_mode: { ok: (v) => ["none", "low_sensitivity", "one_euro", "learned"].includes(v),
                label: (v) => `Switch to ${MODE_NAMES[v]}`, run: (v) => postSettings({ mode: v }) },
    set_strength: { ok: (v) => /^(0(\.\d)?|1(\.0)?)$/.test(v),
                    label: (v) => `Set strength to ${Number(v)}`, run: (v) => postSettings({ strength: Number(v) }) },
    set_response: { ok: (v) => v in RESPONSE_NAMES,
                    label: (v) => `Use ${RESPONSE_NAMES[v]}`, run: (v) => postSettings({ response: v }) },
    set_demo: { ok: (v) => v === "on" || v === "off",
                label: (v) => `Turn demo tremor ${v}`, run: (v) => postSettings({ demo_tremor: v === "on" }) },
    open_tab: { ok: (v) => v in TAB_NAMES_SHOWN,
                label: (v) => `Open ${TAB_NAMES_SHOWN[v]}`, run: (v) => openTab(v) },
    start_calibration: { ok: (v) => v === "",
                         label: () => "Start the calibration test",
                         run: () => { openTab("practice"); document.getElementById("calibrate").click(); } },
  };
  // On the assistant's own test page (assistant/standalone.py) there is no practice page to act on.
  const canAct = typeof postSettings === "function" && typeof openTab === "function";

  // "set_mode=one_euro | run=evil | open_tab=analysis" -> the allowed ones only, at most three.
  function parseActions(line) {
    if (!line || !canAct) return [];
    const found = [];
    for (const piece of line.split("|")) {
      const [name, value = ""] = piece.replace(/\*/g, "").trim().split("=").map((t) => t.trim().toLowerCase());
      const action = Object.prototype.hasOwnProperty.call(ACTIONS, name) ? ACTIONS[name] : null;
      if (action && action.ok(value)) found.push({ label: action.label(value), run: () => action.run(value) });
    }
    return found.slice(0, 3);
  }

  panel.classList.add("panel", "assistant");
  panel.innerHTML = `
    <h2>Ask the assistant</h2>
    <p class="small assistant-mode" aria-live="polite">Checking the assistant...</p>
    <div class="assistant-log" aria-live="polite"></div>
    <p class="assistant-tap-hint">Tap a question:</p>
    <div class="buttons assistant-starters"></div>
    <form class="assistant-form">
      <label class="assistant-label" for="assistant-input">Or type your own question</label>
      <div class="assistant-row">
        <input id="assistant-input" type="text" autocomplete="off" maxlength="1500"
               placeholder="For example: how steady was I?">
        <button type="submit">Send</button>
      </div>
    </form>
    <p class="assistant-disclaimer"><b>This project is a prototype and is not medical advice.</b>
      The assistant only sees the summary numbers, never your raw movement.</p>
    <div class="buttons"><button type="button" class="assistant-delete">Delete my saved pointer data</button></div>`;

  const modeLine = panel.querySelector(".assistant-mode");
  const log = panel.querySelector(".assistant-log");
  const form = panel.querySelector(".assistant-form");
  const input = panel.querySelector("#assistant-input");
  const startersBox = panel.querySelector(".assistant-starters");
  const history = [];          // the conversation so far: [{role, content}, ...]
  let busy = false;

  // Show a list of one-tap questions. When they are follow-ups, also offer a way back.
  function showQuestions(questions) {
    startersBox.replaceChildren();
    for (const question of questions) {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = question;
      button.addEventListener("click", () => ask(question));
      startersBox.appendChild(button);
    }
    if (questions !== STARTERS) {
      const back = document.createElement("button");
      back.type = "button";
      back.className = "assistant-back";
      back.textContent = "↺ Main questions";
      back.addEventListener("click", () => showQuestions(STARTERS));
      startersBox.appendChild(back);
    }
  }
  showQuestions(STARTERS);

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const question = input.value.trim();
    if (question) { input.value = ""; ask(question); }
  });

  panel.querySelector(".assistant-delete").addEventListener("click", deleteMyData);

  // Split a (possibly half-received) reply into the answer and the suggestions line.
  // While streaming, the start of "SUGGESTIONS:" may have arrived only partly ("SUGG"),
  // so a trailing piece that could be the start of the marker is held back.
  // The "ACTIONS:" line (wherever it is) is taken out the same way and returned apart.
  function splitReply(text) {
    let actions = null;
    const line = text.match(/^[ \t]*ACTIONS:(.*)$/m);
    if (line) { actions = line[1]; text = text.replace(line[0], ""); }
    const at = text.indexOf(MARKER);
    if (at >= 0) return { answer: text.slice(0, at), suggestions: text.slice(at + MARKER.length), actions };
    for (const marker of [MARKER, ACTION_MARKER]) {
      for (let k = Math.min(marker.length - 1, text.length); k > 0; k--) {
        if (marker.startsWith(text.slice(-k))) return { answer: text.slice(0, -k), suggestions: null, actions };
      }
    }
    return { answer: text, suggestions: null, actions };
  }

  function parseSuggestions(line) {
    if (!line) return [];
    return line.split("\n")[0].split("|")
      .map((q) => q.replace(/\*/g, "").trim())
      .filter((q) => q.length > 0 && q.length <= 80)
      .slice(0, 3);
  }

  // Put text in an element, turning **this** into a highlighted <strong>. Safe: text only.
  function renderHighlighted(element, text) {
    element.replaceChildren();
    const parts = text.trim().split(/\*\*([^*]+)\*\*/);
    parts.forEach((part, i) => {
      if (i % 2 === 1) {
        const strong = document.createElement("strong");
        strong.className = "assistant-highlight";
        strong.textContent = part;
        element.appendChild(strong);
      } else {
        element.appendChild(document.createTextNode(part.replace(/\*\*/g, "")));
      }
    });
  }

  function addBubble(role, text) {
    const bubble = document.createElement("p");
    bubble.className = "assistant-bubble " + role;
    renderHighlighted(bubble, text);
    log.appendChild(bubble);
    log.scrollTop = log.scrollHeight;
    return bubble;
  }

  // Under EVERY answer, the same fixed reminder (Oleksandr, Sun 15 Nov). It is written here,
  // by the page, so it is always there whatever the model wrote.
  const REMINDER = "Reminder: these numbers are estimates from a student prototype trained on public " +
    "research recordings. They can be wrong and are not medical advice. For advice or treatment, " +
    "please talk to your doctor.";
  function addReminder(bubble) {
    const note = document.createElement("p");
    note.className = "assistant-reminder";
    note.textContent = REMINDER;
    bubble.after(note);
    return note;
  }

  // Keep the newest part of the conversation in view. In the floating window it is the
  // window that scrolls, not the log, so the last element is scrolled into view as well.
  function showNewest() {
    log.scrollTop = log.scrollHeight;
    if (log.lastElementChild) log.lastElementChild.scrollIntoView({ block: "nearest" });
  }

  // "Read aloud" under an answer: the browser's built-in speech (no API, no key, works
  // offline on macOS). Reading is easier than small text for many of our users.
  function addReadAloud(bubble, after) {
    if (!("speechSynthesis" in window)) return;     // a browser without speech: no button
    const button = document.createElement("button");
    button.type = "button";
    button.className = "assistant-speak";
    button.textContent = "Read aloud";
    button.addEventListener("click", () => {
      if (speechSynthesis.speaking) {                // second tap stops it
        speechSynthesis.cancel();
        return;
      }
      const speech = new SpeechSynthesisUtterance(bubble.textContent);
      speech.lang = "en-US";
      speech.rate = 0.95;                            // a little slower than normal
      speech.onstart = () => { button.textContent = "Stop reading"; };
      speech.onend = speech.onerror = () => { button.textContent = "Read aloud"; };
      speechSynthesis.speak(speech);
    });
    after.after(button);                             // under the answer and its reminder
    showNewest();
  }

  // One button per allowed action, under the answer. Pressing it is the person's own act.
  function addActions(after, actions) {
    if (!actions.length) return;
    const row = document.createElement("div");
    row.className = "buttons assistant-actions";
    for (const action of actions) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "assistant-action";
      button.textContent = action.label;
      button.addEventListener("click", async () => {
        try {
          await action.run();
          button.textContent = action.label + " \u2713";
        } catch (error) {
          button.textContent = action.label + " (did not work)";
        }
      });
      row.appendChild(button);
    }
    after.after(row);
    log.scrollTop = log.scrollHeight;
  }

  function setBusy(on) {
    busy = on;
    for (const button of panel.querySelectorAll("button")) button.disabled = on;
    input.disabled = on;
  }

  async function ask(question) {
    if (busy) return;
    setBusy(true);
    history.push({ role: "user", content: question });
    addBubble("user", question);
    const bubble = addBubble("assistant", "...");
    let reply = "";
    try {
      const response = await fetch("/api/assistant/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: history }),
      });
      if (!response.ok || !response.body) throw new Error("HTTP " + response.status);
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        reply += decoder.decode(value, { stream: true });
        renderHighlighted(bubble, splitReply(reply).answer || "...");
        showNewest();
      }
    } catch (error) {
      reply = reply || "Sorry, the assistant could not be reached. The rest of the app still works.";
    }
    const { answer, suggestions, actions } = splitReply(reply);
    renderHighlighted(bubble, answer);
    const note = addReminder(bubble);
    addReadAloud(bubble, note);
    addActions(log.lastElementChild, parseActions(actions));
    showNewest();
    history.push({ role: "assistant", content: answer.trim() });
    const next = parseSuggestions(suggestions);
    showQuestions(next.length ? next : STARTERS);
    setBusy(false);
  }

  async function deleteMyData() {
    if (!confirm("Delete all pointer data saved on this laptop (the local_logs folder)?")) return;
    try {
      const response = await fetch("/api/assistant/delete-my-data", { method: "POST" });
      const result = await response.json();
      addBubble("assistant", `Deleted **${result.deleted_files} saved file(s)**. ` +
        "Use \"New session\" to also clear this session's numbers.");
    } catch (error) {
      addBubble("assistant", "Sorry, deleting did not work.");
    }
  }

  async function showMode() {
    try {
      const status = await (await fetch("/api/assistant/status")).json();
      modeLine.textContent = status.ai
        ? "AI assistant on. It explains your numbers in plain words."
        : "AI assistant off (no API key on this laptop): answers are a plain summary made by ordinary code.";
      if (status.ai && status.past_sessions > 0 && !STARTERS.includes(COMPARE)) {
        STARTERS.push(COMPARE);
        modeLine.textContent += ` It can also compare with ${status.past_sessions} earlier session(s) saved on this laptop.`;
        if (!history.length) showQuestions(STARTERS);
      }
    } catch (error) {
      modeLine.textContent = "The assistant is not available right now.";
    }
  }
  showMode();
})();
