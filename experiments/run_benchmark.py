"""Run benchmark across Standard, ReAct, and Active Inference agents."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

from evaluation.benchmark_runner import run_benchmark
from visualization.belief_plots import plot_benchmark_bars


def load_config(path: str) -> Dict[str, str]:
    cfg: Dict[str, str] = {}
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        cfg[k.strip()] = v.strip()
    return cfg


def parse_agent_types(raw: str) -> List[str]:
    return [v.strip() for v in raw.split(",") if v.strip()]


def write_report(metrics: dict, out_path: str) -> None:
    lines = [
        "# Benchmark Report",
        "",
        "| Agent | Tool Accuracy | First-Step Accuracy | Sequence Accuracy | Planning Accuracy | Premature Action Rate | Prefix Accuracy | Argument Accuracy | Completion Rate | Avg Steps |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for agent, vals in metrics.items():
        lines.append(
            f"| {agent} | {vals['tool_accuracy']:.2f} | {vals['first_step_accuracy']:.2f} | {vals['sequence_tool_accuracy']:.2f} | {vals['planning_accuracy']:.2f} | {vals['premature_action_rate']:.2f} | {vals['prefix_accuracy']:.2f} | {vals['argument_accuracy']:.2f} | {vals['task_completion']:.2f} | {vals['step_efficiency']:.2f} |"
        )

    lines.extend(["", "## Per-task-type summary"])
    for agent, vals in metrics.items():
        lines.append(f"### {agent}")
        lines.append("| Task Type | Tool Acc | First Step Acc | Sequence Acc | Planning Acc | Premature Rate | Avg Depth | Completion |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
        for task_type, task_vals in vals["per_task_type"].items():
            lines.append(
                f"| {task_type} | {task_vals['tool_accuracy']:.2f} | {task_vals['first_step_accuracy']:.2f} | {task_vals['sequence_accuracy']:.2f} | {task_vals['planning_accuracy']:.2f} | {task_vals['premature_action_rate']:.2f} | {task_vals['average_planning_depth']:.2f} | {task_vals['completion']:.2f} |"
            )
        lines.append("")

    Path(out_path).write_text("\n".join(lines), encoding="utf-8")


def write_evaluation_report(metrics: Dict[str, Dict], out_path: str) -> None:
    report = {
        agent: {
            "tool_selection_accuracy": vals["tool_accuracy"],
            "argument_accuracy": vals["argument_accuracy"],
            "sequence_accuracy": vals["sequence_tool_accuracy"],
            "first_step_accuracy": vals["first_step_accuracy"],
            "planning_accuracy": vals["planning_accuracy"],
            "average_planning_depth": vals["average_planning_depth"],
            "premature_action_rate": vals["premature_action_rate"],
            "task_completion_rate": vals["task_completion"],
            "belief_entropy_reduction": vals.get("belief_entropy_reduction", 0.0),
        }
        for agent, vals in metrics.items()
    }
    Path(out_path).write_text(json.dumps(report, indent=2), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/benchmark_config.yaml")
    ap.add_argument("--output-dir", default="results")
    args = ap.parse_args()

    cfg = load_config(args.config)
    seed = int(cfg.get("seed", "7"))
    dataset_path = cfg.get("dataset_path", "evaluation/datasets/benchmark_tasks.json")
    max_steps = int(cfg.get("max_steps", "3"))
    number_of_runs = int(cfg.get("number_of_runs", "1"))
    agent_types = parse_agent_types(cfg.get("agent_types", "standard_llm,react,active_inference"))

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    traces_path = str(out / "benchmark_traces.jsonl")

    metrics = run_benchmark(
        dataset_path=dataset_path,
        seed=seed,
        max_steps=max_steps,
        agent_types=agent_types,
        number_of_runs=number_of_runs,
        trace_log_path=traces_path,
    )

    (out / "benchmark_results.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    plot_benchmark_bars(metrics, str(out / "plots"))
    write_report(metrics, str(out / "benchmark_report.md"))
    write_evaluation_report(metrics, str(out / "evaluation_report.json"))
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
