"""Failure taxonomy classifier for benchmark task outcomes."""

from __future__ import annotations

from typing import Any, Dict, List


class FailureTaxonomyAnalyzer:
    """Classify failed agent runs into actionable failure categories."""

    FAILURE_TYPES = (
        "tool_selection_error",
        "tool_argument_error",
        "premature_action",
        "missing_step",
        "incorrect_sequence",
        "reasoning_error",
        "hallucination",
    )

    def classify(self, task: Dict[str, Any], trace: Dict[str, Any]) -> str:
        expected_sequence = task.get("expected_tool_sequence")
        expected_tool = task.get("expected_tool")
        expected_args = task.get("expected_args")

        steps = trace.get("steps", [])
        actual_sequence: List[str] = [step.get("action") for step in steps if step.get("action")]
        selected_tool = trace.get("selected_tool")
        predicted_args = trace.get("arguments")

        if expected_sequence:
            if actual_sequence == expected_sequence:
                return "success"
            if not actual_sequence:
                return "missing_step"
            if actual_sequence[0] != expected_sequence[0]:
                return "premature_action"
            if len(actual_sequence) < len(expected_sequence):
                return "missing_step"
            if actual_sequence != expected_sequence:
                return "incorrect_sequence"

        if expected_tool and selected_tool != expected_tool:
            return "tool_selection_error"

        if expected_args is not None and predicted_args != expected_args:
            return "tool_argument_error"

        if not trace.get("completed", False):
            return "missing_step"

        final_answer = trace.get("final_answer")
        expected_answer = task.get("expected_answer")
        if expected_answer is not None and final_answer is not None and final_answer != expected_answer:
            return "reasoning_error"

        if trace.get("hallucinated", False):
            return "hallucination"

        return "success"
