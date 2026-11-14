"""
device.py - pick which chip PyTorch should use, in one place for the whole project.

Order of preference:
  "cuda" - an NVIDIA graphics card (some Windows PCs)
  "mps"  - the Apple Silicon graphics chip (our Macs)
  "cpu"  - the normal processor (works everywhere)

Our models are small, so any of the three is fine. Every training script calls
best_device() instead of choosing for itself, so behaviour is the same everywhere.

Run on its own to see which one this machine uses:
    python models/device.py
"""

import torch


def best_device():
    """Return the best available PyTorch device as a torch.device."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


if __name__ == "__main__":
    print("This machine will use:", best_device())
