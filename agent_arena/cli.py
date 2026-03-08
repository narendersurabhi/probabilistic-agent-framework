"""Command line entrypoint for package users."""

from __future__ import annotations

import argparse

from agent_arena import Arena


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Agent Arena benchmarks.")
    parser.add_argument("--dataset", default="tool_benchmark", help="Dataset name (for display in output).")
    parser.add_argument("--max-tasks", type=int, default=None, help="Optional max number of tasks to execute.")
    args = parser.parse_args()

    arena = Arena(dataset=args.dataset)
    payload = arena.run(max_tasks=args.max_tasks)

    print("Agent Leaderboard")
    print()
    for row in payload.get("leaderboard", []):
        print(f"{row['agent']:<20} {row['score']:.2f}")


if __name__ == "__main__":
    main()
