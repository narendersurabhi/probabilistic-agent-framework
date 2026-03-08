"""Matplotlib plots for policy probabilities and expected free energy."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt


def plot_policy_probabilities(policy_probs: Dict[str, float], out_path: str) -> None:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    labels = list(policy_probs.keys())
    values = [policy_probs[k] for k in labels]
    plt.figure(figsize=(6, 3.5))
    plt.bar(labels, values)
    plt.title("Policy Probabilities")
    plt.ylabel("Probability")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_expected_free_energy(efe: Dict[str, float], out_path: str) -> None:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    labels = list(efe.keys())
    values = [efe[k] for k in labels]
    plt.figure(figsize=(6, 3.5))
    plt.bar(labels, values)
    plt.title("Expected Free Energy by Action")
    plt.ylabel("EFE (lower is better)")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
