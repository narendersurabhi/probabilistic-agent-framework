"""Flagship demo script for deterministic RAG evaluation and judge scoring."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    print("RAG Evaluation Results\n")
    cmd = [sys.executable, str(ROOT / "rag_eval" / "experiments" / "run_rag_eval.py")]
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{ROOT}:{env.get('PYTHONPATH', '')}"
    subprocess.run(cmd, check=True, env=env)

    source_results = ROOT / "rag_eval" / "results" / "rag_eval_results.json"
    source_payload = json.loads(source_results.read_text(encoding="utf-8"))
    summary = source_payload["summary"]

    print(f"Retrieval Recall: {summary['retrieval_recall']:.2f}")
    print(f"Answer Accuracy: {summary['answer_accuracy']:.2f}")
    print(f"Faithfulness: {summary['faithfulness']:.2f}")
    print(f"Hallucination Rate: {summary['hallucination_rate']:.2f}")
    print(f"LLM Judge Correctness: {summary['judge_correctness']:.2f}")

    target_results = ROOT / "results" / "rag_eval_results.json"
    target_results.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_results, target_results)
    print("\nSaved to:")
    print("results/rag_eval_results.json")


if __name__ == "__main__":
    main()
