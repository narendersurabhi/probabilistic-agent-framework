"""Run side-by-side reasoning comparison for standard, ReAct, and Active Inference agents."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.evaluation.agent_comparison import AgentComparisonRunner


DEFAULT_QUERY = "What is 20 percent of the population of Spain?"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare reasoning traces across agent architectures.")
    parser.add_argument("--task-id", default="task_001", help="Task identifier for artifact naming.")
    parser.add_argument("--query", default=DEFAULT_QUERY, help="Task query to execute.")
    parser.add_argument("--output-dir", default="results", help="Root output directory.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runner = AgentComparisonRunner(results_dir=args.output_dir)
    payload = runner.compare_task({"task_id": args.task_id, "query": args.query})
    print(json.dumps(payload, indent=2))
    print(f"Saved comparison artifact to {Path(payload['artifact_path'])}")


if __name__ == "__main__":
    main()
