from src.evaluation.metrics import (
    aggregate_metrics,
    argument_accuracy,
    first_step_accuracy,
    sequence_accuracy,
    task_completion_rate,
    tool_selection_accuracy,
)


def test_metric_functions() -> None:
    rows = [
        {
            "tool_correct": True,
            "arguments_correct": True,
            "arguments_evaluated": True,
            "sequence_correct": True,
            "sequence_evaluated": True,
            "first_step_correct": True,
            "completed": True,
        },
        {
            "tool_correct": False,
            "arguments_correct": False,
            "arguments_evaluated": True,
            "sequence_correct": False,
            "sequence_evaluated": True,
            "first_step_correct": False,
            "completed": False,
        },
        {
            "tool_correct": True,
            "arguments_correct": True,
            "arguments_evaluated": False,
            "sequence_correct": False,
            "sequence_evaluated": False,
            "first_step_correct": True,
            "completed": True,
        },
    ]

    assert tool_selection_accuracy(rows) == 2 / 3
    assert argument_accuracy(rows) == 0.5
    assert sequence_accuracy(rows) == 0.5
    assert first_step_accuracy(rows) == 2 / 3
    assert task_completion_rate(rows) == 2 / 3


def test_aggregate_metrics_keys() -> None:
    out = aggregate_metrics([])
    assert set(out.keys()) == {
        "tool_selection_accuracy",
        "argument_accuracy",
        "sequence_accuracy",
        "first_step_accuracy",
        "task_completion_rate",
    }
