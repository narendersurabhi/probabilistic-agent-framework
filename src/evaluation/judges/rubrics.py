"""Prompt templates and rubrics for LLM-as-a-judge scoring."""

from __future__ import annotations

DEFAULT_RAG_RUBRIC = """You are an expert evaluator of AI system outputs.

Evaluate the model answer using this rubric:
1. Correctness: Is the answer factually consistent with the question and ground truth?
2. Faithfulness: Is the answer supported by the retrieved context without introducing unsupported claims?
3. Completeness: Does the answer fully address the user question?

Return strict JSON with this schema:
{
  "correctness_score": 1-10,
  "faithfulness_score": 1-10,
  "completeness_score": 1-10,
  "explanation": "short explanation"
}
"""


def build_rag_judge_prompt(
    question: str,
    context: str,
    answer: str,
    ground_truth: str,
    rubric: str = DEFAULT_RAG_RUBRIC,
) -> str:
    """Build a deterministic prompt for RAG quality judging."""
    return (
        f"{rubric}\n"
        f"Question:\n{question}\n\n"
        f"Retrieved Context:\n{context}\n\n"
        f"Model Answer:\n{answer}\n\n"
        f"Ground Truth:\n{ground_truth}\n"
    )
