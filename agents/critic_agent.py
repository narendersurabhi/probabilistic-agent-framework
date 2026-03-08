"""Critic agent for tool and argument evaluation."""

from __future__ import annotations

from typing import Any, Dict


class CriticAgent:
    def evaluate(
        self,
        expected_tool: str,
        selected_tool: str,
        arguments: Dict[str, Any],
        expected_args: Dict[str, Any] | None,
        observation: Dict[str, bool],
    ) -> Dict[str, Any]:
        tool_correct = expected_tool == selected_tool
        arguments_correct = True if expected_args is None else expected_args == arguments
        if observation.get("answer_generated"):
            task_progress = "complete"
        elif observation.get("relevant_doc_found"):
            task_progress = "retrieving"
        elif observation.get("tool_success"):
            task_progress = "solving"
        else:
            task_progress = "start"
        return {
            "tool_correct": tool_correct,
            "arguments_correct": arguments_correct,
            "task_progress": task_progress,
        }
