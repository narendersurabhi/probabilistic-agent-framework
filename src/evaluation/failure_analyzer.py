"""Backward-compatible failure analyzer built on the failure taxonomy classifier."""

from __future__ import annotations

from typing import Any, Dict

from src.evaluation.failure_taxonomy import FailureTaxonomyAnalyzer


class FailureAnalyzer:
    """Compatibility wrapper for taxonomy-based failure classification."""

    FAILURE_TYPES = FailureTaxonomyAnalyzer.FAILURE_TYPES

    def __init__(self) -> None:
        self._taxonomy = FailureTaxonomyAnalyzer()

    def analyze(self, task: Dict[str, Any], normalized: Dict[str, Any]) -> str:
        return self._taxonomy.classify(task, normalized)
