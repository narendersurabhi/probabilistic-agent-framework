"""Automatic failure classification for benchmark task outcomes."""

from __future__ import annotations

from typing import Any, Dict, List


class FailureAnalyzer:
    """Classifies why a task run failed based on expected vs predicted behavior."""

    FAILURE_TYPES = (
        "wrong_tool",
        "incorrect_arguments",
        "premature_action",
        "incomplete_plan",
        "incorrect_sequence",
    )

    def analyze(self, task: Dict[str, Any], normalized: Dict[str, Any]) -> str:
        expected_sequence = task.get("expected_tool_sequence")
        expected_tool = task.get("expected_tool")
        expected_args = task.get("expected_args")

        predicted_sequence: List[str] = [
            step.get("action") for step in normalized.get("steps", []) if step.get("action")
        ]
        selected_tool = normalized.get("selected_tool")
        predicted_args = normalized.get("arguments")

        if expected_sequence:
            if predicted_sequence == expected_sequence:
                return "success"

            if predicted_sequence and predicted_sequence == expected_sequence[: len(predicted_sequence)]:
                return "incomplete_plan"

            if not predicted_sequence:
                return "incomplete_plan"

            first_action = predicted_sequence[0]
            if first_action in expected_sequence and expected_sequence.index(first_action) > 0:
                return "premature_action"

            return "incorrect_sequence"

        if selected_tool != expected_tool:
            return "wrong_tool"

        if expected_args is not None and predicted_args != expected_args:
            return "incorrect_arguments"

        if not normalized.get("completed", False):
            return "incomplete_plan"

        return "success"

