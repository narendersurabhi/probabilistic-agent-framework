"""Active inference planner agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np

from models.pomdp_model import POMDPModel, build_default_model
from models.state_space import ACTIONS, HIDDEN_STATES, OBSERVATIONS

try:
    import pymdp  # noqa: F401

    HAS_PYMDP = True
except Exception:  # noqa: BLE001
    HAS_PYMDP = False


@dataclass
class PlannerOutput:
    selected_action: str
    policy_probabilities: Dict[str, float]
    expected_free_energy: Dict[str, float]
    belief_state: Dict[str, float]


class PlannerAgent:
    def __init__(self, model: POMDPModel | None = None, seed: int = 7) -> None:
        self.model = model or build_default_model()
        self.rng = np.random.default_rng(seed)
        self.belief = self.model.D.copy()

    def infer_hidden_state(self, observation_flags: Dict[str, bool]) -> np.ndarray:
        obs_idx = OBSERVATIONS.index("tool_success" if observation_flags.get("tool_success") else "tool_failure")
        likelihood = self.model.A[obs_idx, :]
        posterior = likelihood * self.belief
        posterior = posterior / posterior.sum() if posterior.sum() else self.belief
        self.belief = posterior
        return self.belief

    def _efe_for_action(self, action_idx: int) -> float:
        predicted_state = self.model.B[:, :, action_idx] @ self.belief
        predicted_obs = self.model.A @ predicted_state
        risk = -np.sum(predicted_obs * np.log(self.model.C + 1e-9))
        ambiguity = -np.sum(predicted_obs * np.log(predicted_obs + 1e-9))
        return float(risk + 0.25 * ambiguity)

    def select_action(self) -> PlannerOutput:
        efes = np.array([self._efe_for_action(i) for i in range(len(ACTIONS))])
        logits = -efes
        probs = np.exp(logits - logits.max())
        probs /= probs.sum()
        action_idx = int(np.argmax(probs))
        selected = ACTIONS[action_idx]
        belief_dict = {s: float(v) for s, v in zip(HIDDEN_STATES["task_stage"], self.belief)}
        return PlannerOutput(
            selected_action=selected,
            policy_probabilities={a: float(p) for a, p in zip(ACTIONS, probs)},
            expected_free_energy={a: float(e) for a, e in zip(ACTIONS, efes)},
            belief_state=belief_dict,
        )

    def step(self, observation_flags: Dict[str, bool]) -> PlannerOutput:
        self.infer_hidden_state(observation_flags)
        return self.select_action()
