"""Deterministic mock LLM implementation used in CI benchmark mode."""

from __future__ import annotations

import os


class MockLLM:
    def __init__(self) -> None:
        self.provider = os.getenv("LLM_PROVIDER", "fake")

    def extract_state(self, query: str) -> dict[str, str]:
        if "%" in query:
            return {"intent": "calculation"}
        if "population" in query.lower():
            return {"intent": "retrieval"}
        return {"intent": "answer"}
