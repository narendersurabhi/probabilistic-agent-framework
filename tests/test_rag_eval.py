import json
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAG_SRC = ROOT / "rag_eval" / "src"
if str(RAG_SRC) not in sys.path:
    sys.path.insert(0, str(RAG_SRC))

from rag_eval.evaluator import RAGEvaluator
from rag_eval.generator import SimpleGenerator
from rag_eval.metrics import answer_accuracy, context_precision, faithfulness, hallucination_rate, retrieval_recall
from rag_eval.retriever import KeywordRetriever


def test_rag_metrics_behave_as_expected() -> None:
    docs = ["France is a country in Europe. Its capital city is Paris."]
    relevant = ["France is a country in Europe. Its capital city is Paris."]

    assert retrieval_recall(docs, relevant) == 1.0
    assert context_precision(docs, relevant) == 1.0
    assert answer_accuracy("Paris", "Paris") == 1.0
    assert faithfulness("Paris", docs) == 1.0
    assert hallucination_rate("Paris", docs) == 0.0


def test_rag_pipeline_components() -> None:
    retriever = KeywordRetriever(
        [
            "France is a country in Europe. Its capital city is Paris.",
            "Berlin is the capital of Germany.",
        ]
    )
    docs = retriever.retrieve("What is the capital of France?")
    answer = SimpleGenerator().generate("What is the capital of France?", docs)
    result = RAGEvaluator().evaluate(
        question="What is the capital of France?",
        answer=answer,
        retrieved_docs=docs,
        ground_truth="Paris",
        relevant_documents=["France is a country in Europe. Its capital city is Paris."],
    )

    assert docs
    assert result.retrieval_recall == 1.0
    assert result.answer_accuracy == 1.0
    assert result.judge_correctness is None


def test_run_rag_eval_script_writes_results(tmp_path: Path, monkeypatch) -> None:
    rag_root = tmp_path / "rag_eval"
    (rag_root / "datasets").mkdir(parents=True)
    (rag_root / "experiments").mkdir(parents=True)
    source_root = Path(__file__).resolve().parents[1] / "rag_eval"
    dataset_text = (source_root / "datasets" / "qa_dataset.json").read_text(encoding="utf-8")
    (rag_root / "datasets" / "qa_dataset.json").write_text(dataset_text, encoding="utf-8")

    script_path = source_root / "experiments" / "run_rag_eval.py"
    monkeypatch.setenv("RAG_EVAL_ROOT", str(rag_root))
    runpy.run_path(str(script_path), run_name="__main__")

    result_path = rag_root / "results" / "rag_eval_results.json"
    assert result_path.exists()
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    assert "summary" in payload
    assert "answer_accuracy" in payload["summary"]
    assert "judge_correctness" in payload["summary"]
    judge_result_path = rag_root / "results" / "rag_judge_results.json"
    assert judge_result_path.exists()
