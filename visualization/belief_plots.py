"""Matplotlib plotting helpers for experiments and benchmarks."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt


def plot_belief_entropy(entropies: List[float], out_path: str) -> None:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.figure()
    plt.plot(range(len(entropies)), entropies, marker="o")
    plt.title("Belief Entropy Over Time")
    plt.xlabel("Step")
    plt.ylabel("Entropy")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_benchmark_bars(metrics: Dict[str, Dict[str, float]], out_dir: str) -> None:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    agents = list(metrics.keys())
    for key, fname in [
        ("tool_accuracy", "tool_accuracy.png"),
        ("task_completion", "task_completion.png"),
        ("step_efficiency", "steps_per_task.png"),
    ]:
        vals = [metrics[a][key] for a in agents]
        plt.figure()
        plt.bar(agents, vals)
        plt.title(key.replace("_", " ").title())
        plt.tight_layout()
        plt.savefig(str(Path(out_dir) / fname))
        plt.close()
