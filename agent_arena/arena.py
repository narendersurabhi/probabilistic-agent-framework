"""High-level Arena API for running head-to-head agent evaluations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Protocol

from agent_arena.datasets import load_dataset
from src.evaluation.arena import AgentArena


class SupportsRun(Protocol):
    """Protocol for user-provided arena agents."""

    name: str

    def run(self, query: str) -> Dict[str, Any]:
        ...


@dataclass
class Arena:
    """User-facing Arena class with custom-agent and built-in modes."""

    agents: Iterable[SupportsRun] | None = None
    dataset: str = "tool_benchmark"
    results_dir: str | Path = "results"

    def _score_task(self, task: Dict[str, Any], result: Dict[str, Any]) -> float:
        selected_tool = result.get("tool") or result.get("selected_tool")
        expected_tool = task.get("expected_tool")
        if expected_tool is not None:
            return float(selected_tool == expected_tool)

        expected_sequence = task.get("expected_tool_sequence") or task.get("expected_tools") or []
        if expected_sequence:
            return float(selected_tool == expected_sequence[0])

        return 0.0

    def run(self, max_tasks: int | None = None) -> Dict[str, Any]:
        """Run either custom provided agents or built-in auto-discovered arena agents."""
        if self.agents:
            tasks = load_dataset(self.dataset)
            if max_tasks is not None:
                tasks = tasks[: max(0, max_tasks)]

            results: Dict[str, List[float]] = {}
            for task in tasks:
                query = str(task.get("query", ""))
                for agent in self.agents:
                    score = self._score_task(task, agent.run(query))
                    results.setdefault(agent.name, []).append(score)

            leaderboard = [
                {
                    "agent": name,
                    "score": (sum(scores) / len(scores)) if scores else 0.0,
                    "tasks": len(scores),
                }
                for name, scores in results.items()
            ]
            leaderboard.sort(key=lambda row: row["score"], reverse=True)
            return {"dataset": self.dataset, "leaderboard": leaderboard, "scores": results}

        internal = AgentArena(results_dir=Path(self.results_dir))
        return internal.run(max_tasks=max_tasks)
