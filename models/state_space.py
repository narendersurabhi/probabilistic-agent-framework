"""State and action spaces used by the POMDP planner."""

from __future__ import annotations

HIDDEN_STATES = {
    "knowledge_state": ["unknown", "partial", "confident"],
    "task_stage": ["start", "retrieving", "solving", "complete"],
    "tool_effectiveness": ["low", "medium", "high"],
}

OBSERVATIONS = [
    "relevant_doc_found",
    "doc_not_relevant",
    "tool_success",
    "tool_failure",
    "answer_generated",
]

ACTIONS = ["retrieve_docs", "call_calculator", "ask_user", "generate_answer"]
