from src.evaluation.failure_taxonomy import FailureTaxonomyAnalyzer


def test_failure_taxonomy_reasoning_error_and_hallucination() -> None:
    analyzer = FailureTaxonomyAnalyzer()

    reasoning_task = {"expected_tool": "generate_answer", "expected_answer": "42"}
    reasoning_trace = {
        "selected_tool": "generate_answer",
        "arguments": {"text": "41"},
        "completed": True,
        "final_answer": "41",
    }
    assert analyzer.classify(reasoning_task, reasoning_trace) == "reasoning_error"

    hallucination_trace = {
        "selected_tool": "generate_answer",
        "arguments": {"text": "42"},
        "completed": True,
        "hallucinated": True,
    }
    assert analyzer.classify({"expected_tool": "generate_answer"}, hallucination_trace) == "hallucination"
