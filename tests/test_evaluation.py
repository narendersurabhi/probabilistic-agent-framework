from evaluation.benchmark_runner import run_benchmark
from evaluation.metrics import (
    argument_accuracy,
    average_planning_depth,
    final_answer_accuracy,
    first_step_accuracy,
    planning_accuracy,
    prefix_accuracy,
    premature_action_rate,
    sequence_tool_accuracy,
    task_completion_rate,
    tool_selection_accuracy,
)


def test_dataset_bundles_exist_and_match_expected_sizes() -> None:
    import json
    from pathlib import Path

    dataset_specs = {
        "evaluation/datasets/tool_benchmark.json": 100,
        "evaluation/datasets/tool_confusion_tasks.json": 50,
        "evaluation/datasets/uncertainty_tasks.json": 40,
        "evaluation/datasets/argument_accuracy_tasks.json": 40,
        "evaluation/datasets/multi_step_tasks.json": 40,
        "evaluation/datasets/delayed_reward_tasks.json": 40,
    }

    for path, expected_size in dataset_specs.items():
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        assert isinstance(payload, list)
        assert len(payload) == expected_size



def test_delayed_reward_dataset_shape() -> None:
    import json
    from pathlib import Path

    payload = json.loads(Path("evaluation/datasets/delayed_reward_tasks.json").read_text(encoding="utf-8"))
    assert len(payload) == 40
    assert all(item.get("task_type") == "delayed_reward" for item in payload)
    assert all(len(item["expected_tool_sequence"]) >= 3 for item in payload)

def test_tool_benchmark_distribution() -> None:
    import json
    from collections import Counter
    from pathlib import Path

    payload = json.loads(Path("evaluation/datasets/tool_benchmark.json").read_text(encoding="utf-8"))
    counts = Counter(item["task_type"] for item in payload)

    assert counts == {
        "arithmetic": 30,
        "retrieval": 30,
        "multi_step": 20,
        "direct_answer": 20,
    }


def test_metrics_basic() -> None:
    rows = [
        {
            "tool_correct": True,
            "first_step_correct": True,
            "arguments_correct": True,
            "completed": True,
            "steps": 1,
            "sequence_exact": True,
            "prefix_ratio": 1.0,
            "final_answer_correct": True,
        },
        {
            "tool_correct": False,
            "first_step_correct": False,
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
    assert first_step_accuracy(rows) == 0.5
    assert planning_accuracy(rows) == 0.5
    assert average_planning_depth(rows) == 1.5
    assert premature_action_rate(rows) == 0.5


def test_benchmark_runner_executes() -> None:
    results = run_benchmark("evaluation/datasets/benchmark_tasks.json", seed=7, max_steps=3)
    assert "active_inference" in results
    assert "tool_accuracy" in results["standard_llm"]
    assert "sequence_tool_accuracy" in results["react"]
    assert "planning_accuracy" in results["react"]
    assert "average_planning_depth" in results["active_inference"]
    assert "premature_action_rate" in results["active_inference"]
    assert "first_step_accuracy" in results["active_inference"]


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
