// The assistant's chat panel (team leader's lane). It fills <div id="assistant-panel">.
// Plain JavaScript, no libraries. Replies stream in from POST /api/assistant/chat.
// Model text is always shown with textContent (never as HTML), so it cannot run code.

(function () {
  const panel = document.getElementById("assistant-panel");
  if (!panel) return;

  // Load the panel's styles (same folder as this file).
  const css = document.createElement("link");
  css.rel = "stylesheet";
  css.href = "assistant/assistant.css";
  document.head.appendChild(css);

  // One-tap questions, because typing is hard with a tremor.
  const STARTERS = ["Explain my summary", "When was my tremor strongest?", "What settings do you suggest?"];

  panel.classList.add("panel", "assistant");
  panel.innerHTML = `
    <h2>Ask the assistant</h2>
    <p class="small assistant-mode" aria-live="polite">Checking the assistant...</p>
    <div class="buttons assistant-starters"></div>
    <div class="assistant-log" aria-live="polite"></div>
    <form class="assistant-form">
      <label class="assistant-label" for="assistant-input">Or type a question</label>
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

  for (const question of STARTERS) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = question;
    button.addEventListener("click", () => ask(question));
    startersBox.appendChild(button);
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const question = input.value.trim();
    if (question) { input.value = ""; ask(question); }
  });

  panel.querySelector(".assistant-delete").addEventListener("click", deleteMyData);

  function addBubble(role, text) {
    const bubble = document.createElement("p");
    bubble.className = "assistant-bubble " + role;
    bubble.textContent = text;
    log.appendChild(bubble);
    log.scrollTop = log.scrollHeight;
    return bubble;
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
      // Read the reply piece by piece as it is written.
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        reply += decoder.decode(value, { stream: true });
        bubble.textContent = reply;
        log.scrollTop = log.scrollHeight;
      }
    } catch (error) {
      reply = reply || "Sorry, the assistant could not be reached. The rest of the app still works.";
      bubble.textContent = reply;
    }
    history.push({ role: "assistant", content: reply });
    setBusy(false);
  }

  async function deleteMyData() {
    if (!confirm("Delete all pointer data saved on this laptop (the local_logs folder)?")) return;
    try {
      const response = await fetch("/api/assistant/delete-my-data", { method: "POST" });
      const result = await response.json();
      addBubble("assistant", `Deleted ${result.deleted_files} saved file(s). ` +
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
    } catch (error) {
      modeLine.textContent = "The assistant is not available right now.";
    }
  }
  showMode();
})();
