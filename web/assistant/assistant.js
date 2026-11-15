// The assistant's chat panel (team leader's lane). It fills <div id="assistant-panel">.
// Plain JavaScript, no libraries. Replies stream in from POST /api/assistant/chat.
//
// Safety: the model's text is never inserted as HTML. The only formatting we honour is
// **highlight**, which we turn into <strong> elements ourselves, so the text cannot run code.
//
// Each reply ends with a line "SUGGESTIONS: question | question | question" (see
// assistant/prompt.py). We hide that line and turn it into the one-tap buttons.

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
        <input id="assistant-input" type="text" autocomplete="off" maxlength="500"
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
  function splitReply(text) {
    const at = text.indexOf(MARKER);
    if (at >= 0) return { answer: text.slice(0, at), suggestions: text.slice(at + MARKER.length) };
    for (let k = Math.min(MARKER.length - 1, text.length); k > 0; k--) {
      if (MARKER.startsWith(text.slice(-k))) return { answer: text.slice(0, -k), suggestions: null };
    }
    return { answer: text, suggestions: null };
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

  // "Read aloud" under an answer: the browser's built-in speech (no API, no key, works
  // offline on macOS). Reading is easier than small text for many of our users.
  function addReadAloud(bubble) {
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
    bubble.after(button);
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
        log.scrollTop = log.scrollHeight;
      }
    } catch (error) {
      reply = reply || "Sorry, the assistant could not be reached. The rest of the app still works.";
    }
    const { answer, suggestions } = splitReply(reply);
    renderHighlighted(bubble, answer);
    addReadAloud(bubble);
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
