"""JSONL logger for agent runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class RunLogger:
    def __init__(self, path: str = "logs/agent_runs.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, record: Dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
