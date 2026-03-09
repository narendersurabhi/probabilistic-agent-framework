"""Minimal ReAct baseline agent for planning-strategy comparisons."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str: ...


class ReActAgent:
    """Simple baseline that asks an LLM for the next tool decision."""

    def __init__(self, llm: LLMClient, tools: dict[str, Callable[..., Any]] | None = None) -> None:
        self.llm = llm
        self.tools = tools or {}

    def build_prompt(self, query: str) -> str:
        return (
            "You are an agent that can use tools.\n\n"
            f"Question: {query}\n\n"
            "Decide which tool to use next and explain your short reasoning."
        )

    def run(self, query: str) -> dict[str, Any]:
        prompt = self.build_prompt(query)
        response = self.llm.generate(prompt)
        return {
            "query": query,
            "prompt": prompt,
            "response": response,
            "available_tools": sorted(self.tools.keys()),
        }
