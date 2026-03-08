"""Run complete benchmark evaluation pipeline with one command."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.generate_report import generate_markdown_report
from src.evaluation.benchmark_runner import BenchmarkRunner
from src.visualization.belief_plots import plot_belief_evolution
from src.visualization.free_energy_plot import plot_expected_free_energy
from src.visualization.policy_plots import plot_policy_probabilities


def _load_trace(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    steps = payload.get("steps", [])
    return steps if isinstance(steps, list) else []


def _generate_trace_plots(trace_dir: Path) -> list[Path]:
    active_traces = sorted(trace_dir.glob("active_inference__*.json"))
    if not active_traces:
        return []
    trace = _load_trace(active_traces[0])
    if not trace:
        return []

    return [
        plot_belief_evolution(trace),
        plot_policy_probabilities(trace),
        plot_expected_free_energy(trace),
    ]


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
    trace_plots = _generate_trace_plots(Path("results/traces"))

    print(json.dumps(results, indent=2))
    print(f"Benchmark report written to: {report_path}")
    if trace_plots:
        print("Trace plots written:")
        for path in trace_plots:
            print(f"- {path}")


if __name__ == "__main__":
    main()
