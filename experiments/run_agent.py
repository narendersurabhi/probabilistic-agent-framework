"""Run a full active inference loop example."""

from __future__ import annotations

import json

import numpy as np

from evaluation.harness import AgentHarness
from visualization.belief_plots import plot_belief_entropy


def main() -> None:
    harness = AgentHarness()
    query = "Find documents about reinforcement learning"
    rows = []
    entropies = []
    for step in range(3):
        rec = harness.run_step(step, query, expected_tool="retrieve_docs", arguments={"query": query})
        rows.append(rec)
        p = np.array(list(rec["belief_state"].values()))
        entropies.append(float(-(p * np.log(p + 1e-9)).sum()))
    for r in rows:
        print(json.dumps(r, indent=2))
    plot_belief_entropy(entropies, "results/plots/belief_entropy.png")


if __name__ == "__main__":
    main()
