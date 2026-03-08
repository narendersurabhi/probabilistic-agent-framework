"""Metric helpers for tool-use benchmarks."""

from __future__ import annotations

from typing import Dict, List


def _safe_rate(numerator: int, denominator: int) -> float:
    return float(numerator / denominator) if denominator else 0.0


def tool_selection_accuracy(rows: List[Dict]) -> float:
    return _safe_rate(sum(bool(r.get("tool_correct")) for r in rows), len(rows))


def argument_accuracy(rows: List[Dict]) -> float:
    eligible = [r for r in rows if r.get("arguments_evaluated", True)]
    return _safe_rate(sum(bool(r.get("arguments_correct")) for r in eligible), len(eligible))


def sequence_accuracy(rows: List[Dict]) -> float:
    eligible = [r for r in rows if r.get("sequence_evaluated")]
    return _safe_rate(sum(bool(r.get("sequence_correct")) for r in eligible), len(eligible))


def first_step_accuracy(rows: List[Dict]) -> float:
    return _safe_rate(sum(bool(r.get("first_step_correct")) for r in rows), len(rows))


def task_completion_rate(rows: List[Dict]) -> float:
    return _safe_rate(sum(bool(r.get("completed")) for r in rows), len(rows))


def aggregate_metrics(rows: List[Dict]) -> Dict[str, float]:
    return {
        "tool_selection_accuracy": tool_selection_accuracy(rows),
        "argument_accuracy": argument_accuracy(rows),
        "sequence_accuracy": sequence_accuracy(rows),
        "first_step_accuracy": first_step_accuracy(rows),
        "task_completion_rate": task_completion_rate(rows),
    }
