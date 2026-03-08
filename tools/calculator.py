"""Calculator tool with strict validation."""

from __future__ import annotations

from tools.tool_schema import CalculatorArgs, ToolOutput


def run_calculator(args: CalculatorArgs) -> ToolOutput:
    safe_expression = args.expression.replace(" ", "")
    if not all(c in "0123456789+-*/()." for c in safe_expression):
        return ToolOutput(tool="calculator", success=False, result=None, metadata={"error": "invalid_chars"})
    try:
        value = eval(safe_expression, {"__builtins__": {}}, {})
    except Exception as exc:  # noqa: BLE001
        return ToolOutput(tool="calculator", success=False, result=None, metadata={"error": str(exc)})
    return ToolOutput(tool="calculator", success=True, result=value)
