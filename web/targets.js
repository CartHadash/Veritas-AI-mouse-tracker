// targets.js - the things to click in the practice area (team leader, Sun 15 Nov).
//
// Before, every target was the same orange circle. Real screens are full of things of
// different shapes and sizes, and the small ones (a checkbox, a close button) are exactly
// what a shaky cursor misses. So the target now takes turns being six everyday things.
//
// The kinds come round in a fixed order, not at random, so every filter you try gets the
// same mix of easy and hard targets. That keeps the comparison under "Your targets" fair.
//
// Loaded before app.js, which uses three functions from here:
//   makeTarget(width, height)   a new target somewhere in the practice area
//   targetContains(target, p)   is the point p on the target? (this decides hit or miss)
//   drawTarget(ctx, target)     draw it
// To add a kind, add one entry to TARGET_KINDS: its size and how to draw it.

const TARGET_ORANGE = "#d9661a";
const TARGET_WHITE = "#fffdf8";
const TARGET_INK = "#2f1d10";
const TARGET_FONT = '"Instrument Sans", "Avenir Next", "Segoe UI", system-ui, sans-serif';

// Each kind has a size in pixels (w wide, h high; `round: true` means a circle w across) and
// a draw function. (x, y) is the target's centre. The size is ALSO the area that counts as a
// hit, so what you see is exactly what you have to click. Labels beside or under a target
// are only there to make it look real; clicking the label does not count.
const TARGET_KINDS = [
  { name: "round button", w: 44, h: 44, round: true,
    draw(ctx, x, y) {
      fillDisc(ctx, x, y, 22, TARGET_ORANGE);
      fillDisc(ctx, x, y, 5, TARGET_WHITE);
    } },

  { name: "checkbox", w: 26, h: 26,
    draw(ctx, x, y) {
      fillBox(ctx, x, y, 26, 26, 6, TARGET_WHITE);
      ctx.lineWidth = 3;
      ctx.strokeStyle = TARGET_ORANGE;
      ctx.stroke();                                    // the outline of the box just drawn
      drawLabel(ctx, "Remember me", x + 22, y + 6, "left", 17);
    } },

  { name: "folder", w: 58, h: 46,
    draw(ctx, x, y) {
      fillBox(ctx, x - 13, y - 19, 28, 14, 5, "#b9520f");   // the folder's tab, a darker orange
      fillBox(ctx, x, y + 3, 58, 40, 7, TARGET_ORANGE);    // the folder's body
      drawLabel(ctx, "Photos", x, y + 43, "center", 15);
    } },

  { name: "close button", w: 26, h: 26, round: true,
    draw(ctx, x, y) {
      fillDisc(ctx, x, y, 13, TARGET_ORANGE);
      ctx.lineWidth = 2.6;
      ctx.lineCap = "round";
      ctx.strokeStyle = TARGET_WHITE;
      ctx.beginPath();
      ctx.moveTo(x - 5, y - 5); ctx.lineTo(x + 5, y + 5);
      ctx.moveTo(x + 5, y - 5); ctx.lineTo(x - 5, y + 5);
      ctx.stroke();
    } },

  { name: "link", w: 96, h: 26,
    draw(ctx, x, y) {
      ctx.font = `600 18px ${TARGET_FONT}`;
      ctx.textAlign = "center";
      ctx.fillStyle = "#b9520f";
      ctx.fillText("Read more", x, y + 6);
      ctx.fillRect(x - 46, y + 10, 92, 2);             // the underline
    } },

  { name: "Save button", w: 104, h: 42,
    draw(ctx, x, y) {
      fillBox(ctx, x, y, 104, 42, 21, TARGET_ORANGE);
      ctx.font = `700 18px ${TARGET_FONT}`;
      ctx.textAlign = "center";
      ctx.fillStyle = TARGET_WHITE;
      ctx.fillText("Save", x, y + 6);
    } },
];

// ------------------------------------------------------------ small drawing helpers

function fillDisc(ctx, x, y, radius, colour) {
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, 2 * Math.PI);
  ctx.fillStyle = colour;
  ctx.fill();
}

// A filled box with rounded corners, centred on (x, y).
function fillBox(ctx, x, y, w, h, corner, colour) {
  ctx.beginPath();
  ctx.roundRect(x - w / 2, y - h / 2, w, h, corner);
  ctx.fillStyle = colour;
  ctx.fill();
}

function drawLabel(ctx, words, x, y, align, size) {
  ctx.font = `500 ${size}px ${TARGET_FONT}`;
  ctx.textAlign = align;
  ctx.fillStyle = TARGET_INK;
  ctx.fillText(words, x, y);
}

// ------------------------------------------------------------ what app.js uses

let targetsMade = 0;                                   // counts targets, to take the kinds in turn

// A new target at a random place, at least 70 px from every edge so labels fit too.
function makeTarget(width, height) {
  const kind = TARGET_KINDS[targetsMade % TARGET_KINDS.length];
  targetsMade += 1;
  const margin = 70;
  return {
    x: margin + Math.random() * (width - 2 * margin),
    y: margin + Math.random() * (height - 2 * margin),
    shownAt: performance.now(),
    kind,
  };
}

// Is the point p on the target? A circle for round kinds, a rectangle for the others.
function targetContains(target, p) {
  const dx = Math.abs(p.x - target.x), dy = Math.abs(p.y - target.y);
  if (target.kind.round) return Math.hypot(dx, dy) <= target.kind.w / 2;
  return dx <= target.kind.w / 2 && dy <= target.kind.h / 2;
}

function drawTarget(ctx, target) {
  const kind = target.kind;
  // A soft orange glow 8 px larger than the target, so even a small one is easy to find.
  if (kind.round) fillDisc(ctx, target.x, target.y, kind.w / 2 + 8, "rgba(217, 102, 26, 0.16)");
  else fillBox(ctx, target.x, target.y, kind.w + 16, kind.h + 16, 12, "rgba(217, 102, 26, 0.16)");
  kind.draw(ctx, target.x, target.y);
}
