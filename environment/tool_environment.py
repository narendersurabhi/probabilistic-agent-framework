"""Deterministic swappable tool execution environment."""

from __future__ import annotations

from typing import Any, Dict

from pydantic import ValidationError

from tools.calculator import run_calculator
from tools.retriever import run_retriever
from tools.tool_schema import (
    AskUserArgs,
    CalculatorArgs,
    GenerateAnswerArgs,
    RetrieverArgs,
    ToolOutput,
)


class ToolEnvironment:
    def execute(self, action: str, arguments: Dict[str, Any]) -> ToolOutput:
        try:
            if action == "retrieve_docs":
                return run_retriever(RetrieverArgs(**arguments))
            if action == "call_calculator":
                return run_calculator(CalculatorArgs(**arguments))
            if action == "ask_user":
                AskUserArgs(**arguments)
                return ToolOutput(tool="ask_user", success=True, result="Need clarification")
            if action == "generate_answer":
                GenerateAnswerArgs(**arguments)
                return ToolOutput(tool="generate_answer", success=True, result="Final answer", metadata={"answer_generated": True})
            return ToolOutput(tool=action, success=False, result=None, metadata={"error": "unknown_action"})
        except ValidationError as exc:
            return ToolOutput(tool=action, success=False, result=None, metadata={"validation_error": exc.errors()})
