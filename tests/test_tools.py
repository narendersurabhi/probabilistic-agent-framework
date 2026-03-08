from pydantic import ValidationError

from environment.tool_environment import ToolEnvironment
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
