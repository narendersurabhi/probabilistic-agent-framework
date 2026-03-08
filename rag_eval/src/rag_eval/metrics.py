"""RAG evaluation metrics."""

from __future__ import annotations


def retrieval_recall(retrieved_docs: list[str], relevant_docs: list[str]) -> float:
    if not relevant_docs:
        return 1.0
    hits = sum(1 for doc in relevant_docs if doc in retrieved_docs)
    return hits / len(relevant_docs)


def context_precision(retrieved_docs: list[str], relevant_docs: list[str]) -> float:
    total_tokens = sum(len(doc.split()) for doc in retrieved_docs)
    if total_tokens == 0:
        return 0.0

    relevant_tokens = 0
    relevant_set = set(relevant_docs)
    for doc in retrieved_docs:
        if doc in relevant_set:
            relevant_tokens += len(doc.split())
    return relevant_tokens / total_tokens


def answer_accuracy(answer: str, ground_truth: str) -> float:
    return 1.0 if answer.strip().lower() == ground_truth.strip().lower() else 0.0


def _tokens(text: str) -> set[str]:
    import re

    return {token.lower() for token in re.findall(r"[A-Za-z0-9]+", text)}


def faithfulness(answer: str, retrieved_docs: list[str]) -> float:
    answer_tokens = _tokens(answer)
    context_tokens = set().union(*(_tokens(doc) for doc in retrieved_docs)) if retrieved_docs else set()
    if not answer_tokens:
        return 0.0
    return len(answer_tokens.intersection(context_tokens)) / len(answer_tokens)


def hallucination_rate(answer: str, retrieved_docs: list[str]) -> float:
    return 1.0 - faithfulness(answer, retrieved_docs)
