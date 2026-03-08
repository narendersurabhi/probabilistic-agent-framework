"""Active Inference planner for tool-selection in LLM agents.

This module exposes an ``ActiveInferencePlanner`` that maintains beliefs over
hidden states, evaluates policies using expected free energy (G), and selects
an action/tool minimizing G.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np
from pydantic import BaseModel, Field


class PlannerSnapshot(BaseModel):
    """Structured planner output for trace/logging systems."""

    belief_state: Dict[str, Dict[str, float]]
    policy_probabilities: Dict[str, float]
    expected_free_energy: Dict[str, float]
    selected_action: str


@dataclass
class StateSpace:
    """Discrete state, observation, and action definitions."""

    knowledge_state: List[str]
    task_stage: List[str]
    tool_effectiveness: List[str]
    observations: List[str]
    actions: List[str]


class ActiveInferencePlanner:
    """Active Inference planner built around POMDP matrices.

    The implementation keeps matrices readable and provides an optional `pymdp`
    agent initialization when available.
    """

    def __init__(self) -> None:
        self.space = StateSpace(
            knowledge_state=["unknown", "partial", "confident"],
            task_stage=["start", "retrieving", "solving", "complete"],
            tool_effectiveness=["low", "medium", "high"],
            observations=[
                "relevant_doc_found",
                "doc_not_relevant",
                "tool_success",
                "tool_failure",
                "answer_generated",
            ],
            actions=["retrieve_docs", "call_calculator", "generate_answer"],
        )

        self.A = self._build_A()
        self.B = self._build_B()
        self.C = self._build_C()
        self.D = self._build_D()

        self.qs = {
            "knowledge_state": self.D["knowledge_state"].copy(),
            "task_stage": self.D["task_stage"].copy(),
            "tool_effectiveness": self.D["tool_effectiveness"].copy(),
        }

        self._last_eval: Tuple[Dict[str, float], Dict[str, float]] = ({}, {})
        self._last_selected_action = self.space.actions[0]
        self._init_pymdp_agent_if_available()

    @staticmethod
    def _normalize(arr: np.ndarray) -> np.ndarray:
        arr = np.asarray(arr, dtype=float)
        s = arr.sum()
        if s <= 0:
            return np.ones_like(arr) / len(arr)
        return arr / s

    def _build_A(self) -> Dict[str, np.ndarray]:
        """Build observation likelihood per state factor.

        A_factor[o, s] := P(observation=o | state=s_factor)
        """
        n_obs = len(self.space.observations)

        A_knowledge = np.full((n_obs, len(self.space.knowledge_state)), 0.05)
        A_knowledge[self.space.observations.index("doc_not_relevant"), self.space.knowledge_state.index("unknown")] = 0.55
        A_knowledge[self.space.observations.index("relevant_doc_found"), self.space.knowledge_state.index("partial")] = 0.45
        A_knowledge[self.space.observations.index("answer_generated"), self.space.knowledge_state.index("confident")] = 0.65
        A_knowledge = np.apply_along_axis(self._normalize, 0, A_knowledge)

        A_task = np.full((n_obs, len(self.space.task_stage)), 0.05)
        A_task[self.space.observations.index("relevant_doc_found"), self.space.task_stage.index("retrieving")] = 0.65
        A_task[self.space.observations.index("tool_success"), self.space.task_stage.index("solving")] = 0.6
        A_task[self.space.observations.index("answer_generated"), self.space.task_stage.index("complete")] = 0.75
        A_task[self.space.observations.index("tool_failure"), self.space.task_stage.index("start")] = 0.55
        A_task = np.apply_along_axis(self._normalize, 0, A_task)

        A_eff = np.full((n_obs, len(self.space.tool_effectiveness)), 0.05)
        A_eff[self.space.observations.index("tool_failure"), self.space.tool_effectiveness.index("low")] = 0.65
        A_eff[self.space.observations.index("tool_success"), self.space.tool_effectiveness.index("medium")] = 0.45
        A_eff[self.space.observations.index("answer_generated"), self.space.tool_effectiveness.index("high")] = 0.5
        A_eff = np.apply_along_axis(self._normalize, 0, A_eff)

        return {
            "knowledge_state": A_knowledge,
            "task_stage": A_task,
            "tool_effectiveness": A_eff,
        }

    def _build_B(self) -> Dict[str, np.ndarray]:
        """Build action-dependent transition matrices B[s'|s,a] per state factor."""
        n_actions = len(self.space.actions)

        B_knowledge = np.zeros((len(self.space.knowledge_state), len(self.space.knowledge_state), n_actions))
        B_task = np.zeros((len(self.space.task_stage), len(self.space.task_stage), n_actions))
        B_eff = np.zeros((len(self.space.tool_effectiveness), len(self.space.tool_effectiveness), n_actions))

        for a_idx, action in enumerate(self.space.actions):
            k = np.eye(len(self.space.knowledge_state)) * 0.65
            t = np.eye(len(self.space.task_stage)) * 0.65
            e = np.eye(len(self.space.tool_effectiveness)) * 0.7

            if action == "retrieve_docs":
                k[self.space.knowledge_state.index("partial"), self.space.knowledge_state.index("unknown")] += 0.3
                t[self.space.task_stage.index("retrieving"), self.space.task_stage.index("start")] += 0.35
            elif action == "call_calculator":
                t[self.space.task_stage.index("solving"), self.space.task_stage.index("retrieving")] += 0.35
                t[self.space.task_stage.index("complete"), self.space.task_stage.index("solving")] += 0.2
            elif action == "generate_answer":
                k[self.space.knowledge_state.index("confident"), self.space.knowledge_state.index("partial")] += 0.25
                t[self.space.task_stage.index("complete"), self.space.task_stage.index("solving")] += 0.35
                e[self.space.tool_effectiveness.index("high"), self.space.tool_effectiveness.index("medium")] += 0.2

            B_knowledge[:, :, a_idx] = np.apply_along_axis(self._normalize, 0, k)
            B_task[:, :, a_idx] = np.apply_along_axis(self._normalize, 0, t)
            B_eff[:, :, a_idx] = np.apply_along_axis(self._normalize, 0, e)

        return {
            "knowledge_state": B_knowledge,
            "task_stage": B_task,
            "tool_effectiveness": B_eff,
        }

    def _build_C(self) -> np.ndarray:
        """Observation preferences C with high utility for answer/tool success."""
        c = np.array([0.15, 0.05, 0.25, 0.02, 0.53], dtype=float)
        return self._normalize(c)

    def _build_D(self) -> Dict[str, np.ndarray]:
        """Prior beliefs D over hidden state factors."""
        return {
            "knowledge_state": self._normalize(np.array([0.7, 0.2, 0.1], dtype=float)),
            "task_stage": self._normalize(np.array([0.72, 0.15, 0.1, 0.03], dtype=float)),
            "tool_effectiveness": self._normalize(np.array([0.2, 0.6, 0.2], dtype=float)),
        }

    def _init_pymdp_agent_if_available(self) -> None:
        """Best-effort pymdp Agent initialization (optional dependency at runtime)."""
        self.pymdp_agent = None
        try:
            from pymdp.agent import Agent  # type: ignore

            self.pymdp_agent = Agent(
                A=[self.A["knowledge_state"], self.A["task_stage"], self.A["tool_effectiveness"]],
                B=[self.B["knowledge_state"], self.B["task_stage"], self.B["tool_effectiveness"]],
                C=[self.C],
                D=[self.D["knowledge_state"], self.D["task_stage"], self.D["tool_effectiveness"]],
            )
        except Exception:
            self.pymdp_agent = None

    def _obs_index(self, observation: str) -> int:
        if observation not in self.space.observations:
            raise ValueError(f"Unknown observation: {observation}")
        return self.space.observations.index(observation)

    def infer_state(self, observation: str) -> Dict[str, Dict[str, float]]:
        """Infer posterior beliefs given a categorical observation."""
        obs_idx = self._obs_index(observation)

        for factor in ["knowledge_state", "task_stage", "tool_effectiveness"]:
            likelihood = self.A[factor][obs_idx, :]
            posterior = self._normalize(likelihood * self.qs[factor])
            self.qs[factor] = posterior

        return self.get_belief_state()

    def update_beliefs(self, observation: str) -> Dict[str, Dict[str, float]]:
        """Alias for infer_state to keep API ergonomic for users."""
        return self.infer_state(observation)

    def _predict_obs_for_action(self, action_idx: int) -> np.ndarray:
        pred_obs = np.zeros(len(self.space.observations), dtype=float)
        for factor in ["knowledge_state", "task_stage", "tool_effectiveness"]:
            pred_state = self.B[factor][:, :, action_idx] @ self.qs[factor]
            pred_obs += self.A[factor] @ pred_state
        pred_obs = self._normalize(pred_obs)
        return pred_obs

    def evaluate_policies(self) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Compute expected free energy per action and softmax policy probabilities."""
        G: Dict[str, float] = {}

        for a_idx, action in enumerate(self.space.actions):
            qo = self._predict_obs_for_action(a_idx)
            risk = -np.sum(qo * np.log(self.C + 1e-9))
            ambiguity = -np.sum(qo * np.log(qo + 1e-9))
            G[action] = float(risk + 0.25 * ambiguity)

        g_vals = np.array([G[a] for a in self.space.actions], dtype=float)
        logits = -g_vals
        probs = np.exp(logits - logits.max())
        probs = self._normalize(probs)
        policy_probs = {a: float(p) for a, p in zip(self.space.actions, probs)}

        self._last_eval = (policy_probs, G)
        return policy_probs, G

    def select_action(self) -> str:
        """Select action minimizing expected free energy."""
        if not self._last_eval[0]:
            self.evaluate_policies()
        _, G = self._last_eval
        selected = min(G, key=G.get)
        self._last_selected_action = selected
        return selected

    def get_belief_state(self) -> Dict[str, Dict[str, float]]:
        """Return beliefs in structured dictionary form."""
        return {
            "knowledge_state": {
                state: float(prob) for state, prob in zip(self.space.knowledge_state, self.qs["knowledge_state"])
            },
            "task_stage": {
                state: float(prob) for state, prob in zip(self.space.task_stage, self.qs["task_stage"])
            },
            "tool_effectiveness": {
                state: float(prob) for state, prob in zip(self.space.tool_effectiveness, self.qs["tool_effectiveness"])
            },
        }

    def step(self, observation: str) -> PlannerSnapshot:
        """Full planner step: update beliefs, evaluate policies, choose action."""
        self.update_beliefs(observation)
        policy_probs, G = self.evaluate_policies()
        action = self.select_action()
        return PlannerSnapshot(
            belief_state=self.get_belief_state(),
            policy_probabilities=policy_probs,
            expected_free_energy=G,
            selected_action=action,
        )


if __name__ == "__main__":
    planner = ActiveInferencePlanner()
    planner.update_beliefs("relevant_doc_found")
    policy_probs, g_vals = planner.evaluate_policies()
    action = planner.select_action()
    print(
        {
            "belief_state": planner.get_belief_state(),
            "policy_probabilities": policy_probs,
            "expected_free_energy": g_vals,
            "selected_action": action,
        }
    )
