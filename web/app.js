// app.js - the live demo page (step 11). Plain JavaScript, no build tools (DECISION 7).
//
// Clicks work like real buttons: a hit needs the button pressed AND released on the target.
// "Click freeze" (an idea from Timofey, a team member) holds the shown cursor still from the
// press until the release (at most 0.3 s), so tremor while the button is down cannot carry
// it off the target.
//
// "Calibrate for my mouse" (an idea from Godson, a team member): a 10 s test. Hold the cursor
// on a blue dot (4 s), then follow it slowly round a circle. The page sends the dot's position
// with every sample; the server tries each filter on this recorded test and reports how close
// each kept the cursor to the dot (server/main.py, score_calibration). It does NOT switch the
// filter: in a simulation, choosing it from one short test did worse than always using our model
// (evaluation/results/calibration_val.md).
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
const tally = {};                   // per mode (+ click freeze): {hits, misses, totalTime}
const FREEZE_MS = 300;              // click freeze never holds the cursor longer than this
let freezeOn = false;
let press = null;                   // while the button is down: {x, y, at, downInside}
const CALIB_SECONDS = 10.24;        // the test's length; the server needs at least 8 s
let calib = null;                   // during the test: {phase: "waiting"|"running"|"scoring", start, centre, radius}

// Where the corrected cursor is shown: frozen at the press position during a click freeze.
function shownPosition() {
  if (press && freezeOn && performance.now() - press.at < FREEZE_MS) return { x: press.x, y: press.y };
  return latest ? { x: latest.x, y: latest.y } : null;
}
// Where the calibration dot is, `seconds` into the test: still for 4 s, then once round a
// circle every 8 s (about 94 px/s). evaluation/calibration_sim.py uses the same path.
function calibrationDot(seconds) {
  const angle = 2 * Math.PI * Math.max(0, seconds - 4) / 8;
  return { x: calib.centre.x + calib.radius * Math.sin(angle),
           y: calib.centre.y - calib.radius * (1 - Math.cos(angle)) };
}
function onTarget(p) { return Math.hypot(p.x - target.x, p.y - target.y) <= TARGET_RADIUS; }

// ------------------------------------------------------------ server connection

function connect() {
  const protocol = location.protocol === "https:" ? "wss" : "ws";
  socket = new WebSocket(`${protocol}://${location.host}/ws/cursor`);
  socket.onopen = () => { setStatus("Connected to the local server."); sendArea(); };
  socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.type === "calibration") { showCalibration(message); return; }
    latest = message;
    updateMeter();
  };
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
    const message = { t: e.timeStamp / 1000, x: p.x, y: p.y };
    if (calib && calib.phase === "waiting") {
      const dot = calibrationDot(0);
      if (Math.hypot(p.x - dot.x, p.y - dot.y) <= 20) {      // the hand reached the dot: start
        send({ type: "calibrate_start" });
        calib.phase = "running";
        calib.start = e.timeStamp;
      }
    }
    if (calib && calib.phase === "running") {
      const dot = calibrationDot((e.timeStamp - calib.start) / 1000);
      message.dot_x = dot.x;
      message.dot_y = dot.y;
    }
    send(message);
  }
});
area.addEventListener("pointerleave", () => {
  inside = false;
  if (calib && calib.phase !== "scoring") {                 // left the area: the test is void
    if (calib.phase === "running") send({ type: "calibrate_cancel" });
    calib = null;
    showCalibrationText("Calibration stopped: keep the pointer inside the practice area. Try again.");
  }
});
// Coming back into the area (maybe somewhere else): start the filter afresh, so the
// cursor never jumps across from where the pointer left.
area.addEventListener("pointerenter", () => send({ type: "reset" }));

// The server needs the practice area's size so "Lower sensitivity" stays inside it.
function sendArea() { send({ type: "area", width: area.clientWidth, height: area.clientHeight }); }

area.addEventListener("pointerdown", (event) => {
  if (!latest || !target || calib) return;
  try { area.setPointerCapture(event.pointerId); } catch (error) { /* not essential */ }  // see the release even off the area
  press = { x: latest.x, y: latest.y, at: performance.now(), downInside: onTarget(latest) };
});

area.addEventListener("pointerup", () => {
  if (!press || !target) return;
  const released = shownPosition();               // frozen position, if the freeze is on
  const hit = press.downInside && onTarget(released);
  press = null;
  const key = settings.mode + (freezeOn ? "+freeze" : "");
  const row = tally[key] ??= { hits: 0, misses: 0, totalTime: 0 };
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
    const [name, freeze] = mode.split("+");
    tr.innerHTML = `<td>${MODE_NAMES[name]}${freeze ? " + click freeze" : ""}</td><td>${row.hits}</td><td>${row.misses}</td><td>${time}</td>`;
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
  // How much of our model's correction is being applied right now (the detector's gate).
  const correcting = document.getElementById("correcting-word");
  if (latest.mode !== "learned") {
    correcting.textContent = "our model is not selected";
    correcting.classList.remove("on");
  } else {
    const g = latest.gate ?? 0;
    correcting.textContent = g > 0.5 ? `ON (${Math.round(g * 100)}%)` : g > 0.05 ? `partly (${Math.round(g * 100)}%)` : "off - no tremor-like movement";
    correcting.classList.toggle("on", g > 0.5);
  }
  document.getElementById("freq").textContent = latest.tremor ? latest.frequency_hz.toFixed(1) : "-";
  document.getElementById("size").textContent = latest.size_px.toFixed(1);
  const demo = latest.demo;
  document.getElementById("demo-source").textContent = demo
    ? `(Now: ${demo.level} tremor of a test-set person with ${demo.condition}, about ${demo.strength_px} px.)` : "";
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
  document.getElementById("demo-levels").hidden = !settings.demo_tremor;
  document.getElementById("demo-tip").hidden = settings.demo_tremor;
  for (const button of document.querySelectorAll("#demo-levels button")) {
    button.classList.toggle("on", button.dataset.level === settings.demo_level);
  }
  document.getElementById("legend-demo").hidden = !settings.demo_tremor;
  const trackButton = document.getElementById("tracking-toggle");
  trackButton.textContent = `Whole-laptop tracking: ${settings.tracking ? "on" : "off"}`;
  trackButton.classList.toggle("on", settings.tracking);
}

for (const button of document.querySelectorAll("#modes button")) {
  button.addEventListener("click", () => postSettings({ mode: button.dataset.mode }));
}
for (const button of document.querySelectorAll("#demo-levels button")) {
  button.addEventListener("click", () => postSettings({ demo_level: button.dataset.level }));
}
document.getElementById("strength").addEventListener("change", (e) => postSettings({ strength: Number(e.target.value) }));
document.getElementById("strength").addEventListener("input", (e) => {
  document.getElementById("strength-value").textContent = Number(e.target.value).toFixed(1);
});
document.getElementById("demo-toggle").addEventListener("click", () => postSettings({ demo_tremor: !settings.demo_tremor }));
document.getElementById("freeze-toggle").addEventListener("click", (event) => {
  freezeOn = !freezeOn;
  event.target.textContent = `Click freeze: ${freezeOn ? "on" : "off"}`;
  event.target.classList.toggle("on", freezeOn);
});
document.getElementById("tracking-toggle").addEventListener("click", () => postSettings({ tracking: !settings.tracking }));
document.getElementById("reset").addEventListener("click", async () => {
  await fetch("/api/reset", { method: "POST" });
  for (const key of Object.keys(tally)) delete tally[key];
  showTally();
  send({ type: "reset" });
  newTarget();
});

// ------------------------------------------------------------ calibration test

document.getElementById("calibrate").addEventListener("click", () => {
  const radius = Math.min(120, area.clientWidth / 2 - 30, area.clientHeight / 2 - 30);
  calib = { phase: "waiting", start: null, radius,
            centre: { x: area.clientWidth / 2, y: area.clientHeight / 2 + radius } };
  showCalibrationText("Move your cursor onto the blue dot and hold it there. Then follow the dot.");
});

function showCalibrationText(text) {
  const line = document.getElementById("calib-result");
  line.hidden = false;
  line.textContent = text;
}

function showCalibration(result) {
  calib = null;
  if (!result.ok) { showCalibrationText(result.message); return; }
  const others = result.distances.map((d) => `${d.name} ${d.px.toFixed(1)} px`).join(" · ");
  const shake = result.size_px === null ? "" :
    ` Shaking during the test: about ${result.size_px.toFixed(1)} px` +
    (result.tremor_share > 0 ? `, tremor-like ${Math.round(result.tremor_share * 100)}% of the time at about ${result.frequency_hz.toFixed(1)} Hz.` : ", not tremor-like.");
  showCalibrationText(`On your test, average distance from the dot: ${others} (closest: ${result.chosen}). ` +
    `Your device sent ${result.samples_per_second} samples per second.${shake} ` +
    "The filter is not changed automatically: one short test is not enough to choose well. " +
    "Kept only until the server stops; not a diagnosis.");
}

// ------------------------------------------------------------ drawing

function resizeCanvas() {
  // Draw sharply on high-resolution (Retina) screens.
  const ratio = window.devicePixelRatio || 1;
  area.width = area.clientWidth * ratio;
  area.height = area.clientHeight * ratio;
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  if (!target) newTarget();
  sendArea();
}

function circle(x, y, r, fill) {
  ctx.beginPath();
  ctx.arc(x, y, r, 0, 2 * Math.PI);
  ctx.fillStyle = fill;
  ctx.fill();
}

function draw() {
  ctx.clearRect(0, 0, area.clientWidth, area.clientHeight);
  if (calib && calib.phase === "running" && (performance.now() - calib.start) / 1000 >= CALIB_SECONDS) {
    calib.phase = "scoring";
    send({ type: "calibrate_end" });
    showCalibrationText("Trying each filter on your test...");
  }
  if (calib && calib.phase !== "scoring") {
    const dot = calibrationDot(calib.phase === "running" ? (performance.now() - calib.start) / 1000 : 0);
    circle(dot.x, dot.y, 14, "#2f6db5");
    circle(dot.x, dot.y, 4, "#fffdf9");
  } else if (target) {
    circle(target.x, target.y, TARGET_RADIUS, "#d9661a");
    circle(target.x, target.y, 5, "#fffdf9");
  }
  if (inside && latest) {
    const shown = shownPosition();
    circle(latest.raw_x, latest.raw_y, 9, "rgba(110, 110, 110, 0.45)");   // raw: faint grey
    circle(shown.x, shown.y, 8, "#3b2314");                                // corrected: solid
    circle(shown.x, shown.y, 3, "#fffdf9");
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
