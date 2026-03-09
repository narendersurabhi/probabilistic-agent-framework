"""Generate a synthetic benchmark dataset using task generation + validation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_arena.data_generation import DatasetBuilder, HeuristicTaskLLM, TaskGenerator, TaskValidator


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic benchmark tasks.")
    parser.add_argument("--count", type=int, default=50, help="Number of tasks to generate.")
    parser.add_argument(
        "--output",
        default="src/evaluation/datasets/synthetic_tasks.json",
        help="Output JSON path for the generated dataset.",
    )
    args = parser.parse_args()

    generator = TaskGenerator(llm=HeuristicTaskLLM())
    validator = TaskValidator()
    builder = DatasetBuilder()

    tasks = []
    for idx in range(args.count):
        task = generator.generate_task()
        task["task_id"] = f"synthetic_{idx + 1:03d}"
        if validator.validate(task):
            tasks.append(task)

    out_path = builder.build(tasks, args.output)
    print(f"Wrote {len(tasks)} tasks to {out_path}")


if __name__ == "__main__":
    main()
