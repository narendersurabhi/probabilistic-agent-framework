from evaluation.benchmark_runner import run_benchmark
from evaluation.metrics import (
    argument_accuracy,
    final_answer_accuracy,
    prefix_accuracy,
    sequence_tool_accuracy,
    task_completion_rate,
    tool_selection_accuracy,
)


def test_metrics_basic() -> None:
    rows = [
        {
            "tool_correct": True,
            "arguments_correct": True,
            "completed": True,
            "steps": 1,
            "sequence_exact": True,
            "prefix_ratio": 1.0,
            "final_answer_correct": True,
        },
        {
            "tool_correct": False,
            "arguments_correct": True,
            "completed": False,
            "steps": 2,
            "sequence_exact": False,
            "prefix_ratio": 0.5,
            "final_answer_correct": False,
        },
    ]
    assert tool_selection_accuracy(rows) == 0.5
    assert argument_accuracy(rows) == 1.0
    assert task_completion_rate(rows) == 0.5
    assert sequence_tool_accuracy(rows) == 0.5
    assert prefix_accuracy(rows) == 0.75
    assert final_answer_accuracy(rows) == 0.5


def test_benchmark_runner_executes() -> None:
    results = run_benchmark("evaluation/datasets/benchmark_tasks.json", seed=7, max_steps=3)
    assert "active_inference" in results
    assert "tool_accuracy" in results["standard_llm"]
    assert "sequence_tool_accuracy" in results["react"]


def test_runner_normalizes_selected_tool_format() -> None:
    from evaluation.benchmark_runner import _normalize_result

    result = {
        "selected_tool": "call_calculator",
        "arguments": {"expression": "350 * 0.12"},
        "steps": [{"action": "call_calculator"}],
    }
    norm = _normalize_result(result)
    assert norm["tool"] == "call_calculator"
    assert norm["args"] == {"expression": "350 * 0.12"}
    assert norm["trace"][0]["tool"] == "call_calculator"
