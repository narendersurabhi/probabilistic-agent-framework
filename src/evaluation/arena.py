"""Head-to-head Agent Arena runner for pluggable tool-using agents."""

from __future__ import annotations

import importlib
import inspect
import json
import pkgutil
from pathlib import Path
from typing import Any, Dict, List

from src.agents.base_agent import BaseAgent
from src.evaluation.benchmark_runner import BenchmarkRunner
from src.evaluation.dataset_loader import DatasetLoader
from src.evaluation.failure_analyzer import FailureAnalyzer


class AgentArena:
    """Runs all discovered BaseAgent plugins on a shared task set and ranks them."""

    def __init__(self, dataset_dir: str | Path = "src/evaluation/datasets", results_dir: str | Path = "results") -> None:
        self.dataset_loader = DatasetLoader(dataset_dir=dataset_dir)
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.failure_analyzer = FailureAnalyzer()
        self._benchmark_helper = BenchmarkRunner(dataset_dir=dataset_dir, results_dir=results_dir)

    def discover_agents(self) -> List[BaseAgent]:
        import src.agents as agents_pkg

        discovered: List[BaseAgent] = []
        for mod in pkgutil.iter_modules(agents_pkg.__path__, prefix="src.agents."):
            if mod.name.endswith("base_agent"):
                continue
            module = importlib.import_module(mod.name)
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if not issubclass(obj, BaseAgent) or obj is BaseAgent:
                    continue
                if inspect.isabstract(obj):
                    continue
                discovered.append(obj())
        discovered.sort(key=lambda agent: agent.name)
        return discovered

    def _evaluate(self, task: Dict[str, Any], raw_output: Dict[str, Any]) -> Dict[str, Any]:
        normalized = self._benchmark_helper._normalize(raw_output)
        evaluation = self._benchmark_helper._evaluate_task(task, normalized)
        failure_type = self.failure_analyzer.analyze(task, normalized)
        evaluation["failure_type"] = failure_type
        evaluation["normalized"] = normalized
        return evaluation

    def run(self, max_tasks: int | None = None) -> Dict[str, Any]:
        tasks = [task for bundle in self.dataset_loader.load_all().values() for task in bundle]
        if max_tasks is not None:
            tasks = tasks[: max(0, max_tasks)]

        agents = self.discover_agents()
        if not agents:
            raise ValueError("No arena agents discovered under src/agents")

        score = {agent.name: 0 for agent in agents}
        totals = {agent.name: 0 for agent in agents}
        failures = {agent.name: {label: 0 for label in self.failure_analyzer.FAILURE_TYPES} for agent in agents}
        battle_log: List[Dict[str, Any]] = []

        for task in tasks:
            per_agent: Dict[str, Any] = {}
            winners: List[str] = []
            best = -1

            for agent in agents:
                evaluation = self._evaluate(task, agent.run(str(task.get("query", ""))))
                totals[agent.name] += 1
                if evaluation["completed"]:
                    score[agent.name] += 1
                else:
                    failures[agent.name][evaluation["failure_type"]] += 1

                per_agent[agent.name] = {
                    "completed": evaluation["completed"],
                    "tool_correct": evaluation["tool_correct"],
                    "sequence_correct": evaluation["sequence_correct"],
                    "failure_type": evaluation["failure_type"],
                    "selected_tool": evaluation["normalized"].get("selected_tool"),
                }

                task_points = int(evaluation["completed"])
                if task_points > best:
                    best = task_points
                    winners = [agent.name]
                elif task_points == best:
                    winners.append(agent.name)

            battle_log.append(
                {
                    "task_id": task.get("task_id"),
                    "query": task.get("query"),
                    "results": per_agent,
                    "winners": winners,
                }
            )

        leaderboard = [
            {
                "rank": 0,
                "agent": name,
                "score": round((score[name] / totals[name]) if totals[name] else 0.0, 4),
                "wins": score[name],
                "total_tasks": totals[name],
                "failure_breakdown": failures[name],
            }
            for name in score
        ]
        leaderboard.sort(key=lambda row: row["score"], reverse=True)
        for idx, row in enumerate(leaderboard, start=1):
            row["rank"] = idx

        payload = {
            "total_tasks": len(tasks),
            "agents": [agent.name for agent in agents],
            "leaderboard": leaderboard,
            "battles": battle_log,
        }

        (self.results_dir / "leaderboard.json").write_text(json.dumps(leaderboard, indent=2), encoding="utf-8")
        (self.results_dir / "arena_results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload
