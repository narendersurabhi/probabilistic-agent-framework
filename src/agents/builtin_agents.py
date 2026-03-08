"""Built-in agent plugins for the Agent Arena."""

from __future__ import annotations

from typing import Any, Dict

from src.agents.base_agent import BaseAgent
from src.evaluation.benchmark_runner import ActiveInferenceAgent, ReActAgent, StandardAgent


class StandardArenaAgent(BaseAgent):
    name = "StandardAgent"

    def __init__(self) -> None:
        self._agent = StandardAgent()

    def run(self, query: str) -> Dict[str, Any]:
        return self._agent.run(query)


class ReActArenaAgent(BaseAgent):
    name = "ReActAgent"

    def __init__(self) -> None:
        self._agent = ReActAgent()

    def run(self, query: str) -> Dict[str, Any]:
        return self._agent.run(query)


class ActiveInferenceArenaAgent(BaseAgent):
    name = "ActiveInferenceAgent"

    def __init__(self) -> None:
        self._agent = ActiveInferenceAgent()

    def run(self, query: str) -> Dict[str, Any]:
        return self._agent.run(query)
