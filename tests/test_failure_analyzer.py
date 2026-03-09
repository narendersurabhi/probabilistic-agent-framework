from src.evaluation.failure_analyzer import FailureAnalyzer


def test_failure_analyzer_tool_selection_error() -> None:
    analyzer = FailureAnalyzer()
    task = {"expected_tool": "retrieve_docs"}
    result = {"selected_tool": "generate_answer", "arguments": {}, "steps": [], "completed": True}
    assert analyzer.analyze(task, result) == "tool_selection_error"


def test_failure_analyzer_tool_argument_error() -> None:
    analyzer = FailureAnalyzer()
    task = {"expected_tool": "call_calculator", "expected_args": {"expression": "350 * 0.12"}}
    result = {
        "selected_tool": "call_calculator",
        "arguments": {"expression": "350 * 12"},
        "steps": [{"action": "call_calculator"}],
        "completed": True,
    }
    assert analyzer.analyze(task, result) == "tool_argument_error"


def test_failure_analyzer_premature_action_and_missing_step() -> None:
    analyzer = FailureAnalyzer()
    task = {"expected_tool_sequence": ["retrieve_docs", "call_calculator"]}

    premature = {
        "selected_tool": "call_calculator",
        "arguments": {"expression": "200 * 0.2"},
        "steps": [{"action": "call_calculator"}],
        "completed": True,
    }
    assert analyzer.analyze(task, premature) == "premature_action"

    missing_step = {
        "selected_tool": "retrieve_docs",
        "arguments": {"query": "population of spain"},
        "steps": [{"action": "retrieve_docs"}],
        "completed": False,
    }
    assert analyzer.analyze(task, missing_step) == "missing_step"


def test_failure_analyzer_incorrect_sequence() -> None:
    analyzer = FailureAnalyzer()
    task = {"expected_tool_sequence": ["retrieve_docs", "call_calculator", "generate_answer"]}
    result = {
        "selected_tool": "generate_answer",
        "arguments": {"text": "answer"},
        "steps": [
            {"action": "retrieve_docs"},
            {"action": "generate_answer"},
            {"action": "call_calculator"},
        ],
        "completed": True,
    }
    assert analyzer.analyze(task, result) == "incorrect_sequence"
