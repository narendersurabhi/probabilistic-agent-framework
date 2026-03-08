"""Side-by-side reasoning trace comparison across benchmark agents."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping

from src.evaluation.benchmark_runner import ActiveInferenceAgent, ReActAgent, StandardAgent


class AgentComparisonRunner:
    """Runs the same task through all agents and persists normalized traces."""

    def __init__(self, results_dir: str | Path = "results") -> None:
        self.results_dir = Path(results_dir)
        self.comparison_dir = self.results_dir / "comparisons"
        self.comparison_dir.mkdir(parents=True, exist_ok=True)
        self.agents = {
            "standard_agent": StandardAgent(),
            "react_agent": ReActAgent(),
            "active_inference_agent": ActiveInferenceAgent(),
        }

    @staticmethod
    def _normalize_steps(agent_output: Mapping[str, Any]) -> List[Dict[str, Any]]:
        raw_steps = agent_output.get("steps")
        if not isinstance(raw_steps, list):
            return []

        steps: List[Dict[str, Any]] = []
        for i, step in enumerate(raw_steps, start=1):
            steps.append(
                {
                    "step": i,
                    "action": step.get("action"),
                    "arguments": step.get("arguments", {}),
                    "observation": step.get("observation"),
                    "belief_state": step.get("belief_state"),
                    "policy_probabilities": step.get("policy_probabilities"),
                    "expected_free_energy": step.get("expected_free_energy"),
                }
            )
        return steps

    def compare_task(self, task: Mapping[str, Any]) -> Dict[str, Any]:
        task_id = str(task.get("task_id") or "ad_hoc_task")
        query = str(task.get("query") or "")
        payload: Dict[str, Any] = {"task_id": task_id, "query": query}

        for name, agent in self.agents.items():
            raw = agent.run(query)
            payload[name] = {
                "selected_tool": raw.get("selected_tool"),
                "arguments": raw.get("arguments", {}),
                "steps": self._normalize_steps(raw),
            }

        out_path = self.comparison_dir / f"{task_id}.json"
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        payload["artifact_path"] = str(out_path)
        return payload
