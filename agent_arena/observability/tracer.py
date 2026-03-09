"""Tracing primitives for agent observability."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict


class AgentTracer:
    """Collects structured, timestamped events for an agent run."""

    def __init__(self, run_id: str, query: str, agent_name: str, task_id: str | None = None) -> None:
        self._run_start = time.perf_counter()
        self.trace: Dict[str, Any] = {
            "run_id": run_id,
            "agent": agent_name,
            "task_id": task_id,
            "query": query,
            "started_at": time.time(),
            "status": "running",
            "steps": [],
            "errors": [],
        }

    def record_step(
        self,
        action: str,
        arguments: Dict[str, Any] | None = None,
        observation: Any | None = None,
        error: str | None = None,
        latency_ms: float | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        step: Dict[str, Any] = {
            "step": len(self.trace["steps"]) + 1,
            "action": action,
            "timestamp": time.time(),
        }
        if arguments is not None:
            step["arguments"] = arguments
        if observation is not None:
            step["observation"] = observation
        if error is not None:
            step["error"] = error
            self.trace["errors"].append(error)
        if latency_ms is not None:
            step["latency_ms"] = round(latency_ms, 3)
        if metadata:
            step.update(metadata)
        self.trace["steps"].append(step)

    def finish(self, status: str = "success", result: Dict[str, Any] | None = None) -> Dict[str, Any]:
        self.trace["status"] = status
        self.trace["total_latency_ms"] = round((time.perf_counter() - self._run_start) * 1000.0, 3)
        self.trace["ended_at"] = time.time()
        if result is not None:
            self.trace["result"] = result
        return self.trace

    def save(self, path: str | Path) -> Path:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(self.trace, indent=2), encoding="utf-8")
        return output_path
