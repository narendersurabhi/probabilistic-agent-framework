"""Generate benchmark markdown report from benchmark result metrics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict


PLOT_FILES = [
    "tool_accuracy_comparison.png",
    "sequence_accuracy_comparison.png",
    "first_step_accuracy_comparison.png",
    "completion_rate_comparison.png",
]


def generate_markdown_report(metrics: Dict[str, Dict[str, float]], output_path: str = "results/benchmark_report.md") -> Path:
    lines = [
        "# Benchmark Report",
        "",
        "## Summary Metrics",
        "",
        "| Agent | Tool Selection Accuracy | Argument Accuracy | Sequence Accuracy | First Step Accuracy | Task Completion Rate |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for agent, values in metrics.items():
        lines.append(
            "| {agent} | {tool:.2f} | {args:.2f} | {seq:.2f} | {first:.2f} | {completion:.2f} |".format(
                agent=agent,
                tool=values.get("tool_selection_accuracy", 0.0),
                args=values.get("argument_accuracy", 0.0),
                seq=values.get("sequence_accuracy", 0.0),
                first=values.get("first_step_accuracy", 0.0),
                completion=values.get("task_completion_rate", 0.0),
            )
        )

    lines.extend(["", "## Plots", ""])
    for filename in PLOT_FILES:
        lines.append(f"![{filename}](plots/{filename})")

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate markdown benchmark report")
    parser.add_argument("--input", default="results/benchmark_results.json")
    parser.add_argument("--output", default="results/benchmark_report.md")
    args = parser.parse_args()

    metrics = json.loads(Path(args.input).read_text(encoding="utf-8"))
    out = generate_markdown_report(metrics, output_path=args.output)
    print(f"Report written to: {out}")


if __name__ == "__main__":
    main()
