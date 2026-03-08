"""Belief-state visualization helpers for Active Inference traces."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping


def plot_belief_evolution(trace: Iterable[Mapping[str, object]], out_path: str = "results/plots/belief_evolution.png") -> Path:
    """Plot belief probabilities for knowledge_state values over time."""
    steps = []
    unknown = []
    partial = []
    confident = []

    for snapshot in trace:
        belief = snapshot.get("belief_state", {})
        knowledge = belief.get("knowledge_state", {}) if isinstance(belief, Mapping) else {}
        steps.append(snapshot.get("step", len(steps) + 1))
        unknown.append(float(knowledge.get("unknown", 0.0)))
        partial.append(float(knowledge.get("partial", 0.0)))
        confident.append(float(knowledge.get("confident", 0.0)))

    output = Path(out_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    try:
        import matplotlib.pyplot as plt  # type: ignore

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(steps, unknown, marker="o", label="unknown")
        ax.plot(steps, partial, marker="o", label="partial")
        ax.plot(steps, confident, marker="o", label="confident")
        ax.set_xlabel("Step")
        ax.set_ylabel("Belief Probability")
        ax.set_title("Belief State Evolution")
        ax.legend()
        fig.tight_layout()
        fig.savefig(output)
        plt.close(fig)
    except ModuleNotFoundError:
        output.write_text("matplotlib unavailable for Belief State Evolution\n", encoding="utf-8")

    return output
