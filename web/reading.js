// reading.js - two reading switches in the top bar: "Easier-to-read text" and "Larger text"
// (Oleksandr's accessibility idea; the team leader agreed, Sun 15 Nov). Plain JavaScript in
// its own file, like tutorial.js.
//
// "Larger text" enlarges everything around the practice area by 15% (the CSS "zoom" property
// on the top bar, the side cards and the other tabs). The practice area itself is left alone,
// so the cursor and targets keep their real size and position.
//
// "Easier-to-read text": switches the whole page to OpenDyslexic, a free font designed for
// readers with dyslexia (heavier bottoms on the letters, so they are harder to mix up), with a
// little more space between words and lines, as the British Dyslexia Association's style
// guide recommends. Some readers with dyslexia find such text easier; it is a reading
// preference, not a treatment. The two font files are in web/fonts/ (SIL Open Font License,
// web/fonts/OPENDYSLEXIC_LICENSE.txt), so the page still works without internet; they are only
// loaded when the switch is on. If they cannot load, Verdana is used instead. The choice is
// remembered in this browser only. Text drawn inside the practice area keeps its font.

(function () {
  const SWITCHES = [
    { key: "steadyPointerEasyRead", className: "easy-read", text: "Easier-to-read text",
      title: "The OpenDyslexic font with wider spacing (often easier to read with dyslexia)" },
    { key: "steadyPointerLargeText", className: "large-text", text: "Larger text",
      title: "Makes the text and controls 15% larger" },
  ];

  const style = document.createElement("style");
  style.textContent = `
    /* size-adjust: OpenDyslexic's letters are much wider than the page's usual font, so they
       are drawn a little smaller to fit the same boxes and buttons. */
    @font-face { font-family: "OpenDyslexic"; font-weight: 400; font-display: swap; size-adjust: 84%;
      src: url("fonts/opendyslexic-400.woff2") format("woff2"); }
    @font-face { font-family: "OpenDyslexic"; font-weight: 700; font-display: swap; size-adjust: 84%;
      src: url("fonts/opendyslexic-700.woff2") format("woff2"); }
    :root.easy-read { --font: "OpenDyslexic", Verdana, Tahoma, "DejaVu Sans", Arial, sans-serif; }
    /* OpenDyslexic's letters are already wide and well apart: only words and lines get more room. */
    :root.easy-read body { word-spacing: 0.1em; line-height: 1.6; }
    :root.easy-read p, :root.easy-read li, :root.easy-read small { line-height: 1.6; }
    /* Rows of buttons have a fixed width: keep their spacing normal and the text a little
       smaller, so the wider font still fits (checked at phone and laptop widths). */
    :root.easy-read ui-segmented-control-item, :root.easy-read ui-tabs-tab button {
      letter-spacing: 0; word-spacing: 0; font-size: 0.82em; }
    @media (max-width: 700px) {                 /* a phone-width window: tighter still */
      :root.easy-read ui-segmented-control-item, :root.easy-read ui-tabs-tab button { font-size: 0.72em; }
      :root.easy-read .page, :root.easy-read .rail { overflow-wrap: anywhere; }
    }
    /* Only on laptop-sized windows: on a phone-width window there is no room to enlarge. */
    @media (min-width: 701px) {
      :root.large-text .topbar, :root.large-text .stage-bar, :root.large-text .mode-hint,
      :root.large-text .stage .banner, :root.large-text .legend, :root.large-text .rail,
      :root.large-text .page { zoom: 1.15; }
    }
    .topbar-tools { grid-column: 1 / -1; display: flex; flex-wrap: wrap; gap: 8px; justify-content: flex-end; }
    .topbar-tools .tutorial-open { margin-left: 0; }
    .easy-read-toggle { font: inherit; font-size: 14px; border-radius: 999px; padding: 4px 12px; cursor: pointer;
      border: 1.5px solid var(--edge, #a8825a); background: var(--surface, #fffdf8); color: var(--ink, #2f1d10); }
    .easy-read-toggle[aria-pressed="true"] { background: var(--steady, #1f6f57); border-color: var(--steady, #1f6f57); color: #fff; }`;
  document.head.appendChild(style);

  function saved(sw) { try { return localStorage.getItem(sw.key) === "1"; } catch (e) { return false; } }
  function save(sw, on) { try { localStorage.setItem(sw.key, on ? "1" : "0"); } catch (e) { /* private window: fine */ } }

  // As early as possible, so the page does not flicker.
  for (const sw of SWITCHES) document.documentElement.classList.toggle(sw.className, saved(sw));

  function build() {
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
    for (const sw of SWITCHES) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "easy-read-toggle";
      button.textContent = sw.text;
      button.title = sw.title;
      button.setAttribute("aria-pressed", String(saved(sw)));
      button.addEventListener("click", () => {
        const on = !document.documentElement.classList.contains(sw.className);
        document.documentElement.classList.toggle(sw.className, on);
        button.setAttribute("aria-pressed", String(on));
        save(sw, on);
      });
      tools.appendChild(button);
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", build);
  else build();
})();
