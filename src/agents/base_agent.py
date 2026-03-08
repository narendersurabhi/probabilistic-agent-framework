"""Base interface for pluggable arena agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    """Plugin contract for all Agent Arena participants."""

    name: str

    @abstractmethod
    def run(self, query: str) -> Dict[str, Any]:
        """Run the agent on a query and return normalized or semi-normalized output."""
        raise NotImplementedError
