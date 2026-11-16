// summary.js - the Analysis tab of index.html (it used to be its own page,
// summary.html). Loaded before app.js, which calls loadSummary() when the tab is shown and
// owns MODE_NAMES. Reads GET /api/summary and
// draws a few tiles and one chart with the browser's canvas (no chart library, so it works
// offline). Wording is for a general reader: no medical claims.

function percent(x) { return x === null || x === undefined ? "-" : `${Math.round(x * 100)}%`; }
function number(x, digits = 1) { return x === null || x === undefined ? "-" : Number(x).toFixed(digits); }

// ------------------------------------------------------------ tiles: numbers, rings, a gauge

// What each tile showed last time, so a number counts on from there instead of from zero.
const shownBefore = {};
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// Count a number up (or down) to its new value over 0.7 s. `format` turns the number into
// text, for example percent. If the Analysis tab is hidden, just show the value.
function countTo(element, key, value, format) {
  if (value === null || value === undefined) { element.textContent = "-"; return; }
  const visible = document.getElementById("tiles").offsetParent !== null;
  const from = shownBefore[key] ?? 0;
  if (!visible || reducedMotion || from === value) { element.textContent = format(value); if (visible) shownBefore[key] = value; return; }
  shownBefore[key] = value;
  const start = performance.now();
  function step(now) {
    const k = Math.min(1, (now - start) / 700);
    const eased = 1 - (1 - k) ** 3;                  // fast at first, then settling
    element.textContent = format(from + (value - from) * eased);
    if (k < 1) requestAnimationFrame(step);
  }
  element.textContent = format(from);
  requestAnimationFrame(step);
}

// A plain tile: one number and what it means.
function tile(key, value, format, label) {
  const div = document.createElement("div");
  div.className = "tile";
  div.innerHTML = `<div class="value"></div><div class="label">${label}</div>`;
  countTo(div.querySelector(".value"), key, value, format);
  return div;
}

// A ring tile for a share between 0 and 1: the coloured arc covers that share of the circle.
// The arc is a circle whose outline is one long dash; we hide the part beyond the share.
const RING_LENGTH = 2 * Math.PI * 52;                // the circle's outline, radius 52
function ringTile(key, share, label) {
  const div = document.createElement("div");
  div.className = "tile ring-tile";
  div.innerHTML = `
    <div class="ring">
      <svg viewBox="0 0 120 120" aria-hidden="true">
        <circle class="ring-track" cx="60" cy="60" r="52"/>
        <circle class="ring-arc" cx="60" cy="60" r="52" stroke-dasharray="${RING_LENGTH}"/>
      </svg>
      <div class="value"></div>
    </div>
    <div class="label">${label}</div>`;
  const arc = div.querySelector(".ring-arc");
  const before = shownBefore[key] ?? 0;
  arc.style.strokeDashoffset = RING_LENGTH * (1 - before);       // start where it was...
  requestAnimationFrame(() => requestAnimationFrame(() => {      // ...then glide to the new share
    arc.style.strokeDashoffset = RING_LENGTH * (1 - (share ?? 0));
  }));
  countTo(div.querySelector(".value"), key, share, percent);
  return div;
}

// A gauge tile for a score between 0 and 1, drawn with ui-sdk's <ui-meter>.
function gaugeTile(key, value, label, lowWord, highWord) {
  const div = document.createElement("div");
  div.className = "tile gauge-tile";
  div.innerHTML = `
    <div class="value"></div>
    <ui-meter value="${value ?? 0}" min="0" max="1" aria-label="${label}">
      <ui-meter-track><ui-meter-indicator></ui-meter-indicator></ui-meter-track>
    </ui-meter>
    <div class="gauge-ends"><span>${lowWord}</span><span>${highWord}</span></div>
    <div class="label">${label}</div>`;
  countTo(div.querySelector(".value"), key, value, (x) => number(x, 2));
  return div;
}

function sentence(share) {
  // Plain-language description of the share of time; never "worse"/"better", never a diagnosis.
  if (share === null || share === undefined) return "Not enough movement analysed yet";
  return `Tremor-like movement was detected in ${percent(share)} of the analysed time`;
}

function drawChart(byTime) {
  const canvas = document.getElementById("by-time");
  document.getElementById("by-time-empty").hidden = byTime.length > 0;
  canvas.hidden = byTime.length === 0;
  if (!byTime.length || canvas.clientWidth === 0) return;   // nothing to draw, or the tab is hidden

  const ratio = window.devicePixelRatio || 1;
  canvas.width = canvas.clientWidth * ratio;
  canvas.height = canvas.clientHeight * ratio;
  const ctx = canvas.getContext("2d");
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  const W = canvas.clientWidth, H = canvas.clientHeight;
  const top = 16, bottom = 36;
  const maxSize = Math.max(5, ...byTime.map((m) => m.strength_px));
  ctx.font = '14px "Avenir Next", "Segoe UI", system-ui, sans-serif';
  // The side margins are as wide as the widest label needs, so no label is cut off
  // (the right-hand "12.3 px" labels used to be, with a fixed 50 px margin).
  const left = Math.ceil(ctx.measureText("100%").width) + 14;
  const right = Math.ceil(ctx.measureText(`${maxSize.toFixed(1)} px`).width) + 14;
  chartMargins = { left, right };
  const plotW = W - left - right, plotH = H - top - bottom;
  const slot = plotW / byTime.length;
  ctx.clearRect(0, 0, W, H);

  // Axes and labels: left = share of time (0-100%), right = size in px.
  ctx.fillStyle = "#6a5241";
  ctx.strokeStyle = "#e7d2b8";
  for (const f of [0, 0.5, 1]) {
    const y = top + plotH * (1 - f);
    ctx.beginPath(); ctx.moveTo(left, y); ctx.lineTo(W - right, y); ctx.stroke();
    ctx.textAlign = "right"; ctx.fillText(`${Math.round(f * 100)}%`, left - 6, y + 5);
    ctx.textAlign = "left"; ctx.fillText(`${(f * maxSize).toFixed(1)} px`, W - right + 6, y + 5);
  }

  // Bars: share of time with tremor-like movement.
  byTime.forEach((m, i) => {
    const h = plotH * m.detected_share;
    if (i === hoverIndex) {                          // the minute under the pointer: a soft column
      ctx.fillStyle = "#f3e6d4";
      ctx.fillRect(left + i * slot, top, slot, plotH);
    }
    ctx.fillStyle = "#d9661a";
    ctx.fillRect(left + i * slot + slot * 0.2, top + plotH - h, slot * 0.6, h);
    ctx.fillStyle = "#6a5241";
    ctx.textAlign = "center";
    ctx.fillText(`min ${m.minute}`, left + i * slot + slot / 2, H - 12);
  });

  // Line: typical size of the shaking.
  ctx.strokeStyle = "#1f6f57";
  ctx.lineWidth = 3;
  ctx.beginPath();
  byTime.forEach((m, i) => {
    const x = left + i * slot + slot / 2, y = top + plotH * (1 - m.strength_px / maxSize);
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  });
  ctx.stroke();
  ctx.fillStyle = "#1f6f57";
  byTime.forEach((m, i) => {
    ctx.beginPath();
    ctx.arc(left + i * slot + slot / 2, top + plotH * (1 - m.strength_px / maxSize), 5, 0, 2 * Math.PI);
    ctx.fill();
  });
  ctx.lineWidth = 1;

  // The exact numbers of the minute under the pointer, in a small dark label.
  if (hoverIndex >= 0 && hoverIndex < byTime.length) {
    const m = byTime[hoverIndex];
    const lines = [`Minute ${m.minute}`, `${percent(m.detected_share)} tremor-like`, `shaking about ${number(m.strength_px)} px`];
    ctx.font = '600 14px "Avenir Next", "Segoe UI", system-ui, sans-serif';
    const boxW = Math.max(...lines.map((t) => ctx.measureText(t).width)) + 24, boxH = 74;
    const centre = left + hoverIndex * slot + slot / 2;
    const x = Math.min(Math.max(centre - boxW / 2, 4), W - boxW - 4);       // stay inside the chart
    ctx.fillStyle = "#2f1d10";
    ctx.beginPath(); ctx.roundRect(x, top + 6, boxW, boxH, 10); ctx.fill();
    ctx.fillStyle = "#fffdf8";
    ctx.textAlign = "left";
    lines.forEach((t, k) => ctx.fillText(t, x + 12, top + 28 + k * 20));
  }
}

// Which minute's column the pointer is over (-1 = none). Moving over the chart redraws it.
let hoverIndex = -1;
let chartMargins = { left: 50, right: 50 };       // set by drawChart to fit its labels
function chartHover(event) {
  const canvas = document.getElementById("by-time");
  const byTime = lastSummary ? lastSummary.tremor.by_time : [];
  const box = canvas.getBoundingClientRect();
  const scale = box.width / canvas.clientWidth || 1;               // not 1 when "Larger text" is on
  const plotW = canvas.clientWidth - chartMargins.left - chartMargins.right;
  const x = (event.clientX - box.left) / scale - chartMargins.left;
  const index = byTime.length && x >= 0 && x < plotW ? Math.floor(x / (plotW / byTime.length)) : -1;
  if (index !== hoverIndex) { hoverIndex = index; drawChart(byTime); }
}

async function loadSummary() {
  const s = await (await fetch("/api/summary")).json();
  lastSummary = s;

  const notes = document.getElementById("notes");
  notes.innerHTML = "";
  for (const note of s.notes) {
    const div = document.createElement("div");
    div.className = "banner";
    div.textContent = note.startsWith("Tremor replay")
      ? "Demo mode was on during this session: part of the tremor shown was a replayed recording from a public dataset, not your own movement."
      : note;
    notes.appendChild(div);
  }

  const tiles = document.getElementById("tiles");
  tiles.innerHTML = "";
  tiles.appendChild(ringTile("share", s.tremor.detected_share, sentence(s.tremor.detected_share)));
  tiles.appendChild(tile("rhythm", s.tremor.typical_frequency_hz || null, (x) => `${number(x)} Hz`,
    "Typical rhythm of the shaking, when detected"));
  tiles.appendChild(tile("size", s.tremor.typical_strength_px || null, (x) => `${number(x)} px`,
    "Typical size of the shaking on screen, when detected"));
  tiles.appendChild(gaugeTile("steady", s.usage.steadiness_score, "Steadiness score", "shaking of 10 px or more", "very steady"));
  tiles.appendChild(tile("active", s.session.minutes_active, (x) => `${number(x)} min`, "Active time (pointer moving)"));
  tiles.appendChild(tile("distance", s.usage.distance_px, (x) => `${Math.round(x).toLocaleString()} px`, "Distance the pointer travelled"));
  tiles.appendChild(tile("clicks", s.usage.clicks_in_app, (x) => `${Math.round(x)}`, "Clicks in the practice area"));
  tiles.appendChild(ringTile("accuracy", s.usage.click_accuracy, "Clicks that hit the target"));

  drawChart(s.tremor.by_time);

  const laptop = s.whole_laptop;
  document.getElementById("laptop").hidden = !laptop;
  if (laptop) {
    const lt = document.getElementById("laptop-tiles");
    lt.innerHTML = "";
    lt.appendChild(ringTile("laptop-share", laptop.tremor.detected_share, sentence(laptop.tremor.detected_share)));
    lt.appendChild(tile("laptop-active", laptop.session.minutes_active, (x) => `${number(x)} min`, "Active time across the laptop"));
    lt.appendChild(tile("laptop-distance", laptop.usage.distance_px, (x) => `${Math.round(x).toLocaleString()} px`, "Distance across the laptop"));
    lt.appendChild(gaugeTile("laptop-steady", laptop.usage.steadiness_score, "Steadiness score", "shaking", "very steady"));
  }

  const info = s.model_info;
  const detectorText =
    `Detector version ${info.detector_version}. On people it had never seen, it missed ${percent(info.missed_cases_rate)} ` +
    `of tremor windows and raised a false alarm on ${percent(info.false_alarm_rate)} of windows without tremor ` +
    `(tested on recordings from a public dataset, not on mouse use).`;
  const filterText = ` Filter now: ${MODE_NAMES[s.filter.mode] ?? s.filter.mode}, strength ${s.filter.strength}.`;
  // Analysis shows the detector sentence and the filter in use; "How it works" only the
  // detector sentence (class "no-filter"), next to the corrector's result written in index.html.
  for (const element of document.querySelectorAll(".model-info")) {
    element.textContent = detectorText + (element.classList.contains("no-filter") ? "" : filterText);
  }
  loadHistory(s);
}

// ------------------------------------------------------------ earlier sessions

function historyRow(cells) {
  const tr = document.createElement("tr");
  for (const text of cells) {
    const td = document.createElement("td");
    td.textContent = text;                 // text only: saved values are never treated as HTML
    tr.appendChild(td);
  }
  return tr;
}

async function loadHistory(current) {
  // GET /api/assistant/history belongs to the assistant module; without it, no panel.
  let history;
  try {
    const response = await fetch("/api/assistant/history");
    if (!response.ok) return;
    history = await response.json();
  } catch (error) { return; }
  document.getElementById("history").hidden = false;
  const body = document.querySelector("#history-table tbody");
  body.innerHTML = "";
  const filterText = (f) => f ? `${MODE_NAMES[f.mode] ?? f.mode}${f.strength < 1 ? ` (${f.strength})` : ""}` : "-";
  const demoNow = current.notes.some((n) => n.startsWith("Tremor replay"));
  const now = historyRow(["This session", `${number(current.session.minutes_active)} min`,
    percent(current.tremor.detected_share), number(current.usage.steadiness_score, 2),
    percent(current.usage.click_accuracy), filterText(current.filter), demoNow ? "demo tremor was on" : ""]);
  now.className = "current";
  body.appendChild(now);
  for (const s of history.sessions) {
    const notes = [];
    if (s.demo_tremor_was_on) notes.push("demo tremor was on");
    if (s.filter && s.filter.mode !== current.filter.mode) notes.push("different filter");
    body.appendChild(historyRow([s.day, `${number(s.minutes_active)} min`, percent(s.detected_share),
      number(s.steadiness_score, 2), percent(s.click_accuracy), filterText(s.filter), notes.join(", ")]));
  }
  document.getElementById("history-empty").hidden = history.sessions.length > 0;
}

let lastSummary = null;
document.getElementById("reload").addEventListener("click", loadSummary);
document.getElementById("by-time").addEventListener("pointermove", chartHover);
document.getElementById("by-time").addEventListener("pointerleave", () => { hoverIndex = -1; if (lastSummary) drawChart(lastSummary.tremor.by_time); });
// Redraw the chart (no new request) whenever its size changes: the window was resized, or
// the Analysis tab has just been shown.
new ResizeObserver(() => { if (lastSummary) drawChart(lastSummary.tremor.by_time); })
  .observe(document.getElementById("by-time"));
