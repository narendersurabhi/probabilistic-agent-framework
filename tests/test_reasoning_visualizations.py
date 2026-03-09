from visualization.information_gain_plot import plot_information_gain
from visualization.trace_graph import plot_trace


def test_trace_and_information_gain_plots(tmp_path):
    trace = [
        {"action": "retrieve_docs"},
        {"action": "call_calculator"},
        {"action": "generate_answer"},
    ]
    trace_path = plot_trace(trace, str(tmp_path / "trace_graph.png"))
    ig_path = plot_information_gain(
        ["retrieve_docs", "call_calculator", "generate_answer"],
        [0.42, 0.11, 0.04],
        str(tmp_path / "information_gain.png"),
    )

    assert trace_path.exists()
    assert ig_path.exists()
