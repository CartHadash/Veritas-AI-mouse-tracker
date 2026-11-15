// exercises.js - three extras for the practice area (team leader's requests, Sun 15 Nov):
//
//   1. Trace the spiral: a faint spiral appears; the person follows it from the middle
//      outwards. The raw line stays in grey and the corrected line in green, and the page
//      says how far each strayed from the spiral on average. A practice exercise: it is not a
//      test of anything and says nothing about health.
//   2. Fair test: 10 targets with No filter, then THE SAME 10 targets (same things, same
//      places) with Our model, and a side-by-side result. Same targets both rounds is what
//      makes the comparison fair.
//   3. Hold to peek: while the space bar is held, the correction is off (the shown cursor and
//      the click follow the raw movement), so the person can feel the difference.
//
// Loaded before app.js. app.js calls the small functions in `practiceExtras` at five places
// (a reply arrived, draw, a click started, a click ended, is the target hidden); everything
// else lives here. Uses app.js's own things only when called: area, settings, target,
// postSettings, newTarget, MODE_NAMES. Plain markup with ids; the styling is the leader's.

const SPIRAL_TURNS = 3;
const SPIRAL_POINTS = 720;              // samples along the spiral (finer than a pixel apart)
const SPIRAL_START_PX = 22;             // how close to the middle dot the cursor must come to start
const SPIRAL_SECONDS = 60;              // an unfinished tracing ends by itself after this long
const FAIR_TARGETS = 10;                // targets per round of the fair test
const FAIR_GIVE_UP_SECONDS = 12;        // a target not hit in this time counts as not hit
const FAIR_ROUNDS = ["none", "learned"];

let spiral = null;      // {phase: "waiting"|"tracing"|"done", line, progress, raw, corrected, sums, started}
let fair = null;        // {round, index, targets, rounds: [{mode, hits, notHit, misses, time}], before, pauseUntil}
let peeking = false;    // the space bar is held: show and click with the raw movement

function exerciseStatus(text) {
  const line = document.getElementById("exercise-status");
  line.hidden = !text;
  line.textContent = text || "";
}
function exerciseResult(html) {
  const box = document.getElementById("exercise-result");
  box.hidden = !html;
  box.innerHTML = html || "";              // only text and numbers made in this file, never the server's text
}

// ------------------------------------------------------------ 1. trace the spiral

// The spiral as a list of points: it starts in the middle of the area and winds outwards.
function spiralLine() {
  const cx = area.clientWidth / 2, cy = area.clientHeight / 2;
  const reach = Math.min(area.clientWidth, area.clientHeight) / 2 - 36;
  const line = [];
  for (let i = 0; i < SPIRAL_POINTS; i++) {
    const k = i / (SPIRAL_POINTS - 1), angle = 2 * Math.PI * SPIRAL_TURNS * k;
    line.push({ x: cx + reach * k * Math.cos(angle), y: cy + reach * k * Math.sin(angle) });
  }
  return line;
}

function startSpiral() {
  fair = null;
  spiral = { phase: "waiting", line: spiralLine(), progress: 0, raw: [], corrected: [], sums: [0, 0], started: 0 };
  exerciseResult("");
  exerciseStatus("Move onto the dot in the middle, then follow the line outwards to its end. Take your time.");
  document.getElementById("spiral-start").textContent = "Start the spiral again";
}

// How far point p is from the spiral near where the tracing has got to. Looking only near
// the current place stops the next turn of the spiral, a few centimetres away, from counting.
function spiralDistance(p, from, to) {
  let best = Infinity, at = from;
  for (let i = from; i <= to; i++) {
    const d = Math.hypot(p.x - spiral.line[i].x, p.y - spiral.line[i].y);
    if (d < best) { best = d; at = i; }
  }
  return { distance: best, at };
}

function spiralReply(message) {
  const raw = { x: message.raw_x, y: message.raw_y }, shown = { x: message.x, y: message.y };
  if (spiral.phase === "waiting") {
    if (Math.hypot(shown.x - spiral.line[0].x, shown.y - spiral.line[0].y) > SPIRAL_START_PX) return;
    spiral.phase = "tracing";
    spiral.started = performance.now();
    exerciseStatus("Tracing... follow the line to its outer end.");
  }
  if (spiral.phase !== "tracing") return;
  // Where along the spiral the tracing is: the nearest point to the shown cursor, looked for
  // only a little way either side of the last place. It may also move back. (A first version
  // only ever moved forward and looked far ahead; strong tremor near the middle then made it
  // run a whole turn ahead of the hand and end the exercise early.)
  const last = SPIRAL_POINTS - 1;
  spiral.progress = spiralDistance(shown, Math.max(0, spiral.progress - 10), Math.min(last, spiral.progress + 12)).at;
  const from = Math.max(0, spiral.progress - 25), to = Math.min(last, spiral.progress + 25);
  const a = spiralDistance(raw, from, to), b = spiralDistance(shown, from, to);
  spiral.raw.push([raw.x, raw.y]);
  spiral.corrected.push([shown.x, shown.y]);
  spiral.sums[0] += a.distance;
  spiral.sums[1] += b.distance;
  if (spiral.progress >= SPIRAL_POINTS - 4) finishSpiral(true);
}

function finishSpiral(complete) {
  if (!spiral || spiral.phase !== "tracing" || spiral.raw.length < 20) { spiral = null; exerciseStatus(""); return; }
  spiral.phase = "done";
  const n = spiral.raw.length;
  const rawPx = spiral.sums[0] / n, correctedPx = spiral.sums[1] / n;
  // Kept readable from outside for the leader's session card (leader's request).
  window.lastSpiral = { raw: spiral.raw, corrected: spiral.corrected, rawDistance: rawPx, correctedDistance: correctedPx,
                        filter: settings.mode, demoTremor: Boolean(settings.demo_tremor), complete, at: new Date().toISOString() };
  const same = settings.mode === "none";
  exerciseStatus("");
  exerciseResult(
    `<p id="spiral-result"><b>Spiral traced${complete ? "" : " (stopped early)"}.</b> On average your raw line (grey) was ` +
    `<b>${rawPx.toFixed(1)} px</b> from the spiral` +
    (same ? "; no filter was on, so the shown line is the same." : `, and the corrected line (green) <b>${correctedPx.toFixed(1)} px</b>, with ${MODE_NAMES[settings.mode]}.`) +
    (settings.demo_tremor ? " Demo tremor was on: part of the shaking was a replayed recording." : "") +
    ` This is a practice exercise, not a test of anything.</p>` +
    `<button type="button" class="btn" id="spiral-clear">Back to the targets</button>`);
  document.getElementById("spiral-clear").addEventListener("click", () => { spiral = null; exerciseResult(""); });
}

function drawSpiral(ctx, now) {
  // The spiral to follow: a faint wide line.
  ctx.lineCap = "round"; ctx.lineJoin = "round";
  ctx.strokeStyle = "rgba(217, 102, 26, 0.22)";
  ctx.lineWidth = 10;
  ctx.beginPath();
  spiral.line.forEach((p, i) => (i ? ctx.lineTo(p.x, p.y) : ctx.moveTo(p.x, p.y)));
  ctx.stroke();
  const start = spiral.line[0], end = spiral.line[SPIRAL_POINTS - 1];
  ctx.fillStyle = "#d9661a";
  ctx.beginPath(); ctx.arc(start.x, start.y, spiral.phase === "waiting" ? 9 + 2 * Math.sin(now / 250) : 6, 0, 2 * Math.PI); ctx.fill();
  ctx.strokeStyle = "#d9661a"; ctx.lineWidth = 3;
  ctx.beginPath(); ctx.arc(end.x, end.y, 9, 0, 2 * Math.PI); ctx.stroke();
  // What was drawn so far: raw in grey underneath, corrected in green on top.
  for (const [points, colour, width] of [[spiral.raw, "rgba(120, 108, 98, 0.75)", 2], [spiral.corrected, "#1f6f57", 3]]) {
    if (points.length < 2) continue;
    ctx.strokeStyle = colour; ctx.lineWidth = width;
    ctx.beginPath();
    points.forEach((p, i) => (i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])));
    ctx.stroke();
  }
  if (spiral.phase === "tracing" && (now - spiral.started) / 1000 > SPIRAL_SECONDS) finishSpiral(false);
}

// ------------------------------------------------------------ 2. the fair test

function fairLine() {
  const r = fair.rounds[fair.round];
  exerciseStatus(`Fair test, round ${fair.round + 1} of ${FAIR_ROUNDS.length}: ${MODE_NAMES[r.mode]}. ` +
                 `Target ${Math.min(fair.index + 1, FAIR_TARGETS)} of ${FAIR_TARGETS}. Click each target as you normally would.`);
}

async function startFair() {
  spiral = null;
  exerciseResult("");
  fair = { round: 0, index: 0, targets: [], before: settings.mode, pauseUntil: 0,
           rounds: FAIR_ROUNDS.map((mode) => ({ mode, hits: 0, notHit: 0, misses: 0, time: 0 })) };
  await postSettings({ mode: FAIR_ROUNDS[0] });
  fairTarget();
}

// Show target number fair.index of this round. Round 1 makes the targets; later rounds reuse
// exactly the same ones, so every filter gets the same things in the same places.
function fairTarget() {
  if (fair.round === 0) {
    newTarget();
    fair.targets[fair.index] = { ...target };
  } else {
    target = { ...fair.targets[fair.index], shownAt: performance.now() };
  }
  target.shownAt = performance.now();
  fairLine();
}

async function fairNext() {
  fair.index += 1;
  if (fair.index < FAIR_TARGETS) { fairTarget(); return; }
  fair.round += 1;
  fair.index = 0;
  if (fair.round < FAIR_ROUNDS.length) {
    fair.pauseUntil = performance.now() + 3000;                  // a short breather between rounds
    exerciseStatus(`Round ${fair.round} done. Next: the same ${FAIR_TARGETS} targets with ${MODE_NAMES[FAIR_ROUNDS[fair.round]]}...`);
    await postSettings({ mode: FAIR_ROUNDS[fair.round] });
    setTimeout(() => { if (fair) fairTarget(); }, 3000);
    return;
  }
  finishFair();
}

function finishFair() {
  const done = fair;
  fair = null;
  postSettings({ mode: done.before });                           // back to the filter in use before
  newTarget();
  const cell = (r) => `<td>${r.hits} of ${FAIR_TARGETS}</td><td>${r.misses}</td>` +
                      `<td>${r.hits ? (r.time / r.hits).toFixed(1) + " s" : "-"}</td>`;
  window.lastFairTest = { rounds: done.rounds.map((r) => ({ ...r, secondsPerTarget: r.hits ? r.time / r.hits : null })),
                          targets: FAIR_TARGETS, demoTremor: Boolean(settings.demo_tremor), at: new Date().toISOString() };
  exerciseStatus("");
  exerciseResult(
    `<p><b>Fair test finished.</b> The same ${FAIR_TARGETS} targets each round.</p>` +
    `<table id="fair-result"><thead><tr><th>Filter</th><th>Targets hit</th><th>Clicks that missed</th><th>Time per target hit</th></tr></thead><tbody>` +
    done.rounds.map((r) => `<tr><th>${MODE_NAMES[r.mode]}</th>${cell(r)}</tr>`).join("") + `</tbody></table>` +
    `<p class="small">${settings.demo_tremor ? "Demo tremor was on: the shaking was a replayed recording, not your own movement. " : "Demo tremor was off. "}` +
    `A target not hit within ${FAIR_GIVE_UP_SECONDS} s counts as not hit. One short run on one day: a practice comparison, not a measurement of you.</p>`);
}

// ------------------------------------------------------------ 3. hold to peek (space bar)

function typingSomewhere() {
  const el = document.activeElement;
  // (A button that was just clicked keeps the focus; that is not typing, so it does not count.)
  return el && (el.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(el.tagName));
}
document.addEventListener("keydown", (event) => {
  if (event.code !== "Space" || typingSomewhere() || !inside) return;   // only while the pointer is in the area
  event.preventDefault();                                              // do not scroll the page
  peeking = true;
});
document.addEventListener("keyup", (event) => { if (event.code === "Space") peeking = false; });
window.addEventListener("blur", () => { peeking = false; });

// ------------------------------------------------------------ what app.js calls

const practiceExtras = {
  // A reply from the server arrived. While peeking, the shown cursor IS the raw movement.
  onReply(message) {
    if (peeking) { message.x = message.raw_x; message.y = message.raw_y; }
    if (spiral && inside) spiralReply(message);
  },
  hidesTarget() { return Boolean(spiral) || Boolean(fair && performance.now() < fair.pauseUntil); },
  blocksClicks() { return Boolean(spiral) || Boolean(fair && performance.now() < fair.pauseUntil); },
  // A click on the practice area ended (hit or miss), `seconds` after the target appeared.
  onClick(hit, seconds) {
    if (!fair) return;
    const r = fair.rounds[fair.round];
    if (hit) { r.hits += 1; r.time += seconds; fairNext(); }
    else r.misses += 1;
  },
  draw(ctx, now) {
    if (spiral) drawSpiral(ctx, now);
    if (fair && performance.now() >= fair.pauseUntil && target && (now - target.shownAt) / 1000 > FAIR_GIVE_UP_SECONDS) {
      fair.rounds[fair.round].notHit += 1;                       // too long on one target: move on
      fairNext();
    }
    if (peeking) {
      ctx.fillStyle = "rgba(47, 29, 16, 0.86)";
      ctx.beginPath(); ctx.roundRect(area.clientWidth / 2 - 190, 14, 380, 34, 17); ctx.fill();
      ctx.fillStyle = "#fffdf8";
      ctx.font = '600 15px "Avenir Next", "Segoe UI", system-ui, sans-serif';
      ctx.textAlign = "center";
      ctx.fillText("Correction paused while you hold the space bar", area.clientWidth / 2, 36);
    }
  },
};

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("spiral-start").addEventListener("click", startSpiral);
  document.getElementById("fair-start").addEventListener("click", startFair);
});
