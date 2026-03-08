"""Deterministic answer generator for the local RAG harness."""

from __future__ import annotations

import re


class SimpleGenerator:
    """Generates concise answers with lightweight extraction heuristics."""

    def generate(self, question: str, retrieved_docs: list[str]) -> str:
        if not retrieved_docs:
            return "I do not know based on the provided context."

        question_lower = question.lower()
        joined = " ".join(retrieved_docs)

        if "capital" in question_lower:
            match = re.search(r"capital(?: city)? is ([A-Za-z ]+)", joined, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip().rstrip(".")

        if "largest ocean" in question_lower or "largest" in question_lower:
            match = re.search(r"the ([A-Za-z ]+ocean) is the largest", joined, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip().title()

        numeric_match = re.search(r" is ([0-9]+(?:\.[0-9]+)?)", joined)
        if numeric_match:
            return numeric_match.group(1)

        return retrieved_docs[0].split(".")[0].strip()
