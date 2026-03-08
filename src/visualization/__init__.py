"""Visualization helpers for benchmark and Active Inference traces."""

from src.visualization.belief_plots import plot_belief_evolution
from src.visualization.free_energy_plot import plot_expected_free_energy
from src.visualization.policy_plots import plot_policy_probabilities

__all__ = [
    "plot_belief_evolution",
    "plot_policy_probabilities",
    "plot_expected_free_energy",
]
