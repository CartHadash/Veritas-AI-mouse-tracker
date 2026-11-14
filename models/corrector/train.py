"""
train.py - step 8: train corrector version 1.

Each training example: a random moment in a shaky training sequence. The network sees the 64
movement steps before it and must output the offset that moves the raw (shaky) cursor
position back onto the clean, intended path. The loss is the squared distance in px.

Every 250 training steps it measures the average distance to the clean path on VALIDATION
sequences; the best version is saved to models/corrector/weights.pt (moved to the CPU first,
so it loads on any computer). Test people are never used here.

Run from the repository folder:
    python models/corrector/train.py
    python models/corrector/train.py --version v2 --scale-augment   # step 12
      (v2: each training sequence's tremor is randomly made 0.5x-2x as large, so the network
       sees the range of sizes different mouse settings (DPI) would produce)
Also saves the loss-curve chart to evaluation/results/figures/corrector_v1_loss.png.
"""

import argparse
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from models.corrector.model import HISTORY, Corrector, count_weights  # noqa: E402
from models.device import best_device  # noqa: E402

DERIVED = ROOT / "data" / "derived"
WEIGHTS = ROOT / "models" / "corrector" / "weights.pt"
FIGURE = ROOT / "evaluation" / "results" / "figures" / "corrector_v1_loss.png"

STEPS = 6000          # training steps (batches)
BATCH = 512
LEARNING_RATE = 1e-3
CHECK_EVERY = 250
SEED = 0


def load(name):
    data = np.load(DERIVED / f"corrector_{name}.npz")
    shaky = torch.tensor(data["shaky"])
    clean = torch.tensor(data["clean"])
    steps = torch.zeros_like(shaky)
    steps[:, 1:] = shaky[:, 1:] - shaky[:, :-1]          # movement steps, first one = 0
    return steps, shaky, clean


def gather(steps, shaky, clean, seq, t, scale=None):
    """For each (sequence, time) pair: the 64 steps ending at t, and the target offset at t.
    scale (optional, one number per example) multiplies the tremor part (shaky - clean)."""
    if scale is None:
        offsets = torch.arange(-HISTORY + 1, 1)
        history = steps[seq[:, None], t[:, None] + offsets[None, :]]      # (batch, 64, 2)
        target = clean[seq, t] - shaky[seq, t]                             # where it should be
        return history, target
    index = t[:, None] + torch.arange(-HISTORY, 1)[None, :]                # 65 positions
    c = clean[seq[:, None], index]
    s = c + scale[:, None, None] * (shaky[seq[:, None], index] - c)       # bigger / smaller tremor
    return s[:, 1:] - s[:, :-1], c[:, -1] - s[:, -1]


def validation_distance(model, data, device, stride=4):
    """Average distance (px) to the clean path over validation sequences (every 4th sample)."""
    steps, shaky, clean = data
    times = torch.arange(HISTORY, steps.shape[1], stride)
    seq = torch.arange(steps.shape[0]).repeat_interleave(len(times))
    t = times.repeat(steps.shape[0])
    total, count = 0.0, 0
    model.eval()
    with torch.no_grad():
        for start in range(0, len(seq), 8192):
            h, target = gather(steps, shaky, clean, seq[start:start + 8192], t[start:start + 8192])
            pred = model(h.to(device)).cpu()
            total += torch.linalg.norm(pred - target, dim=1).sum().item()
            count += len(target)
    model.train()
    return total / count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="v1")
    parser.add_argument("--scale-augment", action="store_true")
    args = parser.parse_args()
    weights = WEIGHTS if args.version == "v1" else WEIGHTS.with_name(f"weights_{args.version}.pt")
    figure = FIGURE.with_name(f"corrector_{args.version}_loss.png")
    torch.manual_seed(SEED)
    rng = np.random.default_rng(SEED)
    device = best_device()
    train, val = load("train"), load("val")
    model = Corrector().to(device)
    optimiser = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    print("Device: %s; weights: %d; training sequences: %d" % (device, count_weights(model), len(train[0])))

    n_seq, length = train[0].shape[:2]
    history_log, best, start_time = [], None, time.time()
    for step in range(1, STEPS + 1):
        seq = torch.tensor(rng.integers(0, n_seq, BATCH))
        t = torch.tensor(rng.integers(HISTORY, length, BATCH))
        scale = None
        if args.scale_augment:      # log-uniform between 0.5 and 2: as often smaller as bigger
            scale = torch.tensor(np.exp(rng.uniform(np.log(0.5), np.log(2.0), BATCH)), dtype=torch.float32)
        h, target = gather(*train, seq, t, scale)
        loss = ((model(h.to(device)) - target.to(device)) ** 2).sum(dim=1).mean()
        optimiser.zero_grad()
        loss.backward()
        optimiser.step()

        if step % CHECK_EVERY == 0:
            dist = validation_distance(model, val, device)
            history_log.append((step, loss.item(), dist))
            marker = ""
            if best is None or dist < best:
                best = dist
                torch.save({k: v.cpu() for k, v in model.state_dict().items()}, weights)
                marker = "  <- best so far, saved"
            print("step %5d  train loss %.2f  validation distance %.2f px  (%.0f s)%s" % (
                step, loss.item(), dist, time.time() - start_time, marker))

    print("Training took %.0f s. Best validation distance %.2f px. Saved %s (%.3f MB)" % (
        time.time() - start_time, best, weights.relative_to(ROOT), weights.stat().st_size / 1e6))

    steps_done, losses, dists = zip(*history_log)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(steps_done, np.sqrt(losses), label="training (RMS error, one batch)")
    ax.plot(steps_done, dists, label="validation (average distance)")
    ax.set(xlabel="training step", ylabel="px off the intended path", title="Corrector %s training" % args.version)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figure, dpi=100)
    print("Saved", figure.relative_to(ROOT))


if __name__ == "__main__":
    main()
