"""Benchmark runner over multiple agent architectures with trace-aware scoring."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from benchmarks.active_inference_agent import ActiveInferenceBenchmarkAgent
from benchmarks.react_agent import ReActAgent
from benchmarks.standard_agent import StandardToolAgent
from evaluation.metrics import (
    argument_accuracy,
    belief_entropy_reduction,
    final_answer_accuracy,
    prefix_accuracy,
    sequence_tool_accuracy,
    step_efficiency,
    task_completion_rate,
    tool_selection_accuracy,
)


AGENT_FACTORIES = {
    "standard_llm": lambda max_steps: StandardToolAgent(),
    "react": lambda max_steps: ReActAgent(max_steps=max_steps),
    "active_inference": lambda max_steps: ActiveInferenceBenchmarkAgent(max_steps=max_steps),
}


def load_dataset(path: str) -> List[Dict[str, Any]]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _expected_sequence(item: Dict[str, Any]) -> List[str]:
    if item.get("expected_tools"):
        return list(item["expected_tools"])
    if item.get("expected_tool"):
        return [item["expected_tool"]]
    return []


def _prefix_ratio(expected: List[str], actual: List[str]) -> float:
    if not expected:
        return 0.0
    matched = 0
    for e, a in zip(expected, actual):
        if e == a:
            matched += 1
        else:
            break
    return matched / len(expected)


def _row_from_result(item: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
    expected_tools = _expected_sequence(item)
    trace = result.get("trace", [])
    actual_tools = [t.get("tool") for t in trace]

    expected_args = item.get("expected_args")
    first_args = trace[0].get("args", {}) if trace else result.get("args", {})

    expected_final_answer = item.get("expected_final_answer")
    final_answer = result.get("final_answer")

    return {
        "tool_correct": bool(expected_tools) and bool(actual_tools) and expected_tools[0] == actual_tools[0],
        "arguments_correct": expected_args is None or first_args == expected_args,
        "completed": (actual_tools == expected_tools) if expected_tools else bool(result.get("completed", False)),
        "steps": result.get("steps", len(trace) if trace else 1),
        "sequence_exact": actual_tools == expected_tools,
        "prefix_ratio": _prefix_ratio(expected_tools, actual_tools),
        "final_answer_correct": expected_final_answer is None or final_answer == expected_final_answer,
        "task_type": item.get("task_type", "unknown"),
    }


def _per_task_type(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row.get("task_type", "unknown"), []).append(row)
    return {
        k: {
            "tool_accuracy": tool_selection_accuracy(v),
            "sequence_accuracy": sequence_tool_accuracy(v),
            "completion": task_completion_rate(v),
        }
        for k, v in grouped.items()
    }


def _aggregate_runs(run_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not run_results:
        return {}
    keys = [k for k in run_results[0].keys() if k != "per_task_type"]
    agg: Dict[str, Any] = {k: float(np.mean([rr[k] for rr in run_results])) for k in keys}
    # aggregate per-task metrics
    task_types = set()
    for rr in run_results:
        task_types.update(rr["per_task_type"].keys())
    per_task: Dict[str, Dict[str, float]] = {}
    for t in sorted(task_types):
        vals = [rr["per_task_type"].get(t, {"tool_accuracy": 0.0, "sequence_accuracy": 0.0, "completion": 0.0}) for rr in run_results]
        per_task[t] = {
            "tool_accuracy": float(np.mean([v["tool_accuracy"] for v in vals])),
            "sequence_accuracy": float(np.mean([v["sequence_accuracy"] for v in vals])),
            "completion": float(np.mean([v["completion"] for v in vals])),
        }
    agg["per_task_type"] = per_task
    agg["num_runs"] = len(run_results)
    return agg


def run_benchmark(
    dataset_path: str,
    seed: int = 7,
    max_steps: int = 3,
    agent_types: List[str] | None = None,
    number_of_runs: int = 1,
) -> Dict[str, Any]:
    np.random.seed(seed)
    data = load_dataset(dataset_path)

    selected = agent_types or ["standard_llm", "react", "active_inference"]
    for name in selected:
        if name not in AGENT_FACTORIES:
            raise ValueError(f"Unsupported agent type: {name}")

    all_results: Dict[str, Dict[str, Any]] = {}
    for name in selected:
        per_run_results: List[Dict[str, Any]] = []
        for run_idx in range(number_of_runs):
            agent = AGENT_FACTORIES[name](max_steps)
            rows = []
            entropy_track: List[float] = []
            for item in data:
                res = agent.run(item["query"])
                rows.append(_row_from_result(item, res))
                if name == "active_inference":
                    beliefs = res.get("beliefs", [])
                    for b in beliefs:
                        p = np.array(list(b.values()), dtype=float)
                        entropy_track.append(float(-(p * np.log(p + 1e-9)).sum()))

            per_run_results.append(
                {
                    "tool_accuracy": tool_selection_accuracy(rows),
                    "argument_accuracy": argument_accuracy(rows),
                    "task_completion": task_completion_rate(rows),
                    "step_efficiency": step_efficiency(rows),
                    "sequence_tool_accuracy": sequence_tool_accuracy(rows),
                    "prefix_accuracy": prefix_accuracy(rows),
                    "final_answer_accuracy": final_answer_accuracy(rows),
                    "belief_entropy_reduction": belief_entropy_reduction(entropy_track) if name == "active_inference" else 0.0,
                    "per_task_type": _per_task_type(rows),
                    "run_index": run_idx,
                }
            )
        all_results[name] = _aggregate_runs(per_run_results)

    return all_results
