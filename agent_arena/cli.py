"""Command line entrypoint for package users."""

from __future__ import annotations

import argparse
import json

from agent_arena import Arena
from agent_arena.benchmark import DistributedBenchmarkRunner


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Agent Arena benchmarks.")
    parser.add_argument("--dataset", default="tool_benchmark", help="Dataset name (for display in output).")
    parser.add_argument("--max-tasks", type=int, default=None, help="Optional max number of tasks to execute.")
    parser.add_argument("--workers", type=int, default=1, help="Worker process count for distributed benchmark runs.")
    args = parser.parse_args()

    if args.workers > 1:
        runner = DistributedBenchmarkRunner(workers=args.workers)
        print("Running distributed benchmark\n")
        print(f"Workers: {args.workers}")
        results = runner.run()
        print(f"Tasks: {sum(int(v.get('count', 0)) for v in results.values())}\n")
        print(json.dumps(results, indent=2))
        return

    arena = Arena(dataset=args.dataset)
    payload = arena.run(max_tasks=args.max_tasks)

    print("Agent Leaderboard")
    print()
    for row in payload.get("leaderboard", []):
        print(f"{row['agent']:<20} {row['score']:.2f}")


if __name__ == "__main__":
    main()
