"""High-level evaluator for RAG task runs."""

from __future__ import annotations

from dataclasses import dataclass

from src.evaluation.judges import JudgeRunner

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
    judge_correctness: float | None = None
    judge_faithfulness: float | None = None
    judge_completeness: float | None = None
    judge_explanation: str | None = None


class RAGEvaluator:
    def __init__(self, judge_runner: JudgeRunner | None = None):
        self.judge_runner = judge_runner

    def evaluate(
        self,
        question: str,
        answer: str,
        retrieved_docs: list[str],
        ground_truth: str,
        relevant_documents: list[str],
    ) -> RAGTaskResult:
        task_result = RAGTaskResult(
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

        if self.judge_runner is not None:
            judge_result = self.judge_runner.evaluate_task(
                question=question,
                context_docs=retrieved_docs,
                answer=answer,
                ground_truth=ground_truth,
            )
            task_result.judge_correctness = float(judge_result.correctness_score)
            task_result.judge_faithfulness = float(judge_result.faithfulness_score)
            task_result.judge_completeness = float(judge_result.completeness_score)
            task_result.judge_explanation = judge_result.explanation

        return task_result

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
        summary = {
            key: sum(getattr(result, key) for result in results) / len(results)
            for key in keys
        }

        judged_results = [result for result in results if result.judge_correctness is not None]
        if judged_results:
            summary["judge_correctness"] = (
                sum(float(result.judge_correctness) for result in judged_results) / len(judged_results)
            )
            summary["judge_faithfulness"] = (
                sum(float(result.judge_faithfulness) for result in judged_results) / len(judged_results)
            )
            summary["judge_completeness"] = (
                sum(float(result.judge_completeness) for result in judged_results) / len(judged_results)
            )

        return summary
