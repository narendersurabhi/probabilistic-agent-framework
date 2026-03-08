"""Run head-to-head Agent Arena matches and print a leaderboard."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.evaluation.arena import AgentArena


def _print_sample_battle(arena_results: dict) -> None:
    battles = arena_results.get("battles", [])
    if not battles:
        return
    sample = battles[0]
    print(f"Task: {sample.get('query')}")
    print("\nAgents competing:\n")
    for idx, agent_name in enumerate(arena_results.get("agents", []), start=1):
        print(f"{idx}. {agent_name}")

    print("\nResults\n")
    for agent_name, outcome in sample.get("results", {}).items():
        marker = "✓" if outcome.get("completed") else "❌"
        status = "correct" if outcome.get("completed") else outcome.get("failure_type", "failed")
        print(f"{agent_name:<24} {marker} {status}")

    print(f"\nWinner: {', '.join(sample.get('winners', []))}\n")


def _print_leaderboard(arena_results: dict) -> None:
    print("Agent Leaderboard\n")
    for row in arena_results.get("leaderboard", []):
        print(f"{row['rank']}. {row['agent']:<24} {row['score']:.2f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Agent Arena leaderboard generation")
    parser.add_argument("--max-tasks", type=int, default=None, help="Optional cap on number of tasks.")
    args = parser.parse_args()

    arena = AgentArena()
    results = arena.run(max_tasks=args.max_tasks)

    _print_sample_battle(results)
    _print_leaderboard(results)
    print("\nSaved:\n- results/leaderboard.json\n- results/arena_results.json")
    print("\nJSON Summary:\n")
    print(json.dumps({"total_tasks": results["total_tasks"], "leaderboard": results["leaderboard"]}, indent=2))


if __name__ == "__main__":
    main()
