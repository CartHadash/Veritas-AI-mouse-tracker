// app.js - the live demo page (step 11). Plain JavaScript, no build tools (DECISION 7).
//
// The controls (tabs, filter choice, switches, slider, meter, assistant window) are ui-sdk web
// components: custom HTML tags such as <ui-switch>. They tell us about a change with an event
// (for example "checkedchange") whose new value is in event.detail.value.
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
// "Lower sensitivity" uses Pointer Lock: the browser holds the real pointer still and reports
// only how far the hand moved, so the drawn cursor (half the hand's movement) is the only
// cursor and can reach every part of the area. Esc or another filter releases it.
let locked = false;
let lockFailed = false;             // the browser refused: fall back to normal pointer input
let hand = null;                    // while locked: the hand's position, added up from its movement
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

// The last moments of movement, drawn as two fading lines behind the cursors: where the hand
// went (raw) and where the corrected cursor went. Only real positions from the server.
const TRAIL_MS = 700;               // how much of the past the lines show
let trail = [];                     // [{at, rawX, rawY, x, y}, ...], oldest first

// Set a ui-sdk component's state from code. Once the component's code has loaded we set its
// property; before that we write the HTML attribute, which it reads when it starts up.
// Neither fires a change event, so the page never reacts to its own update.
function setControl(element, name, value) {
  if (customElements.get(element.localName)) element[name] = value;
  else if (typeof value === "boolean") element.toggleAttribute(name, value);
  else element.setAttribute(name, value);
}

// ------------------------------------------------------------ server connection

function connect() {
  const protocol = location.protocol === "https:" ? "wss" : "ws";
  socket = new WebSocket(`${protocol}://${location.host}/ws/cursor`);
  socket.onopen = () => { setStatus("Connected to the local server."); setConnected(true); sendArea(); };
  socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.type === "calibration") { showCalibration(message); return; }
    latest = message;
    if (inside) {
      trail.push({ at: performance.now(), rawX: message.raw_x, rawY: message.raw_y, x: message.x, y: message.y });
      if (trail.length > 400) trail.shift();          // never grows without limit
    }
    updateMeter();
  };
  socket.onclose = () => { setStatus("Connection lost - retrying..."); setConnected(false); setTimeout(connect, 1000); };
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
  setStatus(statusText + " " + parts.join(", "));
  // The tracking button only appears when the leader's tracker can run on this computer.
  document.getElementById("tracking-row").hidden = !String(status.tracker).startsWith("available")
    && !String(status.tracker).startsWith("running");
  settings = await (await fetch("/api/settings")).json();
  showSettings();
}

// The header shows a short word; the full status text is its tooltip.
let statusText = "";
function setStatus(text) {
  statusText = text;
  document.getElementById("status-line").title = text;
}
function setConnected(on) {
  const line = document.getElementById("status-line");
  line.textContent = on ? "Connected" : "Reconnecting...";
  line.classList.toggle("off", !on);
}

// ------------------------------------------------------------ pointer input

function areaPosition(event) {
  const box = area.getBoundingClientRect();
  return { x: event.clientX - box.left, y: event.clientY - box.top };
}

area.addEventListener("pointermove", (event) => {
  inside = true;
  let samples;
  if (locked) {
    // Pointer Lock: the real pointer does not move; add up the hand's movement instead.
    hand.x += event.movementX;
    hand.y += event.movementY;
    samples = [{ p: { x: hand.x, y: hand.y }, timeStamp: event.timeStamp }];
  } else {
    // Browsers may bundle several movements into one event; send each of them.
    const events = event.getCoalescedEvents ? event.getCoalescedEvents() : [event];
    samples = (events.length ? events : [event]).map((e) => ({ p: areaPosition(e), timeStamp: e.timeStamp }));
  }
  for (const e of samples) {
    const p = e.p;
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
  trail = [];
  if (calib && calib.phase !== "scoring") {                 // left the area: the test is void
    if (calib.phase === "running") send({ type: "calibrate_cancel" });
    calib = null;
    showCalibrationText("Calibration stopped: keep the pointer inside the practice area. Try again.");
  }
});
// Coming back into the area (maybe somewhere else): start the filter afresh, so the
// cursor never jumps across from where the pointer left.
area.addEventListener("pointerenter", () => { trail = []; send({ type: "reset" }); });

document.addEventListener("pointerlockchange", () => {
  locked = document.pointerLockElement === area;
  inside = locked;
  trail = [];
  send({ type: "reset" });                // start the filter afresh where the pointer is
});
document.addEventListener("pointerlockerror", () => {
  lockFailed = true;
  setStatus("This browser would not lock the pointer; Lower sensitivity uses the normal pointer.");
});

// The server needs the practice area's size so "Lower sensitivity" stays inside it.
function sendArea() { send({ type: "area", width: area.clientWidth, height: area.clientHeight }); }

area.addEventListener("pointerdown", (event) => {
  if (settings.mode === "low_sensitivity" && !locked && !lockFailed && area.requestPointerLock) {
    hand = areaPosition(event);           // start where the pointer is now
    area.requestPointerLock();            // this click only starts the mode; it is not a target click
    return;
  }
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
  const empty = Object.keys(tally).length === 0;
  document.getElementById("tally").hidden = empty;
  document.getElementById("tally-empty").hidden = !empty;
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
  const meter = document.getElementById("score-meter");
  setControl(meter, "value", latest.score);
  meter.classList.toggle("tremor", latest.tremor);
  word.classList.toggle("tremor", latest.tremor);
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
  if (locked && settings.mode !== "low_sensitivity") document.exitPointerLock();
  setControl(document.getElementById("modes"), "value", settings.mode);
  setControl(document.getElementById("strength"), "value", Number(settings.strength));
  setControl(document.getElementById("demo-toggle"), "checked", Boolean(settings.demo_tremor));
  setControl(document.getElementById("tracking-toggle"), "checked", Boolean(settings.tracking));
  if (settings.demo_level) setControl(document.getElementById("demo-levels"), "value", settings.demo_level);
  document.getElementById("demo-banner").hidden = !settings.demo_tremor;
  document.getElementById("demo-levels-row").hidden = !settings.demo_tremor;
  document.getElementById("demo-tip").hidden = settings.demo_tremor;
  document.getElementById("legend-demo").hidden = !settings.demo_tremor;
}

// Each control reports a change the person made; we send it to the server, which answers
// with the settings now in force (showSettings then shows them).
document.getElementById("modes").addEventListener("valuechange", (e) => postSettings({ mode: e.detail.value }));
document.getElementById("demo-levels").addEventListener("valuechange", (e) => postSettings({ demo_level: e.detail.value }));
// "valuecommit" fires once when the slider is let go, so we save once, not on every step.
document.getElementById("strength").addEventListener("valuecommit", (e) => postSettings({ strength: Number(e.detail.value) }));
document.getElementById("demo-toggle").addEventListener("checkedchange", (e) => postSettings({ demo_tremor: e.detail.value }));
document.getElementById("freeze-toggle").addEventListener("checkedchange", (e) => { freezeOn = e.detail.value; });
document.getElementById("tracking-toggle").addEventListener("checkedchange", (e) => postSettings({ tracking: e.detail.value }));
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
  if (area.clientWidth === 0) return;      // the Practice tab is hidden: nothing to measure
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

// Colours used on the canvas (the same warm palette as styles.css).
const INK = "#2f1d10", MUTED = "#6a5241", PAPER = "#fffdf8", TARGET = "#d9661a", CALIB = "#2f6db5";

// Draw one of the two trail lines. Each short piece is fainter the older it is.
function drawTrail(xKey, yKey, rgb, width, now) {
  ctx.lineWidth = width;
  ctx.lineCap = "round";
  for (let i = 1; i < trail.length; i++) {
    const age = (now - trail[i].at) / TRAIL_MS;            // 0 = just now, 1 = about to vanish
    ctx.strokeStyle = `rgba(${rgb}, ${(1 - age).toFixed(2)})`;
    ctx.beginPath();
    ctx.moveTo(trail[i - 1][xKey], trail[i - 1][yKey]);
    ctx.lineTo(trail[i][xKey], trail[i][yKey]);
    ctx.stroke();
  }
}

function draw() {
  const now = performance.now();
  ctx.clearRect(0, 0, area.clientWidth, area.clientHeight);
  if (calib && calib.phase === "running" && (now - calib.start) / 1000 >= CALIB_SECONDS) {
    calib.phase = "scoring";
    send({ type: "calibrate_end" });
    showCalibrationText("Trying each filter on your test...");
  }
  if (calib && calib.phase !== "scoring") {
    const dot = calibrationDot(calib.phase === "running" ? (now - calib.start) / 1000 : 0);
    circle(dot.x, dot.y, 14, CALIB);
    circle(dot.x, dot.y, 4, PAPER);
  } else if (target) {
    circle(target.x, target.y, TARGET_RADIUS + 7, "rgba(217, 102, 26, 0.16)");   // soft halo
    circle(target.x, target.y, TARGET_RADIUS, TARGET);
    circle(target.x, target.y, 5, PAPER);
  }
  if (settings.mode === "low_sensitivity" && !locked && !lockFailed) {
    ctx.fillStyle = MUTED;
    ctx.font = '600 17px "Avenir Next", "Segoe UI", system-ui, sans-serif';
    ctx.textAlign = "center";
    ctx.fillText("Lower sensitivity: click here to start (Esc to stop)", area.clientWidth / 2, 34);
  }
  if (inside && latest) {
    // Forget trail points older than TRAIL_MS, then draw the two lines.
    while (trail.length && now - trail[0].at > TRAIL_MS) trail.shift();
    // Raw: faint grey. Hidden under Pointer Lock, where the hand's position can be off the area.
    if (!locked) drawTrail("rawX", "rawY", "120, 108, 98", 2, now);
    drawTrail("x", "y", "31, 111, 87", 3.5, now);                        // corrected: green
    const shown = shownPosition();
    if (!locked) circle(latest.raw_x, latest.raw_y, 9, "rgba(120, 108, 98, 0.45)");
    circle(shown.x, shown.y, 9, INK);                                      // corrected: solid
    circle(shown.x, shown.y, 3.5, PAPER);
  } else {
    ctx.fillStyle = MUTED;
    ctx.font = '500 21px "Avenir Next", "Segoe UI", system-ui, sans-serif';
    ctx.textAlign = "center";
    // A shorter invitation when the area is too narrow for the long one (a phone).
    const invite = area.clientWidth < 440 ? "Move in here" : "Move your mouse or trackpad in here";
    ctx.fillText(invite, area.clientWidth / 2, area.clientHeight / 2);
  }
  requestAnimationFrame(draw);
}

// ------------------------------------------------------------ tabs

const tabs = document.getElementById("tabs");
const TAB_NAMES = ["practice", "analysis", "how"];

// Runs whenever a tab is shown. The Analysis numbers are fetched fresh each time.
// (The practice area re-measures itself: see the ResizeObserver below.)
function tabShown(name) {
  history.replaceState(null, "", "#" + name);       // so a reload or a link opens the same tab
  if (name === "analysis") loadSummary();
}
tabs.addEventListener("valuechange", (e) => tabShown(e.detail.value));

// Open a tab from code: the "See the analysis" button, the logo, and links like index.html#analysis.
function openTab(name) {
  if (!TAB_NAMES.includes(name)) return;
  setControl(tabs, "value", name);
  tabShown(name);
}
document.getElementById("open-analysis").addEventListener("click", () => openTab("analysis"));
window.addEventListener("hashchange", () => openTab(location.hash.slice(1)));

// ------------------------------------------------------------ the assistant window (leader's lane)

async function loadAssistant() {
  try {
    const check = await fetch("assistant/assistant.js", { method: "HEAD" });
    if (!check.ok) return;
    document.getElementById("assistant-float").hidden = false;   // show the floating button
    const script = document.createElement("script");
    script.src = "assistant/assistant.js?v=" + Date.now();   // never an old cached copy (leader's request)
    document.body.appendChild(script);
  } catch (error) { /* no assistant: fine */ }
}

// The practice area changes size with the window, and has no size at all while another tab
// is shown. A ResizeObserver tells us each time its size changes, so the drawing stays sharp.
new ResizeObserver(resizeCanvas).observe(area);
resizeCanvas();
showTally();
connect();
loadStatus();
loadAssistant();
loadSummary();                                       // also fills "How well it does"
if (location.hash.length > 1) openTab(location.hash.slice(1));
requestAnimationFrame(draw);
