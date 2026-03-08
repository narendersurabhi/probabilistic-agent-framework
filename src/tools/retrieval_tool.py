"""Deterministic retrieval tool backed by a static knowledge base."""

from __future__ import annotations

KNOWLEDGE_BASE: dict[str, dict[str, object]] = {
    "population of france": {"population": 67_000_000},
    "population of germany": {"population": 83_000_000},
    "reinforcement learning": {
        "description": "A machine learning paradigm where agents learn by interacting with environments."
    },
}


class RetrievalTool:
    """Return deterministic document payloads for known queries."""

    def execute(self, query: str) -> dict[str, object]:
        query_lower = query.lower()

        for key, payload in KNOWLEDGE_BASE.items():
            if key in query_lower:
                return {
                    "tool": "retriever",
                    "success": True,
                    "documents": payload,
                }

        return {
            "tool": "retriever",
            "success": False,
            "documents": None,
        }
