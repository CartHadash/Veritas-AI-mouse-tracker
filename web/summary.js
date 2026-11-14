// summary.js - the session summary page (step 13). Reads GET /api/summary (Contract 2) and
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
  if (!byTime.length) return;

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
  ctx.font = "14px system-ui, sans-serif";

  // Axes and labels: left = share of time (0-100%), right = size in px.
  ctx.fillStyle = "#6e5444";
  ctx.strokeStyle = "#e8c9a8";
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
    ctx.fillStyle = "#6e5444";
    ctx.textAlign = "center";
    ctx.fillText(`min ${m.minute}`, left + i * slot + slot / 2, H - 12);
  });

  // Line: typical size of the shaking.
  ctx.strokeStyle = "#2e7d5b";
  ctx.lineWidth = 3;
  ctx.beginPath();
  byTime.forEach((m, i) => {
    const x = left + i * slot + slot / 2, y = top + plotH * (1 - m.strength_px / maxSize);
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  });
  ctx.stroke();
  ctx.fillStyle = "#2e7d5b";
  byTime.forEach((m, i) => {
    ctx.beginPath();
    ctx.arc(left + i * slot + slot / 2, top + plotH * (1 - m.strength_px / maxSize), 5, 0, 2 * Math.PI);
    ctx.fill();
  });
  ctx.lineWidth = 1;
}

async function load() {
  const s = await (await fetch("/api/summary")).json();

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
  document.getElementById("model-info").textContent =
    `Detector version ${info.detector_version}. On people it had never seen, it missed ${percent(info.missed_cases_rate)} ` +
    `of tremor windows and raised a false alarm on ${percent(info.false_alarm_rate)} of windows without tremor ` +
    `(tested on recordings from a public dataset, not on mouse use). Filter now: ${s.filter.mode}, strength ${s.filter.strength}.`;
}

async function loadAssistant() {
  try {
    const check = await fetch("assistant/assistant.js", { method: "HEAD" });
    if (!check.ok) return;
    const script = document.createElement("script");
    script.src = "assistant/assistant.js";
    document.body.appendChild(script);
  } catch (error) { /* no assistant: fine */ }
}

document.getElementById("reload").addEventListener("click", load);
window.addEventListener("resize", load);
load();
loadAssistant();
