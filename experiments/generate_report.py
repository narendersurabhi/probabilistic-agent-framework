"""Generate benchmark markdown report from benchmark result JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    metrics = json.loads(Path(args.input).read_text(encoding="utf-8"))
    lines = [
        "# Benchmark Report",
        "",
        "| Agent | Tool Accuracy | Argument Accuracy | Completion Rate | Belief Entropy Reduction |",
        "|---|---:|---:|---:|---:|",
    ]
    for agent, vals in metrics.items():
        lines.append(
            f"| {agent} | {vals.get('tool_accuracy', 0.0):.2f} | {vals.get('argument_accuracy', 0.0):.2f} | {vals.get('task_completion', 0.0):.2f} | {vals.get('belief_entropy_reduction', 0.0):.2f} |"
        )
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
