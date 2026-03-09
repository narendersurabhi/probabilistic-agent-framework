"""Metrics utilities for agent observability traces."""

from __future__ import annotations

from typing import Any, Dict, Iterable


class MetricsCollector:
    """Computes per-run and aggregate metrics from trace payloads."""

    @staticmethod
    def compute(trace: Dict[str, Any]) -> Dict[str, Any]:
        steps = trace.get("steps", [])
        step_latencies = [float(step.get("latency_ms", 0.0)) for step in steps if "latency_ms" in step]
        tool_steps = [step for step in steps if str(step.get("action", "")).startswith(("retrieve", "call_", "generate"))]
        errored_steps = [step for step in steps if step.get("error")]

        return {
            "steps": len(steps),
            "tool_calls": len(tool_steps),
            "avg_step_latency_ms": round(sum(step_latencies) / len(step_latencies), 3) if step_latencies else 0.0,
            "total_latency_ms": float(trace.get("total_latency_ms", 0.0)),
            "error_count": len(errored_steps),
            "success": trace.get("status") == "success",
        }

    @staticmethod
    def aggregate(traces: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        rows = [MetricsCollector.compute(trace) for trace in traces]
        if not rows:
            return {
                "runs": 0,
                "avg_steps_per_task": 0.0,
                "avg_latency_ms": 0.0,
                "tool_success_rate": 0.0,
                "failure_rate": 0.0,
            }

        runs = len(rows)
        successes = sum(1 for row in rows if row["success"])
        return {
            "runs": runs,
            "avg_steps_per_task": round(sum(row["steps"] for row in rows) / runs, 3),
            "avg_latency_ms": round(sum(row["total_latency_ms"] for row in rows) / runs, 3),
            "tool_success_rate": round(successes / runs, 3),
            "failure_rate": round(1.0 - (successes / runs), 3),
        }
