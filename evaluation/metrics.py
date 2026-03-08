"""Evaluation and benchmark metrics."""

from __future__ import annotations

from typing import Dict, List

import numpy as np


def tool_selection_accuracy(rows: List[Dict]) -> float:
    if not rows:
        return 0.0
    return sum(1 for r in rows if r.get("tool_correct")) / len(rows)


def argument_accuracy(rows: List[Dict]) -> float:
    if not rows:
        return 0.0
    return sum(1 for r in rows if r.get("arguments_correct")) / len(rows)


def task_completion_rate(rows: List[Dict]) -> float:
    if not rows:
        return 0.0
    return sum(1 for r in rows if r.get("completed")) / len(rows)


def step_efficiency(rows: List[Dict]) -> float:
    if not rows:
        return 0.0
    return float(np.mean([r.get("steps", 0) for r in rows]))


def belief_entropy_reduction(entropies: List[float]) -> float:
    if len(entropies) < 2:
        return 0.0
    return float(entropies[0] - entropies[-1])


def sequence_tool_accuracy(rows: List[Dict]) -> float:
    if not rows:
        return 0.0
    return sum(1 for r in rows if r.get("sequence_exact")) / len(rows)


def prefix_accuracy(rows: List[Dict]) -> float:
    if not rows:
        return 0.0
    return float(np.mean([r.get("prefix_ratio", 0.0) for r in rows]))


def final_answer_accuracy(rows: List[Dict]) -> float:
    if not rows:
        return 0.0
    return sum(1 for r in rows if r.get("final_answer_correct")) / len(rows)


def first_step_accuracy(rows: List[Dict]) -> float:
    if not rows:
        return 0.0
    return sum(1 for r in rows if r.get("first_step_correct")) / len(rows)
