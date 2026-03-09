"""Trace replay utilities for step-by-step run debugging."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


class ReplayEngine:
    """Replays a stored trace file for deterministic run inspection."""

    def __init__(self, trace_path: str | Path):
        self.trace_path = Path(trace_path)
        if not self.trace_path.exists():
            raise FileNotFoundError(f"Trace not found: {self.trace_path}")
        self.trace = json.loads(self.trace_path.read_text(encoding="utf-8"))

    def iter_step_messages(self) -> list[str]:
        """Build formatted replay messages for each recorded step."""
        messages: list[str] = []
        for step in self.trace.get("steps", []):
            lines = [f"STEP {step.get('step', '?')}", f"Action: {step.get('action', 'unknown')}"]
            if "arguments" in step:
                lines.append(f"Arguments: {step.get('arguments')}")
            if "observation" in step:
                lines.append(f"Observation: {step.get('observation')}")
            if "result" in step:
                lines.append(f"Result: {step.get('result')}")
            if "error" in step:
                lines.append(f"Error: {step.get('error')}")
            messages.append("\n".join(lines))
        return messages

    def replay(self, delay: float = 0.0, interactive: bool = False) -> list[str]:
        """Print a replay timeline and optionally pause between steps."""
        run_id = self.trace.get("run_id", "unknown")
        query = self.trace.get("query", "")
        status = self.trace.get("status", "unknown")

        print(f"Run ID: {run_id}")
        print(f"Query: {query}")
        print(f"Status: {status}")

        messages = self.iter_step_messages()
        for index, message in enumerate(messages, start=1):
            print("\n" + message)
            if interactive and index < len(messages):
                input("Press ENTER for next step...")
            elif delay > 0:
                time.sleep(delay)
        return messages

    def summary(self) -> dict[str, Any]:
        """Return lightweight metadata for listing traces in dashboards/CLIs."""
        steps = self.trace.get("steps", [])
        return {
            "run_id": self.trace.get("run_id", "unknown"),
            "query": self.trace.get("query", ""),
            "status": self.trace.get("status", "unknown"),
            "steps": len(steps),
            "trace_path": str(self.trace_path),
        }
