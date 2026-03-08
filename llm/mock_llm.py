"""Mock LLM policies for deterministic behavior."""

from __future__ import annotations

from typing import Dict, Tuple


class MockLLM:
    def extract_state(self, query: str) -> Dict[str, str]:
        text = query.lower()
        if "percent" in text or "multiply" in text:
            return {"task_stage": "solving", "knowledge_state": "partial"}
        if "find" in text or "document" in text:
            return {"task_stage": "retrieving", "knowledge_state": "unknown"}
        return {"task_stage": "start", "knowledge_state": "unknown"}

    def choose_tool(self, query: str) -> Tuple[str, Dict[str, str]]:
        q = query.lower()
        if "percent" in q:
            return "call_calculator", {"expression": "350 * 0.12"}
        if "multiply" in q:
            return "call_calculator", {"expression": "2 * 10"}
        if "find" in q or "document" in q or "population" in q:
            return "retrieve_docs", {"query": query}
        return "generate_answer", {"draft": "Default response"}

    def reason_and_act(self, query: str, last_observation: Dict[str, bool] | None = None) -> Tuple[str, Dict[str, str], str]:
        action, args = self.choose_tool(query)
        thought = f"Given observation={last_observation}, selecting {action}."
        return action, args, thought
