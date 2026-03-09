"""Information-gain plotting helper for probabilistic policy analysis."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt


def plot_information_gain(actions: list[str], scores: list[float], out_path: str) -> Path:
    if len(actions) != len(scores):
        msg = "actions and scores must have the same length"
        raise ValueError(msg)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(7, 4))
    plt.bar(actions, scores, color="#2563eb")
    plt.title("Expected Information Gain")
    plt.ylabel("Gain")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(out)
    plt.close()

    return out
