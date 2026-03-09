"""Distributed benchmark runner using multiprocessing worker pools."""

from __future__ import annotations

import json
import multiprocessing as mp
from pathlib import Path
from typing import Any, Callable, Dict, List

from src.evaluation.benchmark_runner import BenchmarkRunner
from src.evaluation.metrics import aggregate_metrics
from src.visualization.trace_graph import build_reasoning_graph, save_reasoning_graph

_WORKER_RUNNER: BenchmarkRunner | None = None
_WORKER_AGENTS: Dict[str, Any] = {}


def _worker_init(dataset_dir: str, results_dir: str) -> None:
    global _WORKER_RUNNER, _WORKER_AGENTS
    _WORKER_RUNNER = BenchmarkRunner(dataset_dir=dataset_dir, results_dir=results_dir)
    _WORKER_AGENTS = {}


def _run_job(job: Dict[str, Any]) -> Dict[str, Any]:
    if _WORKER_RUNNER is None:
        raise RuntimeError("Distributed worker is not initialized.")

    agent_name = str(job["agent_name"])
    task = dict(job["task"])

    agent = _WORKER_AGENTS.get(agent_name)
    if agent is None:
        agent = _WORKER_RUNNER._build_agent(agent_name)
        _WORKER_AGENTS[agent_name] = agent

    normalized = _WORKER_RUNNER._normalize(agent.run(str(task.get("query", ""))))
    evaluation = _WORKER_RUNNER._evaluate_task(task, normalized)
    failure_type = _WORKER_RUNNER.failure_analyzer.analyze(task, normalized)
    evaluation["failure_type"] = failure_type

    trace_payload = _WORKER_RUNNER._create_trace(task, agent_name, normalized, evaluation)
    graph = build_reasoning_graph(trace_payload)

    task_id = str(trace_payload.get("task_id", "unknown_task"))
    events = [
        {
            "event": "benchmark_step",
            "agent": agent_name,
            "task_id": task_id,
            "query": task.get("query"),
            "failure_type": failure_type,
            **step_payload,
        }
        for step_payload in trace_payload.get("steps", [])
    ]

    return {
        "agent_name": agent_name,
        "evaluation": evaluation,
        "trace": trace_payload,
        "graph": graph,
        "task_id": task_id,
        "events": events,
    }


class DistributedBenchmarkRunner:
    """Parallel benchmark execution using independent worker processes."""

    def __init__(
        self,
        dataset_dir: str | Path = "src/evaluation/datasets",
        results_dir: str | Path = "results",
        workers: int = 4,
    ) -> None:
        self.dataset_dir = Path(dataset_dir)
        self.results_dir = Path(results_dir)
        self.workers = max(1, workers)
        self.benchmark_runner = BenchmarkRunner(dataset_dir=self.dataset_dir, results_dir=self.results_dir)

    def save_results(self, results: Dict[str, Dict[str, float]]) -> Path:
        output_path = self.results_dir / "benchmark_results.json"
        output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
        return output_path

    def run(
        self,
        agent_filter: List[str] | None = None,
        event_callback: Callable[[Dict[str, Any]], None] | None = None,
        progress_callback: Callable[[Dict[str, int]], None] | None = None,
    ) -> Dict[str, Dict[str, float]]:
        datasets = self.benchmark_runner.dataset_loader.load_all()
        available = ["standard", "react", "active_inference"]
        selected_names = [name for name in available if (agent_filter is None or name in agent_filter)]
        if not selected_names:
            raise ValueError("No valid agents selected.")

        jobs = [
            {"agent_name": agent_name, "task": task}
            for agent_name in selected_names
            for tasks in datasets.values()
            for task in tasks
        ]

        rows_by_agent: Dict[str, List[Dict[str, Any]]] = {name: [] for name in selected_names}
        failure_analysis: Dict[str, Dict[str, Any]] = {}
        aggregate_failures = {failure: 0 for failure in self.benchmark_runner.failure_analyzer.FAILURE_TYPES}
        failure_counts_by_agent = {
            name: {failure: 0 for failure in self.benchmark_runner.failure_analyzer.FAILURE_TYPES}
            for name in selected_names
        }

        total_jobs = len(jobs)
        completed_jobs = 0

        start_method = "fork" if "fork" in mp.get_all_start_methods() else "spawn"
        context = mp.get_context(start_method)
        with context.Pool(
            processes=self.workers,
            initializer=_worker_init,
            initargs=(str(self.dataset_dir), str(self.results_dir)),
        ) as pool:
            for payload in pool.imap_unordered(_run_job, jobs):
                agent_name = payload["agent_name"]
                evaluation = payload["evaluation"]
                rows_by_agent[agent_name].append(evaluation)

                failure_type = evaluation.get("failure_type", "success")
                if failure_type != "success" and failure_type in failure_counts_by_agent[agent_name]:
                    failure_counts_by_agent[agent_name][failure_type] += 1
                    aggregate_failures[failure_type] += 1

                trace_payload = payload["trace"]
                self.benchmark_runner.trace_logger.log_trace(trace_payload)
                save_reasoning_graph(payload["graph"], self.benchmark_runner.graph_dir / f"{agent_name}__{payload['task_id']}_graph.json")

                if event_callback is not None:
                    for event in payload["events"]:
                        event_callback(event)

                completed_jobs += 1
                if progress_callback is not None:
                    progress_callback({"workers": self.workers, "total": total_jobs, "completed": completed_jobs})

        results: Dict[str, Dict[str, float]] = {}
        for agent_name in selected_names:
            rows = rows_by_agent[agent_name]
            metrics = aggregate_metrics(rows)
            total_tasks = len(rows)
            total_failures = sum(failure_counts_by_agent[agent_name].values())
            metrics["failure_rate"] = float(total_failures / total_tasks) if total_tasks else 0.0
            results[agent_name] = metrics
            failure_analysis[agent_name] = {
                "total_tasks": total_tasks,
                "total_failures": total_failures,
                "failure_counts": failure_counts_by_agent[agent_name],
            }

        failure_analysis["overall"] = {
            "total_failures": sum(aggregate_failures.values()),
            "failure_counts": aggregate_failures,
        }

        self.save_results(results)
        self.benchmark_runner.save_failure_analysis(failure_analysis)
        self.benchmark_runner.generate_plots(results)
        self.benchmark_runner._plot_failure_distribution(aggregate_failures)
        return results
