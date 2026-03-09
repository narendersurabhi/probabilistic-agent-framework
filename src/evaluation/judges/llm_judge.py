"""LLM-as-a-judge evaluators and deterministic fallback client."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Protocol

from src.evaluation.judges.rubrics import build_rag_judge_prompt


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:
        """Generate a response for the supplied prompt."""


@dataclass
class JudgeResult:
    correctness_score: int
    faithfulness_score: int
    completeness_score: int
    explanation: str

    def to_dict(self) -> dict[str, int | str]:
        return asdict(self)


class HeuristicJudgeClient:
    """Deterministic scorer for offline/local judge evaluation."""

    def generate(self, prompt: str) -> str:
        answer = _extract_block(prompt, "Model Answer:")
        ground_truth = _extract_block(prompt, "Ground Truth:")
        context = _extract_block(prompt, "Retrieved Context:")

        normalized_answer = answer.strip().lower()
        normalized_ground = ground_truth.strip().lower()
        normalized_context = context.strip().lower()

        correctness = 10 if normalized_answer == normalized_ground else 6
        faithfulness = 10 if normalized_answer and normalized_answer in normalized_context else 6
        completeness = 9 if normalized_answer else 2

        payload = {
            "correctness_score": correctness,
            "faithfulness_score": faithfulness,
            "completeness_score": completeness,
            "explanation": "Deterministic heuristic judge scored lexical overlap against context and ground truth.",
        }
        return json.dumps(payload)


class LLMJudge:
    """Prompt-based judge that requests rubric-aligned JSON scores from an LLM client."""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def evaluate(self, question: str, context: str, answer: str, ground_truth: str) -> JudgeResult:
        prompt = build_rag_judge_prompt(
            question=question,
            context=context,
            answer=answer,
            ground_truth=ground_truth,
        )
        response = self.llm.generate(prompt)
        payload = json.loads(response)

        return JudgeResult(
            correctness_score=int(payload["correctness_score"]),
            faithfulness_score=int(payload["faithfulness_score"]),
            completeness_score=int(payload["completeness_score"]),
            explanation=str(payload.get("explanation", "")),
        )


def _extract_block(prompt: str, marker: str) -> str:
    if marker not in prompt:
        return ""

    after = prompt.split(marker, maxsplit=1)[1]
    candidates = ["\n\nModel Answer:", "\n\nGround Truth:", "\n\nQuestion:\n", "\n\nRetrieved Context:\n"]
    end = len(after)
    for candidate in candidates:
        idx = after.find(candidate)
        if idx != -1:
            end = min(end, idx)
    return after[:end].strip()
