"""Deterministic calculator tool used for benchmark execution."""

from __future__ import annotations


class CalculatorTool:
    """Evaluate arithmetic expressions deterministically."""

    _ALLOWED_CHARS = set("0123456789+-*/(). ")

    def execute(self, expression: str) -> dict[str, object]:
        if not expression or any(ch not in self._ALLOWED_CHARS for ch in expression):
            return {"tool": "calculator", "success": False, "result": None}

        try:
            result = eval(expression, {"__builtins__": {}}, {})
        except Exception:  # noqa: BLE001
            return {"tool": "calculator", "success": False, "result": None}

        return {"tool": "calculator", "success": True, "result": result}
