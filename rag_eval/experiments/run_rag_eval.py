"""Run deterministic RAG evaluation pipeline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAG_ROOT = Path(__import__("os").environ.get("RAG_EVAL_ROOT", ROOT / "rag_eval"))
SRC_DIR = RAG_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from rag_eval.evaluator import RAGEvaluator
from rag_eval.generator import SimpleGenerator
from rag_eval.retriever import KeywordRetriever


def _plot_metrics(metrics: dict[str, float], out_path: Path) -> Path:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        out_path.write_text("matplotlib not installed; plot unavailable\n", encoding="utf-8")
        return out_path

    keys = ["retrieval_recall", "answer_accuracy", "hallucination_rate"]
    values = [metrics[key] for key in keys]
    labels = ["Retrieval Recall", "Answer Accuracy", "Hallucination Rate"]

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(labels, values, color=["#4CAF50", "#2196F3", "#FF9800"])
    ax.set_ylim(0.0, 1.0)
    ax.set_ylabel("Score")
    ax.set_title("RAG Evaluation Metrics")

    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.02, f"{value:.2f}", ha="center")

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path)
    plt.close(fig)
    return out_path


def main() -> None:
    dataset_path = RAG_ROOT / "datasets" / "qa_dataset.json"
    output_path = RAG_ROOT / "results" / "rag_eval_results.json"
    plot_path = RAG_ROOT / "results" / "rag_eval_metrics.png"

    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    evaluator = RAGEvaluator()
    generator = SimpleGenerator()

    task_results = []
    for item in dataset:
        retriever = KeywordRetriever(item["corpus"])
        retrieved_docs = retriever.retrieve(item["question"], top_k=3)
        answer = generator.generate(item["question"], retrieved_docs)
        result = evaluator.evaluate(
            question=item["question"],
            answer=answer,
            retrieved_docs=retrieved_docs,
            ground_truth=item["ground_truth"],
            relevant_documents=item["relevant_documents"],
        )
        task_results.append(result)

    aggregate = evaluator.aggregate(task_results)
    payload = {
        "summary": aggregate,
        "tasks": [result.__dict__ for result in task_results],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _plot_metrics(aggregate, plot_path)

    print(f"Retrieval Recall: {aggregate['retrieval_recall']:.2f}")
    print(f"Context Precision: {aggregate['context_precision']:.2f}")
    print(f"Answer Accuracy: {aggregate['answer_accuracy']:.2f}")
    print(f"Faithfulness: {aggregate['faithfulness']:.2f}")
    print(f"Hallucination Rate: {aggregate['hallucination_rate']:.2f}")
    print(f"Saved: {output_path}")
    print(f"Saved: {plot_path}")


if __name__ == "__main__":
    main()
