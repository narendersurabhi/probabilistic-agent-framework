from pathlib import Path

from src.visualization.belief_plots import plot_belief_evolution
from src.visualization.free_energy_plot import plot_expected_free_energy
from src.visualization.policy_plots import plot_policy_probabilities


def _sample_trace() -> list[dict[str, object]]:
    return [
        {
            "step": 1,
            "belief_state": {"knowledge_state": {"unknown": 0.7, "partial": 0.2, "confident": 0.1}},
            "policy_probabilities": {
                "retrieve_docs": 0.65,
                "call_calculator": 0.25,
                "generate_answer": 0.10,
            },
            "expected_free_energy": {
                "retrieve_docs": 1.2,
                "call_calculator": 2.1,
                "generate_answer": 2.5,
            },
        },
        {
            "step": 2,
            "belief_state": {"knowledge_state": {"unknown": 0.3, "partial": 0.5, "confident": 0.2}},
            "policy_probabilities": {
                "retrieve_docs": 0.25,
                "call_calculator": 0.60,
                "generate_answer": 0.15,
            },
            "expected_free_energy": {
                "retrieve_docs": 2.0,
                "call_calculator": 1.4,
                "generate_answer": 2.1,
            },
        },
    ]


def test_trace_plot_builders_write_output(tmp_path: Path) -> None:
    trace = _sample_trace()

    belief = plot_belief_evolution(trace, str(tmp_path / "belief.png"))
    policy = plot_policy_probabilities(trace, str(tmp_path / "policy.png"))
    efe = plot_expected_free_energy(trace, str(tmp_path / "efe.png"))

    assert belief.exists()
    assert policy.exists()
    assert efe.exists()
