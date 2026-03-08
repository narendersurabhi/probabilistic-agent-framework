"""Expected free-energy visualization helpers for Active Inference traces."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping


def plot_expected_free_energy(trace: Iterable[Mapping[str, object]], out_path: str = "results/plots/free_energy.png") -> Path:
    """Plot expected free energy per action across agent steps."""
    steps = []
    retrieve = []
    calculator = []
    generate = []

    for snapshot in trace:
        efe = snapshot.get("expected_free_energy", {})
        efe = efe if isinstance(efe, Mapping) else {}
        steps.append(snapshot.get("step", len(steps) + 1))
        retrieve.append(float(efe.get("retrieve_docs", 0.0)))
        calculator.append(float(efe.get("call_calculator", 0.0)))
        generate.append(float(efe.get("generate_answer", 0.0)))

    output = Path(out_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    try:
        import matplotlib.pyplot as plt  # type: ignore

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(steps, retrieve, marker="o", label="retrieve_docs")
        ax.plot(steps, calculator, marker="o", label="call_calculator")
        ax.plot(steps, generate, marker="o", label="generate_answer")
        ax.set_xlabel("Step")
        ax.set_ylabel("Expected Free Energy")
        ax.set_title("Expected Free Energy per Action")
        ax.legend()
        fig.tight_layout()
        fig.savefig(output)
        plt.close(fig)
    except ModuleNotFoundError:
        output.write_text("matplotlib unavailable for Expected Free Energy per Action\n", encoding="utf-8")

    return output
