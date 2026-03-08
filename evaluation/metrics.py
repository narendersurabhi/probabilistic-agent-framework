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


def planning_accuracy(rows: List[Dict]) -> float:
    """Fraction of tasks where the full expected tool plan is matched."""
    return sequence_tool_accuracy(rows)


def average_planning_depth(rows: List[Dict]) -> float:
    """Average number of tool steps used per task."""
    return step_efficiency(rows)


def premature_action_rate(rows: List[Dict]) -> float:
    """How often the first tool action deviates from the expected first step."""
    if not rows:
        return 0.0
    premature = 0
    for row in rows:
        has_expected = row.get("has_expected_sequence", True)
        has_action = row.get("has_action", True)
        if has_expected and has_action and not row.get("first_step_correct", False):
            premature += 1
    return premature / len(rows)
