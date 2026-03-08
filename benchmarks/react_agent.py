"""Simplified ReAct-style agent."""

from __future__ import annotations

from typing import Any, Dict

from environment.tool_environment import ToolEnvironment
from llm.mock_llm import MockLLM
from llm.observation_parser import ObservationParser


class ReActAgent:
    def __init__(self, max_steps: int = 2) -> None:
        self.llm = MockLLM()
        self.env = ToolEnvironment()
        self.parser = ObservationParser()
        self.max_steps = max_steps

    def run(self, query: str) -> Dict[str, Any]:
        traces = []
        obs = None
        for _ in range(self.max_steps):
            tool, args, thought = self.llm.reason_and_act(query, obs)
            output = self.env.execute(tool, args)
            obs = self.parser.parse(output)
            traces.append({"thought": thought, "tool": tool, "args": args, "obs": obs, "output": output.model_dump()})
            if obs.get("answer_generated"):
                break
        final = traces[-1]
        return {
            "tool": final["tool"],
            "args": final["args"],
            "trace": traces,
            "steps": len(traces),
            "completed": bool(final["obs"].get("answer_generated")),
            "final_answer": final["output"]["result"] if final["obs"].get("answer_generated") else None,
        }
