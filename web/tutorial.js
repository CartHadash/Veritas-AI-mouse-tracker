// tutorial.js - a short first-use guide for the Practice tab (Oleksandr's request, Sat 14 Nov:
// "when I first see the orange target I don't know what to do"). Plain JavaScript, its own
// file so it does not clash with app.js. It shows once (remembered in this browser only) and
// the "How to use" button in the top bar brings it back. Each step outlines the part it is
// about. Nothing is sent anywhere.

(function () {
  const SEEN_KEY = "steadyPointerTutorialSeen";
  const STEPS = [
    { part: "#area", title: "1. Move in the box",
      text: "Move your mouse or trackpad inside the box. The dark dot is the cursor that counts; " +
            "the faint grey dot is your raw movement." },
    { part: "#area", title: "2. Click the orange target",
      text: "Press and release on the orange circle. A hit moves it somewhere new, and your hits " +
            "are counted per filter under \"Your targets\"." },
    { part: "#demo-toggle", title: "3. Switch on Demo tremor",
      text: "It adds a real tremor recording (from a public dataset) to your movement. The grey dot " +
            "now shakes; the dark dot is our correction. \"Shake\" in the tremor meter shows both " +
            "in pixels: raw -> corrected." },
    { part: "#modes", title: "4. Compare the filters",
      text: "Switch between No filter, One Euro and Our model, and see which keeps the dark dot " +
            "steadier and lets you hit more targets. A steady hand is deliberately left alone. " +
            "If Our model feels slow to follow, try \"Balanced\" or \"Faster\" under Adjust." },
  ];

  const style = document.createElement("style");
  style.textContent = `
    .tutorial-card { position: fixed; left: 16px; bottom: 16px; z-index: 50; max-width: 360px;
      background: var(--surface, #fffdf8); color: var(--ink, #2f1d10); border: 2px solid var(--tremor, #c2540f);
      border-radius: 16px; padding: 14px 16px; box-shadow: 0 8px 28px rgba(47, 29, 16, 0.18); font-size: 16px; }
    .tutorial-card h3 { margin: 0 0 6px; font-size: 18px; }
    .tutorial-card p { margin: 0 0 12px; line-height: 1.45; }
    .tutorial-card .tutorial-buttons { display: flex; gap: 8px; justify-content: flex-end; }
    .tutorial-card button, .tutorial-open { font: inherit; border-radius: 999px; padding: 6px 14px; cursor: pointer;
      border: 1.5px solid var(--edge, #a8825a); background: var(--surface, #fffdf8); color: var(--ink, #2f1d10); }
    .tutorial-card button.primary { background: var(--steady, #1f6f57); border-color: var(--steady, #1f6f57); color: #fff; }
    .tutorial-open { margin-left: auto; font-size: 14px; padding: 4px 12px; }
    .tutorial-focus { outline: 4px solid var(--tremor, #c2540f); outline-offset: 5px; border-radius: 12px; }
    @media (max-width: 500px) { .tutorial-card { left: 8px; right: 8px; max-width: none; } }`;
  document.head.appendChild(style);

  let step = -1;
  let card = null;

  function seen() { try { return localStorage.getItem(SEEN_KEY) === "1"; } catch (e) { return false; } }
  function remember() { try { localStorage.setItem(SEEN_KEY, "1"); } catch (e) { /* private window: fine */ } }

  function clearFocus() {
    for (const el of document.querySelectorAll(".tutorial-focus")) el.classList.remove("tutorial-focus");
  }

  function show(i) {
    clearFocus();
    step = i;
    if (i >= STEPS.length) { close(); return; }
    const s = STEPS[i];
    const part = document.querySelector(s.part);
    if (part) {
      part.classList.add("tutorial-focus");
      part.scrollIntoView({ block: "center", behavior: "smooth" });
    }
    card.querySelector("h3").textContent = s.title;
    card.querySelector("p").textContent = s.text;
    card.querySelector(".primary").textContent = i === STEPS.length - 1 ? "Done" : "Next";
    card.hidden = false;
  }

  function close() {
    clearFocus();
    if (card) card.hidden = true;
    remember();
  }

  function start() {
    if (typeof openTab === "function") openTab("practice");      // app.js: show the Practice tab
    show(0);
  }

  function build() {
    card = document.createElement("div");
    card.className = "tutorial-card";
    card.setAttribute("role", "dialog");
    card.setAttribute("aria-label", "How to use the practice area");
    card.hidden = true;
    card.innerHTML = '<h3></h3><p></p><div class="tutorial-buttons">' +
      '<button type="button" class="skip">Skip</button><button type="button" class="primary">Next</button></div>';
    card.querySelector(".skip").addEventListener("click", close);
    card.querySelector(".primary").addEventListener("click", () => show(step + 1));
    document.body.appendChild(card);

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
