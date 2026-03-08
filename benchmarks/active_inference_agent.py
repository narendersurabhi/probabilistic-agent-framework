"""Benchmark wrapper around active inference planner stack."""

from __future__ import annotations

from typing import Any, Dict

from agents.learner_agent import LearnerAgent
from agents.planner_agent import PlannerAgent
from environment.tool_environment import ToolEnvironment
from llm.mock_llm import MockLLM
from llm.observation_parser import ObservationParser
from models.pomdp_model import build_default_model


class ActiveInferenceBenchmarkAgent:
    def __init__(self, max_steps: int = 3) -> None:
        model = build_default_model()
        self.planner = PlannerAgent(model=model)
        self.learner = LearnerAgent(model=model)
        self.env = ToolEnvironment()
        self.parser = ObservationParser()
        self.llm = MockLLM()
        self.max_steps = max_steps

    def run(self, query: str) -> Dict[str, Any]:
        obs = {"tool_success": True}
        trace = []
        for _ in range(self.max_steps):
            plan = self.planner.step(obs)
            action = plan.selected_action
            if action == "retrieve_docs":
                args = {"query": query}
            elif action == "call_calculator":
                _, args = self.llm.choose_tool(query)
            elif action == "ask_user":
                args = {"clarification_question": "Can you clarify your goal?"}
            else:
                args = {"draft": "Generated answer"}
            out = self.env.execute(action, args)
            obs = self.parser.parse(out)
            self.learner.update(action, obs)
            trace.append({"tool": action, "args": args, "obs": obs, "belief": plan.belief_state, "output": out.model_dump()})
            if obs.get("answer_generated"):
                break

        final = trace[-1]
        return {
            "tool": final["tool"],
            "args": final["args"],
            "trace": trace,
            "steps": len(trace),
            "completed": bool(final["obs"].get("answer_generated")),
            "beliefs": [t["belief"] for t in trace],
            "final_answer": final["output"]["result"] if final["obs"].get("answer_generated") else None,
        }
