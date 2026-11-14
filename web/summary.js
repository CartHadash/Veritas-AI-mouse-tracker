// summary.js - the Analysis tab of index.html (step 13; it used to be its own page,
// summary.html). Loaded before app.js, which calls loadSummary() when the tab is shown and
// owns MODE_NAMES. Reads GET /api/summary (Contract 2) and
// draws a few tiles and one chart with the browser's canvas (no chart library, so it works
// offline). Wording is for a general reader: no medical claims.

function percent(x) { return x === null || x === undefined ? "-" : `${Math.round(x * 100)}%`; }
function number(x, digits = 1) { return x === null || x === undefined ? "-" : Number(x).toFixed(digits); }

function tile(value, label) {
  const div = document.createElement("div");
  div.className = "tile";
  div.innerHTML = `<div class="value">${value}</div><div class="label">${label}</div>`;
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
  const left = 50, right = 50, top = 16, bottom = 36;
  const plotW = W - left - right, plotH = H - top - bottom;
  const maxSize = Math.max(5, ...byTime.map((m) => m.strength_px));
  const slot = plotW / byTime.length;
  ctx.clearRect(0, 0, W, H);
  ctx.font = '14px "Avenir Next", "Segoe UI", system-ui, sans-serif';

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
  tiles.appendChild(tile(percent(s.tremor.detected_share), sentence(s.tremor.detected_share)));
  tiles.appendChild(tile(s.tremor.typical_frequency_hz ? `${number(s.tremor.typical_frequency_hz)} Hz` : "-",
    "Typical rhythm of the shaking, when detected"));
  tiles.appendChild(tile(s.tremor.typical_strength_px ? `${number(s.tremor.typical_strength_px)} px` : "-",
    "Typical size of the shaking on screen, when detected"));
  tiles.appendChild(tile(s.usage.steadiness_score === null ? "-" : number(s.usage.steadiness_score, 2),
    "Steadiness score (1 = very steady, 0 = shaking of 10 px or more)"));
  tiles.appendChild(tile(`${number(s.session.minutes_active)} min`, "Active time (pointer moving)"));
  tiles.appendChild(tile(`${Math.round(s.usage.distance_px).toLocaleString()} px`, "Distance the pointer travelled"));
  tiles.appendChild(tile(`${s.usage.clicks_in_app}`, "Clicks in the practice area"));
  tiles.appendChild(tile(percent(s.usage.click_accuracy), "Clicks that hit the target"));

  drawChart(s.tremor.by_time);

  const laptop = s.whole_laptop;
  document.getElementById("laptop").hidden = !laptop;
  if (laptop) {
    const lt = document.getElementById("laptop-tiles");
    lt.innerHTML = "";
    lt.appendChild(tile(percent(laptop.tremor.detected_share), sentence(laptop.tremor.detected_share)));
    lt.appendChild(tile(`${number(laptop.session.minutes_active)} min`, "Active time across the laptop"));
    lt.appendChild(tile(`${Math.round(laptop.usage.distance_px).toLocaleString()} px`, "Distance across the laptop"));
    lt.appendChild(tile(laptop.usage.steadiness_score === null ? "-" : number(laptop.usage.steadiness_score, 2), "Steadiness score"));
  }

  const info = s.model_info;
  const modelText =
    `Detector version ${info.detector_version}. On people it had never seen, it missed ${percent(info.missed_cases_rate)} ` +
    `of tremor windows and raised a false alarm on ${percent(info.false_alarm_rate)} of windows without tremor ` +
    `(tested on recordings from a public dataset, not on mouse use). Filter now: ${MODE_NAMES[s.filter.mode] ?? s.filter.mode}, strength ${s.filter.strength}.`;
  // The same sentence is shown on the Analysis tab and on "How it works".
  for (const element of document.querySelectorAll(".model-info")) element.textContent = modelText;
  loadHistory(s);
}

// ------------------------------------------------------------ earlier sessions (leader's history)

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
  // GET /api/assistant/history belongs to the leader's assistant; without it, no panel.
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
// Redraw the chart (no new request) whenever its size changes: the window was resized, or
// the Analysis tab has just been shown.
new ResizeObserver(() => { if (lastSummary) drawChart(lastSummary.tremor.by_time); })
  .observe(document.getElementById("by-time"));
