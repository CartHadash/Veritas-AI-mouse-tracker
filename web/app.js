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
// One plain sentence per filter, shown under the filter buttons (leader's agent, Sun 15 Nov).
const MODE_HINTS = {
  none: "The cursor follows your hand exactly, shake and all. Useful for comparing.",
  low_sensitivity: "The cursor moves half as far as your hand, so shaking looks smaller. Click the area to start, Esc to stop.",
  one_euro: "A classic smoothing filter: very steady when you hold still, a little behind when you move.",
  learned: "Our trained model removes shaking, and only switches on when the detector sees tremor.",
};
const TARGET_RADIUS = 22;           // px; small on purpose, so a shaky cursor finds it hard

let socket = null;
let latest = null;                  // last reply from the server
let meterStale = false;             // a reply arrived since the meter was last redrawn
let lastReplyAt = 0;                // when the last reply arrived (the meter greys out after 1 s)
const METER_PAUSE_MS = 1000;
// A fast mouse reports up to 1000 movements a second; the models work at 100 a second, so the
// page sends at most one sample per SEND_GAP_MS (plus always the newest one of each event).
const SEND_GAP_MS = 4;
let lastSentAt = -Infinity;
let inside = false;                 // is the pointer inside the practice area?
// "Lower sensitivity" uses Pointer Lock: the browser holds the real pointer still and reports
// only how far the hand moved, so the drawn cursor (half the hand's movement) is the only
// cursor and can reach every part of the area. Esc or another filter releases it.
let locked = false;
let lockRefusals = 0;               // refusals in a row (Chrome refuses for ~1 s after Esc; some
                                    // browsers, like the app's built-in pane, always refuse)
let hand = null;                    // while locked: the hand's position, added up from its movement
let settings = { mode: "learned", strength: 1, demo_tremor: false, tracking: false };
let threshold = 0.165;
let target = null;                  // {x, y, shownAt, kind}: made by makeTarget() in targets.js
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
// The target's shape and size decide this (a checkbox is a small square, a link a wide strip).
function onTarget(p) { return targetContains(target, p); }

// The last moments of movement, drawn as two fading lines behind the cursors: where the hand
// went (raw) and where the corrected cursor went. Only real positions from the server.
const TRAIL_MS = 700;               // how much of the past the lines show
let trail = [];                     // [{at, rawX, rawY, x, y}, ...], oldest first
// "Shake" readout: the last 2.5 s of replies. The intended path is estimated as the raw path
// averaged over 0.25 s (that irons out 3-12 Hz shaking); shake = average distance of a cursor
// from it. For display only: it never affects the correction.
const SHAKE_MS = 2500, SMOOTH_MS = 125;
let shakeLog = [];                  // [{at, rawX, rawY, x, y}, ...], oldest first
let shakeMode = null, shakeShownAt = 0;

function shakeNow() {
  const now = performance.now();
  while (shakeLog.length && now - shakeLog[0].at > SHAKE_MS) shakeLog.shift();
  if (shakeLog.length < 30 || now - shakeLog[0].at < 1500) return null;      // too little yet
  // A sliding window: `from`..`to` are the samples within SMOOTH_MS of sample s, and sumX/sumY
  // their totals. Both ends only ever move forward, so every sample is added and removed once.
  // (Sun 15 Nov: this used to compare every sample with every other one, which stalled the
  // page for 5 ms on a trackpad and 38 ms with a 1000-per-second mouse, 4 times a second.)
  let raw = 0, shown = 0, n = 0;
  let from = 0, to = 0, sumX = 0, sumY = 0;
  for (const s of shakeLog) {
    while (to < shakeLog.length && shakeLog[to].at - s.at <= SMOOTH_MS) {
      sumX += shakeLog[to].rawX; sumY += shakeLog[to].rawY; to += 1;
    }
    while (s.at - shakeLog[from].at > SMOOTH_MS) {
      sumX -= shakeLog[from].rawX; sumY -= shakeLog[from].rawY; from += 1;
    }
    if (s.at - shakeLog[0].at < SMOOTH_MS || now - s.at < SMOOTH_MS) continue;  // need both sides
    const rx = sumX / (to - from), ry = sumY / (to - from);
    raw += Math.hypot(s.rawX - rx, s.rawY - ry);
    shown += Math.hypot(s.x - rx, s.y - ry);
    n += 1;
  }
  return n ? { raw: raw / n, shown: shown / n } : null;
}

// Short-lived marks drawn on the practice area after a click: a ring that bursts out of a hit
// target (with the time it took), or a small cross where a miss landed.
const EFFECT_MS = 700;
let effects = [];                   // [{kind: "hit"|"miss", x, y, at, text}, ...]
let streak = 0;                     // hits in a row; a miss sets it back to 0

// The detector's score over the last 20 seconds, for the small graph under the meter.
const GRAPH_SECONDS = 20;
let scoreHistory = [];              // [{at, score, tremor}, ...], at most 10 points a second

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
    lastReplyAt = performance.now();
    if (inside) {
      trail.push({ at: performance.now(), rawX: message.raw_x, rawY: message.raw_y, x: message.x, y: message.y });
      shakeLog.push({ at: performance.now(), rawX: message.raw_x, rawY: message.raw_y, x: message.x, y: message.y });
      if (trail.length > 400) trail.shift();          // never grows without limit
    }
    meterStale = true;                                // the meter is redrawn once per frame (draw)
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
// (The practice area itself is never enlarged by "Larger text" (web/reading.js), so pointer
// positions and the drawing always use the same pixels.)

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
  for (let i = 0; i < samples.length; i++) {
    const e = samples[i];
    const p = e.p;
    // Skip in-between movements that follow the last sent one too closely (never the newest,
    // so the cursor always ends exactly where the hand stopped; never during a calibration).
    const newest = i === samples.length - 1;
    if (!newest && !calib && e.timeStamp - lastSentAt < SEND_GAP_MS) continue;
    if (e.timeStamp <= lastSentAt) continue;          // time must move forward for the filters
    lastSentAt = e.timeStamp;
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
  shakeLog = [];
  if (calib && calib.phase !== "scoring") {                 // left the area: the test is void
    if (calib.phase === "running") send({ type: "calibrate_cancel" });
    calib = null;
    showCalibrationText("Calibration stopped: keep the pointer inside the practice area. Try again.");
  }
});
// Coming back into the area (maybe somewhere else): start the filter afresh, so the
// cursor never jumps across from where the pointer left.
area.addEventListener("pointerenter", () => { trail = []; shakeLog = []; send({ type: "reset" }); });

document.addEventListener("pointerlockchange", () => {
  locked = document.pointerLockElement === area;
  if (locked) lockRefusals = 0;
  inside = locked;
  trail = [];
  shakeLog = [];
  send({ type: "reset" });                // start the filter afresh where the pointer is
});
document.addEventListener("pointerlockerror", () => {
  // Not final: every new click in the area tries again (no more giving up for the session).
  lockRefusals += 1;
});

// The server needs the practice area's size so "Lower sensitivity" stays inside it.
function sendArea() { send({ type: "area", width: area.clientWidth, height: area.clientHeight }); }

area.addEventListener("pointerdown", (event) => {
  if (settings.mode === "low_sensitivity" && !locked && area.requestPointerLock) {
    hand = areaPosition(event);           // start where the pointer is now
    // This click only starts the mode; it is not a target click. Newer browsers also report a
    // refusal as a failed promise: "pointerlockerror" below already handles it, so ignore that.
    const request = area.requestPointerLock();
    if (request && request.catch) request.catch(() => {});
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
    const seconds = (performance.now() - target.shownAt) / 1000;
    row.hits += 1;
    row.totalTime += seconds;
    streak += 1;
    effects.push({ kind: "hit", x: target.x, y: target.y, at: performance.now(), text: seconds.toFixed(1) + " s" });
    newTarget();
  } else {
    row.misses += 1;
    streak = 0;
    effects.push({ kind: "miss", x: released.x, y: released.y, at: performance.now() });
  }
  showStreak();
  send({ type: "click", hit });
  showTally();
});

// ------------------------------------------------------------ targets and tally

// The next everyday thing to click (targets.js takes the kinds in turn), at a random place.
function newTarget() {
  target = makeTarget(area.clientWidth, area.clientHeight);
}

function showStreak() {
  const chip = document.getElementById("streak");
  chip.hidden = streak < 2;                      // one hit is not yet "in a row"
  chip.textContent = `${streak} in a row`;
}

// One bar per filter tried: the filled part is the share of clicks that hit the target.
// Each bar is a <ui-meter>, so screen readers can read it too.
function showTally() {
  const box = document.getElementById("tally");
  box.replaceChildren();
  const empty = Object.keys(tally).length === 0;
  box.hidden = empty;
  document.getElementById("tally-empty").hidden = !empty;
  for (const [mode, row] of Object.entries(tally)) {
    const [name, freeze] = mode.split("+");
    const title = MODE_NAMES[name] + (freeze ? " + click freeze" : "");
    const clicks = row.hits + row.misses;
    const time = row.hits ? `, ${(row.totalTime / row.hits).toFixed(1)} s per target` : "";
    const div = document.createElement("div");
    div.className = "tally-row";
    div.innerHTML = `
      <div class="row-between"><b>${title}</b><span>${Math.round(100 * row.hits / clicks)}%</span></div>
      <ui-meter value="${row.hits}" min="0" max="${clicks}" aria-label="${title}: clicks that hit">
        <ui-meter-track><ui-meter-indicator></ui-meter-indicator></ui-meter-track>
      </ui-meter>
      <p class="small">${row.hits} of ${clicks} clicks hit${time}</p>`;
    box.appendChild(div);
  }
}

// ------------------------------------------------------------ meter and settings display

function updateMeter() {
  if (!latest) return;
  if (latest.mode !== shakeMode) { shakeLog = []; shakeMode = latest.mode; }   // a new filter: start over
  if (performance.now() - shakeShownAt > 250) {                                   // 4 times a second is plenty
    shakeShownAt = performance.now();
    const shake = shakeNow();
    document.getElementById("shake").textContent = !shake ? "-"
    : latest.mode === "none" ? shake.raw.toFixed(1)
    : `${shake.raw.toFixed(1)} → ${shake.shown.toFixed(1)}`;
  }
  const word = document.getElementById("tremor-word");
  if (latest.score === null) {
    word.textContent = "Collecting 2.56 s of movement...";
    return;
  }
  word.textContent = latest.tremor ? "Tremor-like movement detected" : "No tremor-like movement";
  const now = performance.now();
  const last = scoreHistory[scoreHistory.length - 1];
  if (!last || now - last.at >= 100) scoreHistory.push({ at: now, score: latest.score, tremor: latest.tremor });
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
  if (settings.response) setControl(document.getElementById("response"), "value", settings.response);
  document.getElementById("response-row").hidden = settings.mode !== "learned";
  document.getElementById("mode-hint").textContent = MODE_HINTS[settings.mode] || "";
  document.getElementById("demo-banner").hidden = !settings.demo_tremor;
  document.getElementById("demo-levels-row").hidden = !settings.demo_tremor;
  document.getElementById("demo-tip").hidden = settings.demo_tremor;
  document.getElementById("legend-demo").hidden = !settings.demo_tremor;
}

// Each control reports a change the person made; we send it to the server, which answers
// with the settings now in force (showSettings then shows them).
// One exception: after a reload the browser may put a control back to how it was and report
// that as a change with reason "restore". The server already knows the real settings, so
// those reports are ignored.
function onChange(id, eventName, handler) {
  document.getElementById(id).addEventListener(eventName, (e) => {
    if (e.detail.reason !== "restore") handler(e.detail.value);
  });
}
onChange("modes", "valuechange", (value) => postSettings({ mode: value }));
onChange("demo-levels", "valuechange", (value) => postSettings({ demo_level: value }));
onChange("response", "valuechange", (value) => postSettings({ response: value }));
// "valuecommit" fires once when the slider is let go, so we save once, not on every step.
onChange("strength", "valuecommit", (value) => postSettings({ strength: Number(value) }));
onChange("demo-toggle", "checkedchange", (value) => postSettings({ demo_tremor: value }));
onChange("freeze-toggle", "checkedchange", (value) => { freezeOn = value; });
onChange("tracking-toggle", "checkedchange", (value) => postSettings({ tracking: value }));
document.getElementById("reset").addEventListener("click", async () => {
  await fetch("/api/reset", { method: "POST" });
  for (const key of Object.keys(tally)) delete tally[key];
  streak = 0;
  scoreHistory = [];
  showStreak();
  showTally();
  send({ type: "reset" });
  newTarget();
});

// ------------------------------------------------------------ calibration test

document.getElementById("calibrate").addEventListener("click", () => {
  const radius = Math.min(120, area.clientWidth / 2 - 30, area.clientHeight / 2 - 30);
  calib = { phase: "waiting", start: null, radius,
            centre: { x: area.clientWidth / 2, y: area.clientHeight / 2 + radius } };
  document.getElementById("calib-apply").hidden = true;
  showCalibrationText("Move your cursor onto the blue dot and hold it there. Then follow the dot.");
});

// "Use this filter": switches to the filter that kept the cursor closest to the dot in the
// test. Never automatic: the person decides (one short test is a hint, not a final answer).
let calibChoice = null;
document.getElementById("calib-apply").addEventListener("click", async () => {
  if (!calibChoice) return;
  await postSettings({ mode: calibChoice.mode, strength: calibChoice.strength });
  document.getElementById("calib-apply").hidden = true;
  showCalibrationText(`Switched to ${calibChoice.name}. You can change the filter any time.`);
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
    "Kept only until the server stops; not a diagnosis.");
  // Offer the closest filter, unless it is already the one in use.
  calibChoice = { name: result.chosen, mode: result.mode, strength: result.strength };
  const inUse = settings.mode === result.mode && Number(settings.strength) === result.strength;
  const apply = document.getElementById("calib-apply");
  apply.textContent = `Use ${result.chosen}`;
  apply.hidden = inUse;
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

// "Lower sensitivity" works only with the pointer locked (see the top of this file). Until then,
// a clear message in the middle of the area says what to do, or that the browser blocked it.
function drawLockInvite() {
  const w = area.clientWidth, h = area.clientHeight;
  const blocked = lockRefusals >= 2;
  const narrow = w < 440;                                   // a phone: shorter words
  ctx.fillStyle = "rgba(255, 252, 247, 0.88)";
  ctx.fillRect(0, h / 2 - 52, w, 104);
  ctx.textAlign = "center";
  ctx.fillStyle = INK;
  ctx.font = '600 20px "Avenir Next", "Segoe UI", system-ui, sans-serif';
  ctx.fillText(blocked ? (narrow ? "Pointer lock blocked" : "This browser blocked the pointer lock")
                       : (narrow ? "Click to start" : "Click here to start Lower sensitivity"), w / 2, h / 2 - 8);
  ctx.fillStyle = MUTED;
  ctx.font = '500 15px "Avenir Next", "Segoe UI", system-ui, sans-serif';
  ctx.fillText(blocked ? (narrow ? "Click to retry, or use Chrome" : "Lower sensitivity needs it. Click to try again, or use Chrome or Safari.")
                       : (narrow ? "Esc gives the pointer back" : "Your pointer is then held in the box; press Esc to get it back."),
               w / 2, h / 2 + 20);
}

function draw() {
  const now = performance.now();
  if (meterStale) { meterStale = false; updateMeter(); }
  // No movement for a second: the meter's numbers are old, so grey them out and say so.
  const paused = latest !== null && now - lastReplyAt > METER_PAUSE_MS;
  const meterCard = document.querySelector(".meter-card");
  if (paused !== meterCard.classList.contains("paused")) {
    meterCard.classList.toggle("paused", paused);
    if (paused) {
      const word = document.getElementById("tremor-word");
      word.textContent = "Paused: move the pointer in the practice area";
      word.classList.remove("tremor");
    }
    else meterStale = true;                           // back: show the fresh values at once
  }
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
    drawTarget(ctx, target);                          // a button, a checkbox, a folder... (targets.js)
  }
  drawEffects(now);
  if (settings.mode === "low_sensitivity" && !locked) drawLockInvite();
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
  } else if (!(settings.mode === "low_sensitivity" && !locked)) {   // (that mode has its own message)
    ctx.fillStyle = MUTED;
    ctx.font = '500 21px "Avenir Next", "Segoe UI", system-ui, sans-serif';
    ctx.textAlign = "center";
    // A shorter invitation when the area is too narrow for the long one (a phone).
    const invite = area.clientWidth < 440 ? "Move in here" : "Move your mouse or trackpad in here";
    ctx.fillText(invite, area.clientWidth / 2, area.clientHeight / 2);
  }
  drawScoreGraph(now);
  requestAnimationFrame(draw);
}

// Hit: a ring grows out of where the target was and fades, with the time it took above it.
// Miss: a small cross where the click landed. Both last EFFECT_MS.
function drawEffects(now) {
  effects = effects.filter((e) => now - e.at < EFFECT_MS);
  for (const e of effects) {
    const k = (now - e.at) / EFFECT_MS;             // 0 at the click, 1 when it vanishes
    const fade = (1 - k).toFixed(2);
    if (e.kind === "hit") {
      ctx.lineWidth = 4;
      ctx.strokeStyle = `rgba(31, 111, 87, ${fade})`;
      ctx.beginPath();
      ctx.arc(e.x, e.y, TARGET_RADIUS + 34 * k, 0, 2 * Math.PI);
      ctx.stroke();
      ctx.fillStyle = `rgba(31, 111, 87, ${fade})`;
      ctx.font = '700 19px "Avenir Next", "Segoe UI", system-ui, sans-serif';
      ctx.textAlign = "center";
      ctx.fillText(e.text, e.x, e.y - TARGET_RADIUS - 14 - 16 * k);
    } else {
      ctx.lineWidth = 3;
      ctx.lineCap = "round";
      ctx.strokeStyle = `rgba(194, 84, 15, ${fade})`;
      ctx.beginPath();
      ctx.moveTo(e.x - 7, e.y - 7); ctx.lineTo(e.x + 7, e.y + 7);
      ctx.moveTo(e.x + 7, e.y - 7); ctx.lineTo(e.x - 7, e.y + 7);
      ctx.stroke();
    }
  }
}

// The small graph under the meter: the score (0 at the bottom, 1 at the top) against time,
// "now" at the right edge. Green while below the cut-off, orange while tremor-like. Where the
// pointer was not moving there are no points, so the line has a gap.
const graph = document.getElementById("score-graph");
const graphCtx = graph.getContext("2d");
function drawScoreGraph(now) {
  const W = graph.clientWidth, H = graph.clientHeight;
  if (W === 0) return;                               // the Practice tab is hidden
  const ratio = window.devicePixelRatio || 1;
  if (graph.width !== Math.round(W * ratio)) { graph.width = Math.round(W * ratio); graph.height = Math.round(H * ratio); }
  graphCtx.setTransform(ratio, 0, 0, ratio, 0, 0);
  graphCtx.clearRect(0, 0, W, H);
  scoreHistory = scoreHistory.filter((p) => now - p.at < GRAPH_SECONDS * 1000);
  const xOf = (p) => W * (1 - (now - p.at) / (GRAPH_SECONDS * 1000));
  const yOf = (score) => 3 + (H - 6) * (1 - score);
  // The cut-off: a dashed line across the graph.
  graphCtx.setLineDash([5, 5]);
  graphCtx.strokeStyle = MUTED;
  graphCtx.lineWidth = 1.5;
  graphCtx.beginPath(); graphCtx.moveTo(0, yOf(threshold)); graphCtx.lineTo(W, yOf(threshold)); graphCtx.stroke();
  graphCtx.setLineDash([]);
  graphCtx.lineWidth = 3;
  graphCtx.lineCap = "round";
  for (let i = 1; i < scoreHistory.length; i++) {
    const a = scoreHistory[i - 1], b = scoreHistory[i];
    if (b.at - a.at > 500) continue;                 // a pause in movement: leave a gap
    graphCtx.strokeStyle = b.tremor ? "#c2540f" : "#1f6f57";
    graphCtx.beginPath(); graphCtx.moveTo(xOf(a), yOf(a.score)); graphCtx.lineTo(xOf(b), yOf(b.score)); graphCtx.stroke();
  }
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

// "Show me" buttons on the How-it-works tab: open Practice and ring the part the step is about.
for (const button of document.querySelectorAll("[data-show]")) {
  button.addEventListener("click", () => {
    openTab("practice");
    const part = document.querySelector(button.dataset.show);
    part.scrollIntoView({ block: "center" });
    part.classList.add("spotlight");
    setTimeout(() => part.classList.remove("spotlight"), 2600);
  });
}
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
