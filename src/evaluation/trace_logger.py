"""Structured trace logging for benchmark runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class TraceLogger:
    """Persists per-task traces as JSON files."""

    def __init__(self, output_dir: str | Path = "results/traces") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def log_trace(self, trace: Dict[str, Any]) -> Path:
        task_id = trace.get("task_id", "unknown_task")
        agent = trace.get("agent", "unknown_agent")
        path = self.output_dir / f"{agent}__{task_id}.json"
        path.write_text(json.dumps(trace, indent=2), encoding="utf-8")
        return path
