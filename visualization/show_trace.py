"""CLI utility to print agent trace timelines."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python visualization/show_trace.py <trace_path>")
        return 1

    trace_path = Path(sys.argv[1])
    if not trace_path.exists():
        print(f"Trace not found: {trace_path}")
        return 1

    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    print(f"Run ID: {trace.get('run_id', 'unknown')}")
    print(f"Agent: {trace.get('agent', 'unknown')}")
    print(f"Query: {trace.get('query', '')}")
    print(f"Status: {trace.get('status', 'unknown')}")
    print("\nTimeline")
    print("-" * 32)
    for step in trace.get("steps", []):
        print(f"STEP {step.get('step')}")
        print(f"action: {step.get('action')}")
        if "latency_ms" in step:
            print(f"latency_ms: {step.get('latency_ms')}")
        if "observation" in step:
            print(f"observation: {step.get('observation')}")
        if "error" in step:
            print(f"error: {step.get('error')}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
