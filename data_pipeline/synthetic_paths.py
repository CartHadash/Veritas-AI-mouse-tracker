"""
synthetic_paths.py - step 4: computer-generated mouse movement with NO tremor in it.

This plays the role of "what the person meant to do". Later (step 5) real tremor from the
library is added on top, so we know exactly what the clean movement was.

What a generated path contains, chosen at random one after another:
  - reaches to a target 50-900 px away, lasting 0.3-1.2 s, with the smooth
    speed-up-then-slow-down shape real pointing has ("minimum jerk"), often slightly
    curved, sometimes missing a little and then making a small correction;
  - pauses (holding still) and slow drifts;
  - TREMOR LOOK-ALIKES, which are deliberate and contain no tremor: quick back-and-forth
    wiggles, fast small circles, and zig-zags (sudden direction changes). The detector must
    learn not to call these tremor, so they are the cases we expect false alarms on;
  - a little random sensor jitter on top of everything.

All positions are in pixels, 100 samples per second, on a 1920 x 1080 screen.
Every path comes from a numpy random generator, so a fixed seed gives the same paths.

Run from the repository folder to draw example paths:
    python data_pipeline/synthetic_paths.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RATE = 100                      # samples per second
SCREEN_W, SCREEN_H = 1920, 1080
MARGIN = 60                     # keep targets this far from the screen edge

# What each sample is part of (saved alongside the path, used later to describe windows).
STILL, REACH, CORRECTION, DRIFT, WIGGLE, CIRCLE, ZIGZAG = range(7)
KIND_NAMES = ["still", "reach", "correction", "drift", "wiggle", "circle", "zigzag"]
LOOKALIKES = (WIGGLE, CIRCLE, ZIGZAG)

FIGURES = Path(__file__).resolve().parents[1] / "evaluation" / "results" / "figures"


def minimum_jerk(n):
    """Fraction of the way travelled at each of n samples: smooth start and stop."""
    s = np.linspace(0, 1, n)
    return 10 * s ** 3 - 15 * s ** 4 + 6 * s ** 5


def move(start, end, seconds, curve=0.0):
    """Smooth movement from start to end. curve bends the path sideways (0 = straight)."""
    n = max(2, int(round(seconds * RATE)))
    s = minimum_jerk(n)[:, None]
    path = start + s * (end - start)
    direction = end - start
    sideways = np.array([-direction[1], direction[0]])        # perpendicular to the movement
    return path + curve * np.sin(np.pi * s) * sideways


def random_target(rng, here):
    """A point 50-900 px away from here, inside the screen."""
    for _ in range(100):
        distance = rng.uniform(50, 900)
        angle = rng.uniform(0, 2 * np.pi)
        target = here + distance * np.array([np.cos(angle), np.sin(angle)])
        if MARGIN < target[0] < SCREEN_W - MARGIN and MARGIN < target[1] < SCREEN_H - MARGIN:
            return target
    return np.array([SCREEN_W / 2, SCREEN_H / 2])


def reach(rng, here):
    """A reach to a target, maybe curved, maybe with a miss and a correction."""
    target = random_target(rng, here)
    distance = np.linalg.norm(target - here)
    seconds = np.clip(0.3 + distance / 900 * 0.7 + rng.normal(0, 0.1), 0.3, 1.2)
    curve = rng.normal(0, 0.08)
    # Land slightly off target 60% of the time (an overshoot or undershoot of a few %)...
    miss = rng.random() < 0.6
    landing = target + (rng.normal(0, 0.04 * distance, 2) if miss else 0)
    parts = [(move(here, landing, seconds, curve), REACH)]
    # ...then make a small, short correction to the real target.
    if miss:
        parts.append((move(landing, target, rng.uniform(0.15, 0.35)), CORRECTION))
    return parts


def pause(rng, here):
    return [(np.repeat(here[None], int(rng.uniform(0.2, 1.5) * RATE), axis=0), STILL)]


def drift(rng, here):
    """Slow movement, 5-40 px per second."""
    seconds = rng.uniform(0.5, 2.0)
    angle = rng.uniform(0, 2 * np.pi)
    end = here + rng.uniform(5, 40) * seconds * np.array([np.cos(angle), np.sin(angle)])
    return [(move(here, end, seconds, rng.normal(0, 0.2)), DRIFT)]


def wiggle(rng, here):
    """Deliberate back-and-forth, 2-6 times a second, 5-40 px wide (e.g. 'shaking' a window)."""
    seconds, freq, size = rng.uniform(0.5, 1.5), rng.uniform(2, 6), rng.uniform(5, 40)
    t = np.arange(int(seconds * RATE)) / RATE
    angle = rng.uniform(0, np.pi)
    envelope = np.sin(np.pi * t / seconds)               # starts and ends gently
    offset = size * envelope * np.sin(2 * np.pi * freq * t)
    return [(here + offset[:, None] * np.array([np.cos(angle), np.sin(angle)]), WIGGLE)]


def circle(rng, here):
    """Fast small circles, 1.5-4 per second, radius 5-30 px (e.g. circling a word)."""
    seconds, freq, radius = rng.uniform(0.5, 1.5), rng.uniform(1.5, 4), rng.uniform(5, 30)
    t = np.arange(int(seconds * RATE)) / RATE
    envelope = np.sin(np.pi * t / seconds)
    phase = 2 * np.pi * freq * t * rng.choice([-1, 1])
    offset = radius * envelope[:, None] * np.stack([np.cos(phase) - 1, np.sin(phase)], axis=1)
    return [(here + offset, CIRCLE)]


def zigzag(rng, here):
    """3-6 short fast moves with sudden changes of direction."""
    parts, point = [], here
    for _ in range(rng.integers(3, 7)):
        angle = rng.uniform(0, 2 * np.pi)
        end = point + rng.uniform(20, 80) * np.array([np.cos(angle), np.sin(angle)])
        end = np.clip(end, MARGIN, [SCREEN_W - MARGIN, SCREEN_H - MARGIN])
        parts.append((move(point, end, rng.uniform(0.1, 0.2)), ZIGZAG))
        point = end
    return parts


def glide(rng, here):
    """Step 12: a long, smooth, continuous curve (1-3 s at 50-300 px/s), like dragging or
    slowly following a line. It never stops, which our first detector found suspicious."""
    seconds = rng.uniform(1.0, 3.0)
    t = np.arange(int(seconds * RATE)) / RATE
    speed = rng.uniform(50, 300)
    heading = rng.uniform(0, 2 * np.pi) + rng.uniform(-1.5, 1.5) * np.sin(2 * np.pi * t / seconds)
    steps = speed / RATE * np.stack([np.cos(heading), np.sin(heading)], axis=1)
    path = here + np.cumsum(steps, axis=0)
    return [(np.clip(path, MARGIN, [SCREEN_W - MARGIN, SCREEN_H - MARGIN]), DRIFT)]


# How often each kind of event is chosen. Look-alikes are about a quarter of all events.
EVENTS = [(reach, 0.40), (pause, 0.20), (drift, 0.12), (wiggle, 0.10), (circle, 0.09), (zigzag, 0.09)]

# Step 12: movement that never pauses (reaches straight into glides and drifts).
CONTINUOUS_EVENTS = [(reach, 0.40), (glide, 0.45), (drift, 0.15)]


def generate_path(rng, n_samples, jitter_px=None, events=EVENTS):
    """
    One synthetic path of n_samples. Returns:
      xy   - (n_samples, 2) positions in pixels, float32
      kind - (n_samples,) what each sample is part of (STILL, REACH, ... see top of file)
    """
    functions = [f for f, _ in events]
    weights = np.array([w for _, w in events])
    here = np.array([rng.uniform(MARGIN, SCREEN_W - MARGIN), rng.uniform(MARGIN, SCREEN_H - MARGIN)])
    xy_parts, kind_parts, total = [], [], 0
    while total < n_samples:
        event = functions[rng.choice(len(functions), p=weights / weights.sum())]
        for xy, kind in event(rng, here):
            xy_parts.append(xy)
            kind_parts.append(np.full(len(xy), kind))
            total += len(xy)
            here = xy[-1]
    xy = np.concatenate(xy_parts)[:n_samples]
    kind = np.concatenate(kind_parts)[:n_samples]
    # Sensor jitter: tiny random noise, a different amount for each path (0-0.3 px).
    if jitter_px is None:
        jitter_px = rng.uniform(0, 0.3)
    xy = xy + rng.normal(0, jitter_px, xy.shape)
    return xy.astype(np.float32), kind.astype(np.int8)


def plot_examples(seed=0):
    rng = np.random.default_rng(seed)
    paths = [generate_path(rng, 1024) for _ in range(6)]
    colours = plt.cm.tab10(np.arange(len(KIND_NAMES)))

    fig = plt.figure(figsize=(13, 11))
    for i, (xy, kind) in enumerate(paths):
        ax = fig.add_subplot(3, 3, i + 1)
        ax.plot(xy[:, 0], xy[:, 1], color="lightgrey", linewidth=0.8, zorder=1)
        for k, name in enumerate(KIND_NAMES):
            mask = kind == k
            ax.scatter(xy[mask, 0], xy[mask, 1], s=2, color=colours[k], label=name, zorder=2)
        ax.set(xlim=(0, SCREEN_W), ylim=(SCREEN_H, 0), title="path %d (10.24 s)" % (i + 1))
        ax.set_aspect("equal")
        ax.tick_params(labelsize=7)
    fig.axes[0].legend(fontsize=7, markerscale=4, loc="lower left")

    # Speed over time for the first path: the reaches are bell-shaped, look-alikes are fast and jumpy.
    xy, kind = paths[0]
    speed = np.linalg.norm(np.diff(xy, axis=0), axis=1) * RATE
    ax = fig.add_subplot(3, 1, 3)
    t = np.arange(len(speed)) / RATE
    ax.plot(t, speed, color="black", linewidth=0.7)
    for k, name in enumerate(KIND_NAMES):
        mask = kind[1:] == k
        ax.scatter(t[mask], speed[mask], s=3, color=colours[k])
    ax.set(xlabel="time (s)", ylabel="speed (px/s)", title="Path 1: speed over time (colours as above)")

    fig.tight_layout()
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / "synthetic_paths_examples.png", dpi=90)
    plt.close(fig)

    # Print a quick summary of what was generated, over many paths.
    rng = np.random.default_rng(seed + 1)
    kinds = np.concatenate([generate_path(rng, 1024)[1] for _ in range(500)])
    print("Share of time in each kind of movement (500 paths of 10.24 s, seed %d):" % (seed + 1))
    for k, name in enumerate(KIND_NAMES):
        print("  %-11s %5.1f%%" % (name, 100 * np.mean(kinds == k)))
    print("Saved evaluation/results/figures/synthetic_paths_examples.png")


if __name__ == "__main__":
    plot_examples()
