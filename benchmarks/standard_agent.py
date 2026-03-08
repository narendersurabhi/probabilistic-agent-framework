"""Standard LLM tool agent without planning."""

from __future__ import annotations

from typing import Any, Dict

from environment.tool_environment import ToolEnvironment
from llm.mock_llm import MockLLM
from llm.observation_parser import ObservationParser


class StandardToolAgent:
    def __init__(self) -> None:
        self.llm = MockLLM()
        self.env = ToolEnvironment()
        self.parser = ObservationParser()

    def run(self, query: str) -> Dict[str, Any]:
        tool, args = self.llm.choose_tool(query)
        output = self.env.execute(tool, args)
        obs = self.parser.parse(output)
        trace = [{"tool": tool, "args": args, "obs": obs, "output": output.model_dump()}]
        return {
            "tool": tool,
            "args": args,
            "output": output.model_dump(),
            "observation": obs,
            "trace": trace,
            "steps": len(trace),
            "completed": bool(obs.get("answer_generated")),
            "final_answer": output.result if obs.get("answer_generated") else None,
        }
