"""Evaluation harness for single active inference runs."""

from __future__ import annotations

from typing import Any, Dict

from agents.critic_agent import CriticAgent
from agents.learner_agent import LearnerAgent
from agents.planner_agent import PlannerAgent
from environment.tool_environment import ToolEnvironment
from llm.observation_parser import ObservationParser
from logging.run_logger import RunLogger
from models.pomdp_model import build_default_model


class AgentHarness:
    def __init__(self) -> None:
        model = build_default_model()
        self.planner = PlannerAgent(model=model)
        self.critic = CriticAgent()
        self.learner = LearnerAgent(model=model)
        self.env = ToolEnvironment()
        self.parser = ObservationParser()
        self.logger = RunLogger()

    def run_step(self, step: int, query: str, expected_tool: str, arguments: Dict[str, Any], expected_args: Dict[str, Any] | None = None) -> Dict[str, Any]:
        planner_output = self.planner.step({"tool_success": step == 0})
        action = planner_output.selected_action
        tool_args = arguments
        tool_output = self.env.execute(action, tool_args)
        obs = self.parser.parse(tool_output)
        critic = self.critic.evaluate(expected_tool, action, tool_args, expected_args, obs)
        self.learner.update(action, obs)
        row = {
            "step": step,
            "query": query,
            "belief_state": planner_output.belief_state,
            "selected_action": action,
            "policy_probabilities": planner_output.policy_probabilities,
            "expected_free_energy": planner_output.expected_free_energy,
            "tool_output": tool_output.model_dump(),
            "critic_evaluation": critic,
            "success_or_failure": obs["tool_success"],
        }
        self.logger.log(
            {
                "query": query,
                "chosen_tool": action,
                "arguments": tool_args,
                "tool_output": tool_output.model_dump(),
                "critic_result": critic,
                "success_or_failure": obs["tool_success"],
            }
        )
        return row
