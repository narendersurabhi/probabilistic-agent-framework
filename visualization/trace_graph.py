"""Simple reasoning-trace graph visualization utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt


def plot_trace(trace: list[dict[str, Any]], out_path: str) -> Path:
    """Render a simple directed reasoning graph from a linear trace."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    labels = [str(step.get("action", f"step_{idx + 1}")) for idx, step in enumerate(trace)]

    plt.figure(figsize=(8, 2.8))
    ax = plt.gca()
    ax.axis("off")

    for idx, label in enumerate(labels):
        x = idx * 2.2
        ax.text(
            x,
            0,
            label,
            ha="center",
            va="center",
            bbox={"boxstyle": "round,pad=0.35", "facecolor": "#dbeafe", "edgecolor": "#1d4ed8"},
        )
        if idx < len(labels) - 1:
            ax.annotate(
                "",
                xy=(x + 1.35, 0),
                xytext=(x + 0.8, 0),
                arrowprops={"arrowstyle": "->", "color": "#1f2937", "lw": 1.2},
            )

    ax.set_xlim(-1, max(2, len(labels) * 2.2 - 1))
    ax.set_ylim(-1, 1)
    plt.title("Reasoning Trace Graph")
    plt.tight_layout()
    plt.savefig(out)
    plt.close()
    return out
