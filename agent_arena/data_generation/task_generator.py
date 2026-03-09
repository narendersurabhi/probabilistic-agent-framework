"""Synthetic benchmark task generation helpers."""

from __future__ import annotations

import json
from typing import Any, Dict, Protocol


DEFAULT_PROMPT = """
Generate exactly one benchmark task for evaluating AI agents that use tools.

Available tools:
- retrieve_docs
- call_calculator
- generate_answer

Return only JSON with the fields:
- task_id
- query
- expected_tool_sequence
""".strip()


class LLMGenerator(Protocol):
    """Protocol for LLM clients used by the task generator."""

    def generate(self, prompt: str) -> str:
        """Generate a string response from a prompt."""


class HeuristicTaskLLM:
    """Deterministic fallback LLM client for offline synthetic task generation."""

    def __init__(self) -> None:
        self._index = 0
        self._templates = [
            ("Find the population of Canada and compute 5 percent of it.", ["retrieve_docs", "call_calculator"]),
            ("What is twice the population of Australia?", ["retrieve_docs", "call_calculator"]),
            ("Which city is the capital of Japan?", ["retrieve_docs", "generate_answer"]),
            ("What is 19 multiplied by 7?", ["call_calculator"]),
        ]

    def generate(self, prompt: str) -> str:
        _ = prompt
        query, tool_sequence = self._templates[self._index % len(self._templates)]
        self._index += 1
        payload = {
            "task_id": f"synthetic_{self._index:03d}",
            "query": query,
            "expected_tool_sequence": tool_sequence,
        }
        return json.dumps(payload)


class TaskGenerator:
    """Generate synthetic benchmark tasks through an LLM client."""

    def __init__(self, llm: LLMGenerator, prompt_template: str = DEFAULT_PROMPT) -> None:
        self.llm = llm
        self.prompt_template = prompt_template

    def generate_task(self) -> Dict[str, Any]:
        """Generate and parse one benchmark task."""
        response = self.llm.generate(self.prompt_template)
        parsed = json.loads(response)
        if not isinstance(parsed, dict):
            raise ValueError("Generated task must be a JSON object.")
        return parsed
