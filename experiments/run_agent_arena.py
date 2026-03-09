"""Flagship demo script for Agent Arena head-to-head benchmarking."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.evaluation.arena import AgentArena


def main() -> None:
    print("Running Agent Arena Benchmark\n")
    arena = AgentArena()
    results = arena.run()

    print("Agents competing:")
    for agent_name in results.get("agents", []):
        print(agent_name)

    print("\nResults\n")
    for row in results.get("leaderboard", []):
        print(f"{row['agent']:<24} {row['score']:.2f}")

    print("\nLeaderboard generated.")
    print("results/leaderboard.json")
    print("\nSummary JSON:")
    print(json.dumps({"total_tasks": results.get("total_tasks"), "leaderboard": results.get("leaderboard", [])}, indent=2))


if __name__ == "__main__":
    main()
