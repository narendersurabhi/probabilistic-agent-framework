"""Simple deterministic retriever used for repeatable RAG evaluation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RetrievedDocument:
    text: str
    score: float


class KeywordRetriever:
    """Scores documents by token overlap with the input question."""

    def __init__(self, corpus: list[str]) -> None:
        self.corpus = corpus

    def retrieve(self, question: str, top_k: int = 3) -> list[str]:
        question_tokens = {token.lower() for token in question.split() if token}
        scored: list[RetrievedDocument] = []
        for doc in self.corpus:
            doc_tokens = {token.lower() for token in doc.split() if token}
            overlap = len(question_tokens.intersection(doc_tokens))
            if overlap == 0:
                continue
            score = overlap / max(len(question_tokens), 1)
            scored.append(RetrievedDocument(text=doc, score=score))

        scored.sort(key=lambda item: item.score, reverse=True)
        return [item.text for item in scored[:top_k]]
