// reading.js - an "Easier-to-read text" switch in the top bar (Oleksandr's accessibility idea;
// the team leader agreed, Sun 15 Nov). Plain JavaScript in its own file, like tutorial.js.
//
// What it does: switches the whole page to Verdana with wider spacing between letters, words
// and lines. That follows the British Dyslexia Association's style guide (a plain, evenly
// spaced sans-serif font such as Verdana; more space between letters, words and lines). Some
// readers with dyslexia find such text easier; it is a reading preference, not a treatment.
// No font is downloaded: Verdana is already on macOS and Windows. The choice is remembered in
// this browser only. Text drawn inside the practice area itself keeps its font.

(function () {
  const KEY = "steadyPointerEasyRead";

  const style = document.createElement("style");
  style.textContent = `
    :root.easy-read { --font: Verdana, Tahoma, "DejaVu Sans", Arial, sans-serif; }
    :root.easy-read body { letter-spacing: 0.035em; word-spacing: 0.12em; line-height: 1.6; }
    :root.easy-read p, :root.easy-read li, :root.easy-read small { line-height: 1.6; }
    /* Rows of buttons have a fixed width: keep their spacing normal and the text a little
       smaller, so the wider font still fits (checked at phone and laptop widths). */
    :root.easy-read ui-segmented-control-item, :root.easy-read ui-tabs-tab button {
      letter-spacing: 0; word-spacing: 0; font-size: 0.82em; }
    .topbar-tools { grid-column: 1 / -1; display: flex; flex-wrap: wrap; gap: 8px; justify-content: flex-end; }
    .topbar-tools .tutorial-open { margin-left: 0; }
    .easy-read-toggle { font: inherit; font-size: 14px; border-radius: 999px; padding: 4px 12px; cursor: pointer;
      border: 1.5px solid var(--edge, #a8825a); background: var(--surface, #fffdf8); color: var(--ink, #2f1d10); }
    .easy-read-toggle[aria-pressed="true"] { background: var(--steady, #1f6f57); border-color: var(--steady, #1f6f57); color: #fff; }`;
  document.head.appendChild(style);

  function saved() { try { return localStorage.getItem(KEY) === "1"; } catch (e) { return false; } }
  function save(on) { try { localStorage.setItem(KEY, on ? "1" : "0"); } catch (e) { /* private window: fine */ } }

  function apply(on, button) {
    document.documentElement.classList.toggle("easy-read", on);
    if (button) button.setAttribute("aria-pressed", String(on));
  }

  apply(saved(), null);                    // as early as possible, so the page does not flicker

  function build() {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "easy-read-toggle";
    button.textContent = "Easier-to-read text";
    button.title = "Verdana with wider spacing (often easier to read with dyslexia)";
    apply(saved(), button);
    button.addEventListener("click", () => {
      const on = !document.documentElement.classList.contains("easy-read");
      apply(on, button);
      save(on);
    });
    // Next to "How to use" (tutorial.js) in a small row of tools under the top bar.
    const bar = document.querySelector(".topbar");
    if (!bar) return;
    let tools = bar.querySelector(".topbar-tools");
    if (!tools) {
      tools = document.createElement("div");
      tools.className = "topbar-tools";
      bar.appendChild(tools);
    }
    const guide = bar.querySelector(".tutorial-open");
    if (guide) tools.appendChild(guide);
    tools.appendChild(button);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", build);
  else build();
})();
