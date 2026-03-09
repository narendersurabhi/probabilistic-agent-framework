"""Public package interface for the agent-arena framework."""

from __future__ import annotations

from typing import Any

__all__ = [
    "Arena",
    "BenchmarkRunner",
    "DistributedBenchmarkRunner",
    "load_dataset",
    "list_datasets",
    "AgentTracer",
    "MetricsCollector",
    "ReplayEngine",
]


def __getattr__(name: str) -> Any:
    if name == "Arena":
        from agent_arena.arena import Arena

        return Arena
    if name in {"BenchmarkRunner", "DistributedBenchmarkRunner"}:
        from agent_arena.benchmark import BenchmarkRunner, DistributedBenchmarkRunner

        return {"BenchmarkRunner": BenchmarkRunner, "DistributedBenchmarkRunner": DistributedBenchmarkRunner}[name]
    if name in {"load_dataset", "list_datasets"}:
        from agent_arena.datasets import list_datasets, load_dataset

        return {"load_dataset": load_dataset, "list_datasets": list_datasets}[name]
    if name in {"AgentTracer", "MetricsCollector"}:
        from agent_arena.observability import AgentTracer, MetricsCollector

        return {"AgentTracer": AgentTracer, "MetricsCollector": MetricsCollector}[name]
    if name == "ReplayEngine":
        from agent_arena.replay import ReplayEngine

        return ReplayEngine
    raise AttributeError(f"module 'agent_arena' has no attribute {name!r}")
