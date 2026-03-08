"""Deterministic tool environment for benchmark and CI execution."""

from __future__ import annotations

from src.tools.calculator_tool import CalculatorTool
from src.tools.retrieval_tool import RetrievalTool


class ToolEnvironment:
    def __init__(self) -> None:
        self.calculator = CalculatorTool()
        self.retriever = RetrievalTool()

    def execute(self, tool_name: str, args: dict[str, object]) -> dict[str, object]:
        if tool_name == "call_calculator":
            expression = str(args.get("expression", ""))
            return self.calculator.execute(expression)

        if tool_name == "retrieve_docs":
            query = str(args.get("query", ""))
            return self.retriever.execute(query)

        if tool_name == "generate_answer":
            text = str(args.get("text") or args.get("draft") or "")
            return {"tool": "generate_answer", "success": True, "answer_generated": True, "result": text}

        return {"tool": tool_name, "success": False, "result": None}
