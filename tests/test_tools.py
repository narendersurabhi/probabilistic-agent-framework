from pydantic import ValidationError

from environment.tool_environment import ToolEnvironment
from src.environment.tool_environment import ToolEnvironment as SrcToolEnvironment
from src.llm.observation_parser import parse_observation
from tools.tool_schema import CalculatorArgs


def test_calculator_schema_validation() -> None:
    try:
        CalculatorArgs(expression="")
        assert False
    except ValidationError:
        assert True


def test_environment_calculator_success() -> None:
    env = ToolEnvironment()
    out = env.execute("call_calculator", {"expression": "2+2"})
    assert out.success is True
    assert out.result == 4


def test_environment_retriever_no_match_fails() -> None:
    env = ToolEnvironment()
    out = env.execute("retrieve_docs", {"query": "Unrelated topic"})
    assert out.success is False
    assert out.metadata["relevant_doc_found"] is False


def test_src_tool_environment_deterministic_results() -> None:
    env = SrcToolEnvironment()
    calc = env.execute("call_calculator", {"expression": "350 * 0.12"})
    retr = env.execute("retrieve_docs", {"query": "population of france"})

    assert calc["success"] is True
    assert calc["result"] == 42.0
    assert retr["success"] is True
    assert retr["documents"]["population"] == 67_000_000


def test_src_observation_parser() -> None:
    assert parse_observation({"tool": "calculator", "success": True}) == "tool_success"
    assert parse_observation({"tool": "retriever", "success": True}) == "relevant_doc_found"
    assert parse_observation({"tool": "retriever", "success": False}) == "doc_not_relevant"
