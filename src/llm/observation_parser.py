"""Deterministic parser that maps tool outputs to observation labels."""

from __future__ import annotations


def parse_observation(tool_output: dict[str, object]) -> str:
    if tool_output.get("tool") == "calculator" and tool_output.get("success"):
        return "tool_success"

    if tool_output.get("tool") == "retriever":
        if tool_output.get("success"):
            return "relevant_doc_found"
        return "doc_not_relevant"

    return "answer_generated"
