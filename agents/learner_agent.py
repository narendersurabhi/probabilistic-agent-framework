"""Learner agent updating preference/transition parameters."""

from __future__ import annotations

from typing import Dict

import numpy as np

from models.pomdp_model import POMDPModel
from models.state_space import ACTIONS, OBSERVATIONS


class LearnerAgent:
    def __init__(self, model: POMDPModel, lr: float = 0.05) -> None:
        self.model = model
        self.lr = lr

    def update(self, action: str, observation: Dict[str, bool]) -> None:
        success = observation.get("tool_success", False)
        obs_idx = OBSERVATIONS.index("tool_success" if success else "tool_failure")
        delta = self.lr if success else -self.lr
        self.model.C[obs_idx] = max(1e-3, self.model.C[obs_idx] + delta)
        self.model.C = self.model.C / self.model.C.sum()

        action_idx = ACTIONS.index(action)
        boost = 0.02 if success else -0.02
        self.model.B[:, :, action_idx] = np.clip(self.model.B[:, :, action_idx] + np.eye(self.model.B.shape[0]) * boost, 1e-3, 1.0)
        self.model.B[:, :, action_idx] = self.model.B[:, :, action_idx] / self.model.B[:, :, action_idx].sum(axis=0, keepdims=True)
