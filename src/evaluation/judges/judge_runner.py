"""Helpers to run LLM-judge scoring over RAG task outputs."""

from __future__ import annotations

from dataclasses import dataclass

from src.evaluation.judges.llm_judge import JudgeResult, LLMJudge


@dataclass
class JudgeAggregate:
    correctness: float
    faithfulness: float
    completeness: float

    def to_dict(self) -> dict[str, float]:
        return {
            "judge_correctness": self.correctness,
            "judge_faithfulness": self.faithfulness,
            "judge_completeness": self.completeness,
        }


class JudgeRunner:
    def __init__(self, judge: LLMJudge):
        self.judge = judge

    def evaluate_task(
        self,
        question: str,
        context_docs: list[str],
        answer: str,
        ground_truth: str,
    ) -> JudgeResult:
        context = "\n".join(context_docs)
        return self.judge.evaluate(
            question=question,
            context=context,
            answer=answer,
            ground_truth=ground_truth,
        )

    def aggregate(self, results: list[JudgeResult]) -> JudgeAggregate:
        if not results:
            return JudgeAggregate(correctness=0.0, faithfulness=0.0, completeness=0.0)

        denom = float(len(results))
        return JudgeAggregate(
            correctness=sum(result.correctness_score for result in results) / denom,
            faithfulness=sum(result.faithfulness_score for result in results) / denom,
            completeness=sum(result.completeness_score for result in results) / denom,
        )
