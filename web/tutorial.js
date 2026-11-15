// tutorial.js - a first-use walkthrough of the Practice tab (Oleksandr's idea, Sun 15 Nov:
// "text bubbles with a cursor over them, showing what to do"). It replaces the small 4-step
// card of Sat 14 Nov. Plain JavaScript, its own file, nothing sent anywhere.
//
// How it works. Each step names a real part of the page. The page is dimmed except for that
// part (the "spotlight"), a speech bubble with a little arrow points at it, and a demo cursor
// (a drawn arrow, not the real pointer) moves to show what to do: wander around the practice
// area, go to the orange target and click it, press a switch. Because it points at the live
// page instead of screenshots, it can never be out of date, and it follows "Larger text" and
// "Easier-to-read text". The real controls stay usable while the walkthrough is open.
//
// It starts by itself on the first visit (remembered in this browser only); "How to use" in
// the top bar starts it again. Esc or "Skip" closes it; the arrow keys step through it.

(function () {
  const SEEN_KEY = "steadyPointerTutorialSeen";
  const calm = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Where the demo cursor is at time `s` (seconds into the step), inside the spotlit part.
  // Each returns {x, y} as shares of the part's width and height (0-1), plus click: true at
  // the moment it presses. `box` is the part's rectangle on screen.
  function wander(s) {                                   // a relaxed loop around the middle
    return { x: 0.5 + 0.22 * Math.sin(s * 1.3), y: 0.5 + 0.2 * Math.sin(s * 2.1 + 1) };
  }
  function goAndClick(toX, toY) {                        // glide there, click, pause, repeat
    return (s) => {
      const k = (s % 3.2) / 3.2;                         // one round every 3.2 s
      const move = Math.min(1, k / 0.55);
      const ease = 1 - (1 - move) ** 3;
      return { x: 0.5 + (toX() - 0.5) * ease, y: 0.72 + (toY() - 0.72) * ease, click: k > 0.6 && k < 0.8 };
    };
  }
  function hop(points) {                                 // visit each point in turn, clicking
    return (s) => {
      const i = Math.floor(s / 1.6) % points.length, k = (s % 1.6) / 1.6;
      const from = points[(i + points.length - 1) % points.length], to = points[i];
      const ease = 1 - (1 - Math.min(1, k / 0.5)) ** 3;
      return { x: from + (to - from) * ease, y: 0.5, click: k > 0.55 && k < 0.8 };
    };
  }
  // The orange target's place inside the practice area (app.js keeps it in `target`).
  const targetX = () => (typeof target !== "undefined" && target && area.clientWidth ? target.x / area.clientWidth : 0.7);
  const targetY = () => (typeof target !== "undefined" && target && area.clientHeight ? target.y / area.clientHeight : 0.4);

  // Step 2 is about the target, so put it where it can be seen (upper right of the area).
  function showTarget() {
    if (typeof target === "undefined" || !target) return;
    target.x = area.clientWidth * 0.72;
    target.y = Math.min(area.clientHeight * 0.3, 190);
    target.shownAt = performance.now();
  }

  const STEPS = [
    { part: "#area", title: "Move in the box", cursor: wander,
      text: "This is the practice area. Move your mouse or trackpad inside it. The dark dot is " +
            "the cursor that counts; the faint grey dot is your raw movement." },
    { part: "#area", title: "Click the orange target", cursor: goAndClick(targetX, targetY), enter: showTarget,
      text: "Press and release on the orange circle. A hit moves it somewhere new. Your hits are " +
            "counted per filter under \"Your targets\"." },
    { part: "#demo-toggle", grow: "label", title: "Switch on Demo tremor", cursor: goAndClick(() => 0.8, () => 0.5),
      text: "No tremor of your own? This adds a real tremor recording (from a public dataset) to " +
            "your movement. The grey dot then shakes; the dark dot is the corrected cursor." },
    { part: "#modes", title: "Compare the filters", cursor: hop([0.12, 0.38, 0.64, 0.88]),
      text: "Try No filter, One Euro and Our model, and see which keeps the dark dot steadier and " +
            "lets you hit more targets. A steady hand is deliberately left alone." },
    { part: ".meter-card", title: "Watch the tremor meter", cursor: null,
      text: "The bar is how tremor-like your last 2.56 seconds were. \"Shake\" shows how far the raw " +
            "and the corrected cursor wandered, in pixels. It flags tremor-like movement; it does " +
            "not diagnose anything." },
    { part: "#response-row", title: "Too slow to follow?", cursor: hop([0.18, 0.5, 0.82]),
      text: "Our model smooths the cursor, which makes it trail your hand a little. \"Balanced\" or " +
            "\"Faster\" follow quicker but shake more. Pick what feels right." },
    { part: ".topbar-tools", fallback: ".topbar", tight: true, title: "Reading help, and this guide", cursor: null,
      text: "\"Easier-to-read text\" and \"Larger text\" change how the page looks. \"How to use\" " +
            "opens this walkthrough again." },
  ];

  const style = document.createElement("style");
  style.textContent = `
    .tour-spot { position: fixed; z-index: 60; border-radius: 16px; pointer-events: none;
      box-shadow: 0 0 0 4px var(--tremor, #c2540f), 0 0 0 9999px rgba(38, 24, 12, 0.55);
      transition: left 0.3s, top 0.3s, width 0.3s, height 0.3s; }
    .tour-bubble { position: fixed; z-index: 62; width: min(360px, calc(100vw - 24px)); box-sizing: border-box;
      background: var(--surface, #fffdf8); color: var(--ink, #2f1d10); border: 2px solid var(--tremor, #c2540f);
      border-radius: 16px; padding: 14px 16px; box-shadow: 0 10px 30px rgba(47, 29, 16, 0.28);
      font-family: var(--font, system-ui, sans-serif); font-size: 16px; }
    .tour-bubble h3 { margin: 0 0 6px; font-size: 18px; }
    .tour-bubble p { margin: 0 0 12px; line-height: 1.45; }
    .tour-bubble .tour-row { display: flex; align-items: center; gap: 8px; }
    .tour-bubble .tour-count { margin-right: auto; font-size: 14px; color: var(--muted, #6a5241); }
    .tour-bubble button, .tutorial-open { font: inherit; border-radius: 999px; padding: 6px 14px; cursor: pointer;
      border: 1.5px solid var(--edge, #a8825a); background: var(--surface, #fffdf8); color: var(--ink, #2f1d10); }
    .tour-bubble button.primary { background: var(--steady, #1f6f57); border-color: var(--steady, #1f6f57); color: #fff; }
    .tour-bubble button:disabled { opacity: 0.4; cursor: default; }
    .tutorial-open { margin-left: auto; font-size: 14px; padding: 4px 12px; }
    /* The bubble's arrow: a small square turned 45 degrees, half hidden behind the bubble. */
    .tour-arrow { position: absolute; width: 16px; height: 16px; rotate: 45deg; background: var(--surface, #fffdf8);
      border: 2px solid var(--tremor, #c2540f); }
    .tour-bubble[data-side="below"] .tour-arrow { top: -10px; border-right: none; border-bottom: none; }
    .tour-bubble[data-side="above"] .tour-arrow { bottom: -10px; border-left: none; border-top: none; }
    .tour-bubble[data-side="inside"] .tour-arrow { display: none; }
    /* The demo cursor: an arrow with a "demo" tag, and a ring when it clicks. */
    .tour-cursor { position: fixed; z-index: 61; pointer-events: none; width: 26px; height: 26px; }
    .tour-cursor svg { display: block; filter: drop-shadow(0 2px 3px rgba(0, 0, 0, 0.35)); }
    .tour-cursor span { position: absolute; left: 20px; top: 20px; font: 600 12px var(--font, system-ui, sans-serif);
      background: var(--ink, #2f1d10); color: #fff; border-radius: 6px; padding: 1px 6px; }
    .tour-cursor i { position: absolute; left: -12px; top: -12px; width: 28px; height: 28px; border-radius: 50%;
      border: 3px solid var(--tremor, #c2540f); opacity: 0; scale: 0.4; transition: opacity 0.15s, scale 0.25s; }
    .tour-cursor.click i { opacity: 1; scale: 1; }`;
  document.head.appendChild(style);

  let step = -1, startedAt = 0, running = false;
  let spot = null, bubble = null, ghost = null;

  function seen() { try { return localStorage.getItem(SEEN_KEY) === "1"; } catch (e) { return false; } }
  function remember() { try { localStorage.setItem(SEEN_KEY, "1"); } catch (e) { /* private window: fine */ } }

  // The part of the page a step is about (its rectangle on screen), or null if it is not there.
  function partOf(s) {
    let el = document.querySelector(s.part) || (s.fallback && document.querySelector(s.fallback));
    if (el && s.grow) el = el.closest(s.grow) || el;          // e.g. the switch together with its label
    return el && el.getClientRects().length ? el : null;
  }

  // The rectangle around a part's children only (for a row that is wider than what is in it).
  function around(el) {
    const boxes = [...el.children].map((c) => c.getBoundingClientRect()).filter((b) => b.width > 0);
    if (!boxes.length) return el.getBoundingClientRect();
    const left = Math.min(...boxes.map((b) => b.left)), top = Math.min(...boxes.map((b) => b.top));
    const right = Math.max(...boxes.map((b) => b.right)), bottom = Math.max(...boxes.map((b) => b.bottom));
    return { left, top, right, bottom, width: right - left, height: bottom - top };
  }

  // Put the spotlight, the bubble and the demo cursor where the part is now. Runs every frame
  // while the walkthrough is open, so scrolling or resizing never leaves them behind.
  function place() {
    if (!running) return;
    const s = STEPS[step], el = partOf(s);
    if (el) {
      const r = s.tight ? around(el) : el.getBoundingClientRect(), pad = 6;
      spot.style.left = `${r.left - pad}px`; spot.style.top = `${r.top - pad}px`;
      spot.style.width = `${r.width + 2 * pad}px`; spot.style.height = `${r.height + 2 * pad}px`;

      // The bubble goes under the part, or above it, or (for a part as big as the practice
      // area) inside its lower edge. It never leaves the window.
      const bw = bubble.offsetWidth, bh = bubble.offsetHeight, gap = 18;
      let side = "below", top = r.bottom + gap;
      if (top + bh > innerHeight - 8) { side = "above"; top = r.top - gap - bh; }
      if (top < 8) { side = "inside"; top = Math.min(r.bottom, innerHeight) - bh - 16; }
      const left = Math.min(Math.max(r.left + r.width / 2 - bw / 2, 12), innerWidth - bw - 12);
      bubble.style.left = `${left}px`; bubble.style.top = `${Math.max(8, top)}px`;
      bubble.dataset.side = side;
      const arrowX = Math.min(Math.max(r.left + r.width / 2 - left - 8, 18), bw - 34);
      bubble.querySelector(".tour-arrow").style.left = `${arrowX}px`;

      ghost.hidden = !s.cursor;
      if (s.cursor) {
        const seconds = calm ? 1.9 : (performance.now() - startedAt) / 1000;   // reduced motion: hold the end pose
        const p = s.cursor(seconds);
        ghost.style.left = `${r.left + r.width * p.x}px`;
        ghost.style.top = `${r.top + r.height * p.y}px`;
        ghost.classList.toggle("click", Boolean(p.click));
      }
    }
    requestAnimationFrame(place);
  }

  function show(i) {
    if (i < 0) return;
    if (i >= STEPS.length) { close(); return; }
    while (i < STEPS.length && !partOf(STEPS[i])) i += 1;      // skip a part this page does not show
    if (i >= STEPS.length) { close(); return; }
    step = i;
    startedAt = performance.now();
    const s = STEPS[i];
    if (s.enter) s.enter();
    partOf(s).scrollIntoView({ block: "center", behavior: calm ? "auto" : "smooth" });
    bubble.querySelector("h3").textContent = s.title;
    bubble.querySelector("p").textContent = s.text;
    bubble.querySelector(".tour-count").textContent = `${i + 1} of ${STEPS.length}`;
    bubble.querySelector(".back").disabled = i === 0;
    bubble.querySelector(".primary").textContent = i === STEPS.length - 1 ? "Done" : "Next";
    for (const el of [spot, bubble]) el.hidden = false;
    if (!running) { running = true; requestAnimationFrame(place); }
  }

  function close() {
    running = false;
    step = -1;
    for (const el of [spot, bubble, ghost]) if (el) el.hidden = true;
    remember();
  }

  function start() {
    if (typeof openTab === "function") openTab("practice");      // app.js: show the Practice tab
    show(0);
  }

  function build() {
    spot = document.createElement("div");
    spot.className = "tour-spot";
    ghost = document.createElement("div");
    ghost.className = "tour-cursor";
    ghost.innerHTML = '<i></i><svg viewBox="0 0 24 24" width="26" height="26" aria-hidden="true">' +
      '<path d="M4 2 L4 19 L8.5 15 L11.5 22 L14.5 20.7 L11.6 14 L18 14 Z" fill="#fffdf8" stroke="#2f1d10" stroke-width="1.6" stroke-linejoin="round"/>' +
      "</svg><span>demo</span>";
    bubble = document.createElement("div");
    bubble.className = "tour-bubble";
    bubble.setAttribute("role", "dialog");
    bubble.setAttribute("aria-label", "How to use the practice area");
    bubble.innerHTML = '<div class="tour-arrow"></div><h3></h3><p></p><div class="tour-row">' +
      '<span class="tour-count"></span><button type="button" class="skip">Skip</button>' +
      '<button type="button" class="back">Back</button><button type="button" class="primary">Next</button></div>';
    bubble.querySelector(".skip").addEventListener("click", close);
    bubble.querySelector(".back").addEventListener("click", () => show(step - 1));
    bubble.querySelector(".primary").addEventListener("click", () => show(step + 1));
    for (const el of [spot, ghost, bubble]) { el.hidden = true; document.body.appendChild(el); }

    document.addEventListener("keydown", (event) => {
      if (!running) return;
      if (event.key === "Escape") close();
      else if (event.key === "ArrowRight") show(step + 1);
      else if (event.key === "ArrowLeft") show(step - 1);
    });

    const open = document.createElement("button");
    open.type = "button";
    open.className = "tutorial-open";
    open.textContent = "How to use";
    open.addEventListener("click", start);
    const bar = document.querySelector(".topbar");
    if (bar) bar.appendChild(open);

    if (!seen()) setTimeout(start, 600);                          // first visit: start by itself
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", build);
  else build();
})();
