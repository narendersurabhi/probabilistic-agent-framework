"""Pydantic schemas for strict tool validation."""

from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel, Field


class CalculatorArgs(BaseModel):
    expression: str = Field(min_length=1)


class RetrieverArgs(BaseModel):
    query: str = Field(min_length=2)


class AskUserArgs(BaseModel):
    clarification_question: str = Field(min_length=2)


class GenerateAnswerArgs(BaseModel):
    draft: str = Field(min_length=1)


class ToolOutput(BaseModel):
    tool: str
    success: bool
    result: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)
