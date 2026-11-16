// path_check.js - the team's blind check of the generated paths (see data_pipeline/make_path_check.py).
// Plain JavaScript. Replays each generated path at real speed, collects a 1-5 rating and
// what looks wrong, and at the end shows a text report to paste into the group chat.
// Nothing is saved or sent anywhere: the ratings live only in this browser tab.

const screen = document.getElementById("screen");
const speedCanvas = document.getElementById("speed");
let data = null;
let index = 0;                       // which path is showing
let started = 0;                     // performance.now() when the replay started
let slow = false;
let score = null;
const answers = [];                  // {id, version, score, problems, note}

async function load() {
  data = await (await fetch("path_check_paths.json")).json();
  showPath();
  requestAnimationFrame(draw);
}

function current() { return data.paths[index]; }

function showPath() {
  document.getElementById("path-title").textContent = `Path ${index + 1} of ${data.paths.length}`;
  score = null;
  for (const b of document.querySelectorAll("#stars button")) b.classList.remove("on");
  for (const box of document.querySelectorAll("#problems input")) box.checked = false;
  document.getElementById("note").value = "";
  document.getElementById("next").disabled = true;
  started = performance.now();
}

// Sharp drawing on Retina screens: size the canvas in device pixels.
function fit(canvas) {
  const ratio = window.devicePixelRatio || 1;
  const w = canvas.clientWidth, h = canvas.clientHeight;
  if (canvas.width !== Math.round(w * ratio)) {
    canvas.width = Math.round(w * ratio);
    canvas.height = Math.round(h * ratio);
  }
  const ctx = canvas.getContext("2d");
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  return { ctx, w, h };
}

function draw() {
  const path = current();
  const xy = path.xy;
  const seconds = (performance.now() - started) / 1000 * (slow ? 0.5 : 1);
  const shown = Math.min(xy.length, Math.floor(seconds * data.rate) + 1);

  // The screen: the trail so far and the cursor.
  const { ctx, w, h } = fit(screen);
  const scale = w / data.screen[0];
  ctx.clearRect(0, 0, w, h);
  ctx.strokeStyle = "rgba(59, 35, 20, 0.35)";
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  for (let i = 0; i < shown; i++) {
    const [x, y] = xy[i];
    if (i === 0) ctx.moveTo(x * scale, y * scale); else ctx.lineTo(x * scale, y * scale);
  }
  ctx.stroke();
  const [cx, cy] = xy[shown - 1];
  ctx.beginPath();
  ctx.arc(cx * scale, cy * scale, 6, 0, 2 * Math.PI);
  ctx.fillStyle = "#3b2314";
  ctx.fill();

  // Speed over time (px/s), filling in as the replay runs.
  const s = fit(speedCanvas);
  s.ctx.clearRect(0, 0, s.w, s.h);
  const speeds = [];
  for (let i = 1; i < xy.length; i++) {
    speeds.push(Math.hypot(xy[i][0] - xy[i - 1][0], xy[i][1] - xy[i - 1][1]) * data.rate);
  }
  const top = Math.max(200, ...speeds);
  s.ctx.strokeStyle = "#2e7d5b";
  s.ctx.lineWidth = 1.2;
  s.ctx.beginPath();
  for (let i = 0; i < shown - 1; i++) {
    const x = (i / (speeds.length - 1)) * s.w;
    const y = s.h - 6 - (speeds[i] / top) * (s.h - 22);
    if (i === 0) s.ctx.moveTo(x, y); else s.ctx.lineTo(x, y);
  }
  s.ctx.stroke();
  s.ctx.fillStyle = "#6e5444";
  s.ctx.font = "12px system-ui, sans-serif";
  s.ctx.fillText(`speed, up to ${Math.round(top)} px/s · ${(Math.min(seconds, xy.length / data.rate)).toFixed(1)} s of ${(xy.length / data.rate).toFixed(2)} s`, 6, 14);

  requestAnimationFrame(draw);
}

for (const button of document.querySelectorAll("#stars button")) {
  button.addEventListener("click", () => {
    score = Number(button.dataset.score);
    for (const b of document.querySelectorAll("#stars button")) b.classList.toggle("on", b === button);
    document.getElementById("next").disabled = false;
  });
}

document.getElementById("replay").addEventListener("click", () => { started = performance.now(); });
document.getElementById("slow").addEventListener("click", (event) => {
  slow = !slow;
  event.target.textContent = `Half speed: ${slow ? "on" : "off"}`;
  event.target.classList.toggle("on", slow);
  started = performance.now();
});

document.getElementById("next").addEventListener("click", () => {
  const problems = [...document.querySelectorAll("#problems input:checked")].map((box) => box.value);
  answers.push({ id: current().id, version: current().version, score, problems,
                 note: document.getElementById("note").value.trim() });
  index += 1;
  if (index < data.paths.length) { showPath(); return; }
  finish();
});

function finish() {
  index = data.paths.length - 1;                      // keep drawing the last path
  document.getElementById("rating-panel").hidden = true;
  document.getElementById("done-panel").hidden = false;
  const lines = ["Step 4 path check (web/path_check.html, seed " + data.seed + ")"];
  for (const version of ["current", "realistic"]) {
    const mine = answers.filter((a) => a.version === version);
    const mean = mine.reduce((sum, a) => sum + a.score, 0) / mine.length;
    const counts = {};
    for (const a of mine) for (const p of a.problems) counts[p] = (counts[p] || 0) + 1;
    const top = Object.entries(counts).sort((a, b) => b[1] - a[1]).map(([p, n]) => `${p} ${n}`).join(", ");
    lines.push(`${version === "current" ? "Current generator (models trained on it)" : "Realistic version"}: ` +
               `average ${mean.toFixed(1)} / 5 over ${mine.length} paths; problems: ${top || "none ticked"}`);
  }
  lines.push("Per path:");
  for (const a of answers) {
    lines.push(`${a.id} (${a.version}): ${a.score}/5` + (a.problems.length ? `, ${a.problems.join(", ")}` : "") +
               (a.note ? `, "${a.note}"` : ""));
  }
  document.getElementById("report").textContent = lines.join("\n");
}

document.getElementById("copy").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(document.getElementById("report").textContent);
    document.getElementById("copy").textContent = "Copied";
  } catch (error) {
    document.getElementById("copy").textContent = "Select the text and copy it by hand";
  }
});

load();
