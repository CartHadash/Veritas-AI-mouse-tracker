"""
model.py - the corrector network.

Input : the last 64 cursor movement steps (dx, dy), i.e. 0.64 s at 100 samples per second.
        Steps, not screen positions, so it works anywhere on the screen.
Output: where the cursor should be right now, as an offset (dx, dy) from the raw position.

It is CAUSAL: it only ever sees past and current samples, so it can run live.

Shape of the network: three 1-D convolution layers. Each layer looks at a few neighbouring
time steps; the gaps between the steps they look at double each layer (1, 2, 4), so the last
layer "sees" a wide stretch of the past. Then one linear layer turns the features at the
newest time step into the (dx, dy) offset. About 10,000 weights.
"""

import torch
from torch import nn

HISTORY = 64          # samples of history the network sees
SCALE = 10.0          # px: steps and offsets are divided by this so numbers stay near 1


class Corrector(nn.Module):
    def __init__(self, channels=32):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Conv1d(2, channels, kernel_size=5, dilation=1), nn.ReLU(),
            nn.Conv1d(channels, channels, kernel_size=5, dilation=2), nn.ReLU(),
            nn.Conv1d(channels, channels, kernel_size=5, dilation=4), nn.ReLU(),
        )
        self.out = nn.Linear(channels, 2)

    def forward(self, steps):
        """steps: (batch, HISTORY, 2) movement steps in px. Returns (batch, 2) offset in px."""
        x = (steps / SCALE).transpose(1, 2)        # -> (batch, 2, HISTORY)
        features = self.layers(x)[:, :, -1]         # features at the newest time step
        return self.out(features) * SCALE


def count_weights(model):
    return sum(p.numel() for p in model.parameters())
