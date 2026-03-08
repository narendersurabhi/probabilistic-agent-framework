"""High-level evaluator for RAG task runs."""

from __future__ import annotations

from dataclasses import dataclass

from . import metrics


@dataclass
class RAGTaskResult:
    question: str
    answer: str
    ground_truth: str
    retrieved_docs: list[str]
    relevant_documents: list[str]
    retrieval_recall: float
    context_precision: float
    answer_accuracy: float
    faithfulness: float
    hallucination_rate: float


class RAGEvaluator:
    def evaluate(
        self,
        question: str,
        answer: str,
        retrieved_docs: list[str],
        ground_truth: str,
        relevant_documents: list[str],
    ) -> RAGTaskResult:
        return RAGTaskResult(
            question=question,
            answer=answer,
            ground_truth=ground_truth,
            retrieved_docs=retrieved_docs,
            relevant_documents=relevant_documents,
            retrieval_recall=metrics.retrieval_recall(retrieved_docs, relevant_documents),
            context_precision=metrics.context_precision(retrieved_docs, relevant_documents),
            answer_accuracy=metrics.answer_accuracy(answer, ground_truth),
            faithfulness=metrics.faithfulness(answer, retrieved_docs),
            hallucination_rate=metrics.hallucination_rate(answer, retrieved_docs),
        )

    def aggregate(self, results: list[RAGTaskResult]) -> dict[str, float]:
        if not results:
            return {
                "retrieval_recall": 0.0,
                "context_precision": 0.0,
                "answer_accuracy": 0.0,
                "faithfulness": 0.0,
                "hallucination_rate": 0.0,
            }

        keys = [
            "retrieval_recall",
            "context_precision",
            "answer_accuracy",
            "faithfulness",
            "hallucination_rate",
        ]
        return {
            key: sum(getattr(result, key) for result in results) / len(results)
            for key in keys
        }
