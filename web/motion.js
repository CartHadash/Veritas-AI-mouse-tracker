// motion.js - the moving parts of the "colour and movement" layer (team leader, Sun 15 Nov).
// Plain JavaScript in its own file, so it never clashes with app.js. With motion.css it is an
// add-on: delete their two lines in index.html and the page is back to the plain look.
//
// What moves:
//   1. a quiet wave along the bottom of the top bar: shaky on the left, calm on the right
//   2. the logo itself
//   3. the picture on "How it works": a shaky line goes into the detector and comes out steady
// Parts 1 and 2 follow the LIVE tremor score (they shake more when the detector sees tremor).
// Part 3 is an illustration with made-up movement, and says so on the page.
//
// It also puts a small icon in front of the card titles, gives the assistant button one
// nudge, and makes the "Save my session" picture (the last parts of this file).
//
// It reads three things other scripts own, and changes none of them:
//   latest, threshold (app.js): the detector's last reply and its cut-off
//   lastSummary (summary.js): the numbers on the Analysis tab

(function () {
  // People can ask their computer for less motion. Then every picture is drawn once, still.
  const still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // This script adds its own pieces to the page, so index.html needs nothing but the two
  // lines that load motion.css and motion.js.
  // (a) the canvas for the wave, as the first thing inside the top bar
  const wave = document.createElement("canvas");
  wave.id = "wave";
  wave.setAttribute("aria-hidden", "true");
  document.querySelector(".topbar").prepend(wave);
  // (b) the picture on "How it works", just above the three steps
  const artBox = document.createElement("div");
  artBox.className = "how-art";
  artBox.innerHTML = `<canvas id="how-art" aria-label="Picture: a shaky line passes the detector and comes out steady"></canvas>
    <p>An illustration with made-up movement, not your own data.</p>`;
  document.querySelector(".steps").before(artBox);
  const art = artBox.querySelector("canvas");
  // (c) the "Save my session" button, next to Refresh on the Analysis tab
  const reload = document.getElementById("reload");
  const actions = document.createElement("div");
  actions.className = "actions";
  reload.before(actions);
  const saveButton = document.createElement("button");
  saveButton.className = "btn";
  saveButton.textContent = "Save my session as a picture";
  actions.append(saveButton, reload);

  const logo = document.querySelector(".brand svg path");

  // ---------------------------------------------------------- how shaky is it right now?

  // A number from 0 (calm) to 1 (strong tremor) taken from the detector's live score.
  // The score reaches the cut-off at 0.5 here, so the pictures react before and after it.
  function liveShake() {
    if (typeof latest === "undefined" || !latest || latest.score === null) return 0;
    if (document.querySelector(".meter-card.paused")) return 0;     // the hand has stopped
    return Math.min(1, latest.score / (2 * threshold));
  }
  // The pictures follow that number slowly (a little closer each frame), so they swell and
  // settle instead of flickering.
  let level = 0;

  // Make a canvas sharp on high-resolution screens; returns its size in CSS pixels.
  function fit(canvas) {
    const W = canvas.clientWidth, H = canvas.clientHeight;
    const ratio = window.devicePixelRatio || 1;
    if (canvas.width !== Math.round(W * ratio) || canvas.height !== Math.round(H * ratio)) {
      canvas.width = Math.round(W * ratio);
      canvas.height = Math.round(H * ratio);
    }
    const ctx = canvas.getContext("2d");
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    ctx.clearRect(0, 0, W, H);
    return { ctx, W, H };
  }

  // 0 below `from`, 1 above `to`, and a smooth S-shaped rise in between.
  function ramp(from, to, x) {
    const k = Math.min(1, Math.max(0, (x - from) / (to - from)));
    return k * k * (3 - 2 * k);
  }

  // ---------------------------------------------------------- 1. the wave behind the top bar

  // Three thin lines flow along the bottom edge of the bar. Each is a slow swell plus a
  // small fast shake; the shake is there at the left edge and gone by the middle. It is kept
  // faint and slow on purpose, so it never pulls the eye from the page. `t` is in seconds.
  function drawWave(t) {
    const { ctx, W, H } = fit(wave);
    if (W === 0) return;
    const shakeSize = 1.5 + 5 * level;                 // px; grows with the live tremor score
    for (let k = 0; k < 3; k++) {
      ctx.beginPath();
      for (let x = -4; x <= W + 4; x += 5) {
        const swell = 3 * Math.sin(x / 210 + t * 0.3 + k * 1.3);
        const shake = shakeSize * (1 - ramp(0.1, 0.5, x / W)) * Math.sin(x * 0.42 + t * 7 + k * 2.1);
        const y = H * (0.3 + 0.22 * k) + swell + shake;
        if (x === -4) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.lineWidth = 1.3;
      ctx.strokeStyle = k === 1 ? "rgba(169, 230, 204, 0.38)" : "rgba(255, 255, 255, 0.13)";
      ctx.stroke();
    }
  }

  // ---------------------------------------------------------- 2. the logo

  // The logo is a zigzag that turns into a straight line. These are how far each corner of
  // the zigzag sits above (-) or below (+) the middle, in the logo's own units.
  const ZIGZAG = [0, -9, 7, -8, 6, -5, 3];
  function drawLogo(t) {
    // At rest the zigzag is a little smaller; with strong tremor it grows and its corners wobble.
    const size = 0.8 + 0.45 * level;
    let d = "";
    ZIGZAG.forEach((offset, i) => {
      const wobble = still ? 0 : 2.5 * level * Math.sin(t * 16 + i * 1.7);
      const y = Math.min(26, Math.max(2, 14 + offset * size + wobble));
      d += `${i === 0 ? "M" : "L"}${2 + 4 * i} ${y.toFixed(1)} `;
    });
    logo.setAttribute("d", d + "Q29 14 32 14 H58");
  }

  // ---------------------------------------------------------- 3. the "How it works" picture

  // One line crosses the picture from left to right, drawn by a travelling dot:
  //   left third   gold, shaky   = the hand's movement as the page reads it
  //   the middle   orange ring   = the detector noticing the fast rhythm
  //   right third  green, calm   = the corrected cursor
  // The movement here is made up for the picture (a slow curve plus a fast shake).
  const ART_SECONDS = 7;                               // one pass, then it starts again
  function intended(x, W, H) { return H * 0.46 + 30 * Math.sin((x / W) * 2 * Math.PI); }
  function drawArt(t) {
    const { ctx, W, H } = fit(art);
    if (W === 0) return;                               // the tab is hidden
    const gate = W / 2;
    // How far the dot has come: it crosses in 5.5 s, then rests until the pass ends.
    const reach = still ? W : Math.min(1, (t % ART_SECONDS) / 5.5) * W;

    // The shake is full size on the left and is gone 70 px after the detector.
    const lineY = (x) => intended(x, W, H) + 11 * (1 - ramp(gate - 10, gate + 70, x)) * Math.sin(x * 0.55);

    ctx.lineWidth = 4;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    // Draw the line in two colours: gold up to the detector, green after it.
    for (const [from, to, colour] of [[24, gate, "#d39a16"], [gate, W - 24, "#1f6f57"]]) {
      const end = Math.min(to, reach);
      if (end <= from) continue;
      ctx.beginPath();
      for (let x = from; x <= end; x += 2) {
        if (x === from) ctx.moveTo(x, lineY(x)); else ctx.lineTo(x, lineY(x));
      }
      ctx.strokeStyle = colour;
      ctx.stroke();
    }

    // The detector: an orange ring on the line. It swells for a moment as the dot passes.
    const passing = still ? 0 : Math.max(0, 1 - Math.abs(reach - gate) / 60);
    ctx.lineWidth = 4;
    ctx.strokeStyle = "#c2540f";
    ctx.fillStyle = `rgba(194, 84, 15, ${(0.1 + 0.2 * passing).toFixed(2)})`;
    ctx.beginPath();
    ctx.arc(gate, intended(gate, W, H), 24 + 8 * passing, 0, 2 * Math.PI);
    ctx.fill();
    ctx.stroke();

    // The travelling dot, in the colour of the part it is on.
    if (!still && reach > 24 && reach < W - 24) {
      ctx.fillStyle = reach < gate ? "#d39a16" : "#1f6f57";
      ctx.beginPath();
      ctx.arc(reach, lineY(reach), 8, 0, 2 * Math.PI);
      ctx.fill();
    }

    // A word under each part.
    ctx.font = '600 15px "Instrument Sans", "Avenir Next", "Segoe UI", system-ui, sans-serif';
    ctx.textAlign = "center";
    const words = [[W * 0.2, "your hand's movement", "#8a5d00"], [gate, "the detector", "#c2540f"], [W * 0.8, "the corrected cursor", "#1f6f57"]];
    for (const [x, word, colour] of words) {
      ctx.fillStyle = colour;
      ctx.fillText(word, x, H - 10);
    }
  }

  // ---------------------------------------------------------- the loop that redraws them

  function frame(ms) {
    const t = ms / 1000;
    level += (liveShake() - level) * 0.06;             // drift towards the live value
    drawWave(t);
    drawLogo(t);
    drawArt(t);
    if (!still) requestAnimationFrame(frame);
  }
  if (still) {
    // No motion wanted: draw each picture once now, and again when its size changes.
    frame(0);
    new ResizeObserver(() => frame(0)).observe(wave);
    new ResizeObserver(() => frame(0)).observe(art);
  } else {
    requestAnimationFrame(frame);
  }

  // ---------------------------------------------------------- icons in front of card titles

  // Each entry: which title, the badge's colour, and the icon's lines (SVG shapes on a 24 x 24
  // grid). pathLength="1" tells the browser to treat every line as 1 long, whatever its real
  // length, so one CSS rule can make them all "draw themselves" (see motion.css, part g).
  const ICONS = [
    { title: ".meter-card h2", colour: "", lines: '<path pathLength="1" d="M2 12h4l2-6 4 12 3-9 2 3h5"/>' },            // a pulse
    { title: ".card:has(#strength) h2", colour: "gold",                                                                // sliders
      lines: '<path pathLength="1" d="M4 7h16M4 17h16"/><circle pathLength="1" cx="9" cy="7" r="2.6"/><circle pathLength="1" cx="15" cy="17" r="2.6"/>' },
    { title: ".card:has(#tally) h2", colour: "clay",                                                                   // a target
      lines: '<circle pathLength="1" cx="12" cy="12" r="9"/><circle pathLength="1" cx="12" cy="12" r="4"/>' },
    { title: ".chart-panel h2", colour: "clay", lines: '<path pathLength="1" d="M5 20V11M12 20V4M19 20v-6"/>' },        // bars
    { title: "#history h2", colour: "gold", lines: '<circle pathLength="1" cx="12" cy="12" r="9"/><path pathLength="1" d="M12 7v5l3 3"/>' },   // a clock
    { title: "#laptop h2", colour: "ink", lines: '<path pathLength="1" d="M5 6h14v10H5zM2 19h20"/>' },                  // a laptop
  ];
  for (const icon of ICONS) {
    const title = document.querySelector(icon.title);
    if (!title) continue;                              // that card is not on this page
    const badge = document.createElement("span");
    badge.className = "title-icon " + icon.colour;
    badge.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true">${icon.lines}</svg>`;
    title.prepend(badge);
  }

  // ---------------------------------------------------------- one nudge from the assistant button

  // After five clicks on targets there are numbers worth asking about, so the assistant's
  // button wiggles once. `tally` belongs to app.js; we only read it, every two seconds.
  const nudgeTimer = setInterval(() => {
    if (typeof tally === "undefined") return;
    const clicks = Object.values(tally).reduce((sum, row) => sum + row.hits + row.misses, 0);
    const button = document.querySelector(".assistant-launcher");
    if (clicks >= 5 && button) {
      button.classList.add("nudge");
      clearInterval(nudgeTimer);                       // once is enough
    }
  }, 2000);

  // ---------------------------------------------------------- "Save my session": a picture to keep

  // Draws the main numbers of the Analysis tab on one 1200 x 630 picture and saves it as a
  // PNG file through the browser's normal download. Nothing is sent anywhere.
  // (When the builder's spiral exercise exists, its drawing can be added here.)
  function saveCard() {
    const s = typeof lastSummary === "undefined" ? null : lastSummary;
    if (!s) return;
    const W = 1200, H = 630;
    const canvas = document.createElement("canvas");
    canvas.width = W;
    canvas.height = H;
    const ctx = canvas.getContext("2d");
    const FONT = '"Bricolage Grotesque", "Instrument Sans", "Avenir Next", "Segoe UI", system-ui, sans-serif';
    const text = (words, x, y, font, colour, align = "left") => {
      ctx.font = `${font} ${FONT}`;
      ctx.fillStyle = colour;
      ctx.textAlign = align;
      ctx.fillText(words, x, y);
    };

    // Paper background and the green band with the name and the date.
    ctx.fillStyle = "#f5ecdd";
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = "#1a5c49";
    ctx.fillRect(0, 0, W, 104);
    text("Steady Pointer", 56, 66, "700 40px", "#fffdf8");
    text("Session of " + new Date().toLocaleDateString(undefined, { day: "numeric", month: "long", year: "numeric" }),
      W - 56, 64, "500 26px", "#dcefe6", "right");

    // The ring: share of analysed time with tremor-like movement.
    const share = s.tremor.detected_share;
    const cx = 220, cy = 318, r = 118;
    ctx.lineWidth = 30;
    ctx.lineCap = "round";
    ctx.strokeStyle = "#f3e6d4";
    ctx.beginPath(); ctx.arc(cx, cy, r, 0, 2 * Math.PI); ctx.stroke();
    if (share) {
      ctx.strokeStyle = "#c2540f";
      ctx.beginPath(); ctx.arc(cx, cy, r, -Math.PI / 2, -Math.PI / 2 + 2 * Math.PI * share); ctx.stroke();
    }
    text(percent(share), cx, cy + 22, "700 62px", "#2f1d10", "center");
    text("of the analysed time had", cx, cy + r + 62, "500 23px", "#6a5241", "center");
    text("tremor-like movement", cx, cy + r + 92, "500 23px", "#6a5241", "center");

    // Four numbers in two columns.
    const stats = [
      ["Steadiness score (0 to 1)", s.usage.steadiness_score === null ? "-" : number(s.usage.steadiness_score, 2)],
      ["Clicks that hit the target", percent(s.usage.click_accuracy)],
      ["Active time", `${number(s.session.minutes_active)} min`],
      ["Typical rhythm of the shaking", s.tremor.typical_frequency_hz ? `${number(s.tremor.typical_frequency_hz)} Hz` : "-"],
    ];
    stats.forEach(([label, value], i) => {
      const x = 470 + (i % 2) * 350, y = 222 + Math.floor(i / 2) * 150;
      text(value, x, y, "700 58px", "#2f1d10");
      text(label, x, y + 38, "500 22px", "#6a5241");
    });

    // Which filter, and the required note when demo tremor was on.
    const mode = (typeof MODE_NAMES !== "undefined" && MODE_NAMES[s.filter.mode]) || s.filter.mode;
    text(`Filter: ${mode}, strength ${s.filter.strength}`, 470, 500, "600 24px", "#1f6f57");
    if (s.notes.some((note) => note.startsWith("Tremor replay"))) {
      text("Demo mode was on: part of the tremor was a replayed recording", 470, 536, "500 20px", "#6b2c00");
      text("from a public dataset, not this person's own movement.", 470, 562, "500 20px", "#6b2c00");
    }
    text("This project is a prototype and is not medical advice.", W / 2, H - 22, "700 21px", "#2f1d10", "center");

    // Hand the picture to the browser as a download.
    canvas.toBlob((blob) => {
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "steady-pointer-session.png";
      link.click();
      URL.revokeObjectURL(link.href);
    }, "image/png");
  }
  saveButton.addEventListener("click", saveCard);
})();
