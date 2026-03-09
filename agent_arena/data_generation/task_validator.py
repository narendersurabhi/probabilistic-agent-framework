"""Validation utilities for synthetic benchmark tasks."""

from __future__ import annotations

from typing import Any, Dict, Sequence


ALLOWED_TOOLS = {"retrieve_docs", "call_calculator", "generate_answer"}


class TaskValidator:
    """Validate that generated tasks satisfy benchmark schema expectations."""

    required_fields = ("task_id", "query", "expected_tool_sequence")

    def validate(self, task: Dict[str, Any]) -> bool:
        return len(self.errors(task)) == 0

    def errors(self, task: Dict[str, Any]) -> Sequence[str]:
        issues: list[str] = []

        for field in self.required_fields:
            if field not in task:
                issues.append(f"Missing required field: {field}")

        if "task_id" in task and not isinstance(task.get("task_id"), str):
            issues.append("task_id must be a string")

        if "query" in task and (not isinstance(task.get("query"), str) or not task["query"].strip()):
            issues.append("query must be a non-empty string")

        sequence = task.get("expected_tool_sequence")
        if not isinstance(sequence, list) or not sequence:
            issues.append("expected_tool_sequence must be a non-empty list")
        elif any(tool not in ALLOWED_TOOLS for tool in sequence):
            issues.append("expected_tool_sequence contains unsupported tools")

        return issues
