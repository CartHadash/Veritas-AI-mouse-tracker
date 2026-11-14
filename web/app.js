// app.js - the live demo page (step 11). Plain JavaScript, no build tools (DECISION 7).
//
// What happens:
//  1. Inside the practice area the system cursor is hidden. Every pointer movement is sent
//     to the local server over a WebSocket (/ws/cursor) as {t, x, y}.
//  2. The server replies with the raw position (plus replayed tremor in demo mode), the
//     corrected position, and the detector's tremor score, size and frequency.
//  3. We draw both cursors and update the tremor meter. Clicks count where the CORRECTED
//     cursor is, so the tally shows whether correction helps to hit targets.

const area = document.getElementById("area");
const ctx = area.getContext("2d");
const MODE_NAMES = { none: "No filter", low_sensitivity: "Lower sensitivity", one_euro: "One Euro", learned: "Our model" };
const TARGET_RADIUS = 22;           // px; small on purpose, so a shaky cursor finds it hard

let socket = null;
let latest = null;                  // last reply from the server
let inside = false;                 // is the pointer inside the practice area?
let settings = { mode: "learned", strength: 1, demo_tremor: false, tracking: false };
let threshold = 0.165;
let target = null;                  // {x, y, shownAt}
const tally = {};                   // per mode: {hits, misses, totalTime}

// ------------------------------------------------------------ server connection

function connect() {
  const protocol = location.protocol === "https:" ? "wss" : "ws";
  socket = new WebSocket(`${protocol}://${location.host}/ws/cursor`);
  socket.onopen = () => setStatus("Connected to the local server.");
  socket.onmessage = (event) => { latest = JSON.parse(event.data); updateMeter(); };
  socket.onclose = () => { setStatus("Connection lost - retrying..."); setTimeout(connect, 1000); };
}

function send(message) {
  if (socket && socket.readyState === WebSocket.OPEN) socket.send(JSON.stringify(message));
}

async function postSettings(change) {
  const response = await fetch("/api/settings", {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(change) });
  settings = await response.json();
  showSettings();
}

async function loadStatus() {
  const status = await (await fetch("/api/status")).json();
  threshold = status.detector_threshold ?? threshold;
  document.getElementById("cutoff-mark").style.left = `${threshold * 100}%`;
  const parts = [`tracker: ${status.tracker}`, `assistant: ${status.assistant}`];
  setStatus(document.getElementById("status-line").textContent + " " + parts.join(" · "));
  // The tracking button only appears when the leader's tracker can run on this computer.
  document.getElementById("tracking-toggle").hidden = !String(status.tracker).startsWith("available")
    && !String(status.tracker).startsWith("running");
  settings = await (await fetch("/api/settings")).json();
  showSettings();
}

function setStatus(text) { document.getElementById("status-line").textContent = text; }

// ------------------------------------------------------------ pointer input

function areaPosition(event) {
  const box = area.getBoundingClientRect();
  return { x: event.clientX - box.left, y: event.clientY - box.top };
}

area.addEventListener("pointermove", (event) => {
  inside = true;
  // Browsers may bundle several movements into one event; send each of them.
  const events = event.getCoalescedEvents ? event.getCoalescedEvents() : [event];
  for (const e of (events.length ? events : [event])) {
    const p = areaPosition(e);
    send({ t: e.timeStamp / 1000, x: p.x, y: p.y });
  }
});
area.addEventListener("pointerleave", () => { inside = false; });

area.addEventListener("pointerdown", () => {
  if (!latest || !target) return;
  const hit = Math.hypot(latest.x - target.x, latest.y - target.y) <= TARGET_RADIUS;
  const row = tally[settings.mode] ??= { hits: 0, misses: 0, totalTime: 0 };
  if (hit) {
    row.hits += 1;
    row.totalTime += (performance.now() - target.shownAt) / 1000;
    newTarget();
  } else {
    row.misses += 1;
  }
  send({ type: "click", hit });
  showTally();
});

// ------------------------------------------------------------ targets and tally

function newTarget() {
  const margin = 50;
  target = {
    x: margin + Math.random() * (area.clientWidth - 2 * margin),
    y: margin + Math.random() * (area.clientHeight - 2 * margin),
    shownAt: performance.now(),
  };
}

function showTally() {
  const body = document.querySelector("#tally tbody");
  body.innerHTML = "";
  for (const [mode, row] of Object.entries(tally)) {
    const time = row.hits ? (row.totalTime / row.hits).toFixed(1) + " s" : "-";
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${MODE_NAMES[mode]}</td><td>${row.hits}</td><td>${row.misses}</td><td>${time}</td>`;
    body.appendChild(tr);
  }
}

// ------------------------------------------------------------ meter and settings display

function updateMeter() {
  if (!latest) return;
  const word = document.getElementById("tremor-word");
  if (latest.score === null) {
    word.textContent = "Collecting 2.56 s of movement...";
    return;
  }
  word.textContent = latest.tremor ? "Tremor-like movement detected" : "No tremor-like movement";
  const bar = document.getElementById("score-bar");
  bar.style.width = `${Math.round(latest.score * 100)}%`;
  bar.classList.toggle("tremor", latest.tremor);
  document.getElementById("score").textContent = latest.score.toFixed(2);
  document.getElementById("freq").textContent = latest.tremor ? latest.frequency_hz.toFixed(1) : "-";
  document.getElementById("size").textContent = latest.size_px.toFixed(1);
  const demo = latest.demo;
  document.getElementById("demo-source").textContent = demo
    ? `(Now: a test-set person with ${demo.condition}, about ${demo.strength_px} px.)` : "";
}

function showSettings() {
  for (const button of document.querySelectorAll("#modes button")) {
    button.classList.toggle("on", button.dataset.mode === settings.mode);
  }
  document.getElementById("strength").value = settings.strength;
  document.getElementById("strength-value").textContent = Number(settings.strength).toFixed(1);
  const demoButton = document.getElementById("demo-toggle");
  demoButton.textContent = `Demo tremor: ${settings.demo_tremor ? "on" : "off"}`;
  demoButton.classList.toggle("on", settings.demo_tremor);
  document.getElementById("demo-banner").hidden = !settings.demo_tremor;
  document.getElementById("legend-demo").hidden = !settings.demo_tremor;
  const trackButton = document.getElementById("tracking-toggle");
  trackButton.textContent = `Whole-laptop tracking: ${settings.tracking ? "on" : "off"}`;
  trackButton.classList.toggle("on", settings.tracking);
}

for (const button of document.querySelectorAll("#modes button")) {
  button.addEventListener("click", () => postSettings({ mode: button.dataset.mode }));
}
document.getElementById("strength").addEventListener("change", (e) => postSettings({ strength: Number(e.target.value) }));
document.getElementById("strength").addEventListener("input", (e) => {
  document.getElementById("strength-value").textContent = Number(e.target.value).toFixed(1);
});
document.getElementById("demo-toggle").addEventListener("click", () => postSettings({ demo_tremor: !settings.demo_tremor }));
document.getElementById("tracking-toggle").addEventListener("click", () => postSettings({ tracking: !settings.tracking }));
document.getElementById("reset").addEventListener("click", async () => {
  await fetch("/api/reset", { method: "POST" });
  for (const key of Object.keys(tally)) delete tally[key];
  showTally();
  send({ type: "reset" });
  newTarget();
});

// ------------------------------------------------------------ drawing

function resizeCanvas() {
  // Draw sharply on high-resolution (Retina) screens.
  const ratio = window.devicePixelRatio || 1;
  area.width = area.clientWidth * ratio;
  area.height = area.clientHeight * ratio;
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  if (!target) newTarget();
}

function circle(x, y, r, fill) {
  ctx.beginPath();
  ctx.arc(x, y, r, 0, 2 * Math.PI);
  ctx.fillStyle = fill;
  ctx.fill();
}

function draw() {
  ctx.clearRect(0, 0, area.clientWidth, area.clientHeight);
  if (target) {
    circle(target.x, target.y, TARGET_RADIUS, "#d9661a");
    circle(target.x, target.y, 5, "#fffdf9");
  }
  if (inside && latest) {
    circle(latest.raw_x, latest.raw_y, 9, "rgba(110, 110, 110, 0.45)");   // raw: faint grey
    circle(latest.x, latest.y, 8, "#3b2314");                              // corrected: solid
    circle(latest.x, latest.y, 3, "#fffdf9");
  } else {
    ctx.fillStyle = "#6e5444";
    ctx.font = "20px system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("Move your mouse or trackpad in here", area.clientWidth / 2, area.clientHeight / 2);
  }
  requestAnimationFrame(draw);
}

// ------------------------------------------------------------ the assistant panel (leader's lane)

async function loadAssistant() {
  try {
    const check = await fetch("assistant/assistant.js", { method: "HEAD" });
    if (!check.ok) return;
    const script = document.createElement("script");
    script.src = "assistant/assistant.js";
    document.body.appendChild(script);
  } catch (error) { /* no assistant: fine */ }
}

async function hideSummaryLinkIfMissing() {
  try {
    const check = await fetch("summary.html", { method: "HEAD" });
    if (!check.ok) document.querySelector('a[href="summary.html"]').hidden = true;
  } catch (error) { document.querySelector('a[href="summary.html"]').hidden = true; }
}

window.addEventListener("resize", resizeCanvas);
resizeCanvas();
connect();
loadStatus();
loadAssistant();
hideSummaryLinkIfMissing();
requestAnimationFrame(draw);
