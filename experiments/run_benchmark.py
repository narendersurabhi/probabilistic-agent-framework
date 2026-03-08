"""Run complete benchmark evaluation pipeline with one command."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.generate_report import generate_markdown_report
from src.evaluation.benchmark_runner import BenchmarkRunner


def main() -> None:
    parser = argparse.ArgumentParser(description="Run tool-agent benchmark suite")
    parser.add_argument(
        "--agent",
        action="append",
        choices=["standard", "react", "active_inference"],
        help="Optional agent filter; can be passed multiple times.",
    )
    args = parser.parse_args()

    runner = BenchmarkRunner()
    results = runner.run(agent_filter=args.agent)
    report_path = generate_markdown_report(results, output_path="results/benchmark_report.md")

    print(json.dumps(results, indent=2))
    print(f"Benchmark report written to: {report_path}")


if __name__ == "__main__":
    main()
