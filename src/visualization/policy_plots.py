"""Policy-probability visualization helpers for Active Inference traces."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping


def plot_policy_probabilities(trace: Iterable[Mapping[str, object]], out_path: str = "results/plots/policy_probabilities.png") -> Path:
    """Plot per-action policy probabilities across agent steps."""
    steps = []
    retrieve = []
    calculator = []
    generate = []

    for snapshot in trace:
        probs = snapshot.get("policy_probabilities", {})
        probs = probs if isinstance(probs, Mapping) else {}
        steps.append(snapshot.get("step", len(steps) + 1))
        retrieve.append(float(probs.get("retrieve_docs", 0.0)))
        calculator.append(float(probs.get("call_calculator", 0.0)))
        generate.append(float(probs.get("generate_answer", 0.0)))

    output = Path(out_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    try:
        import matplotlib.pyplot as plt  # type: ignore

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(steps, retrieve, marker="o", label="retrieve_docs")
        ax.plot(steps, calculator, marker="o", label="call_calculator")
        ax.plot(steps, generate, marker="o", label="generate_answer")
        ax.set_xlabel("Step")
        ax.set_ylabel("Policy Probability")
        ax.set_title("Policy Probabilities Over Time")
        ax.legend()
        fig.tight_layout()
        fig.savefig(output)
        plt.close(fig)
    except ModuleNotFoundError:
        output.write_text("matplotlib unavailable for Policy Probabilities Over Time\n", encoding="utf-8")

    return output
