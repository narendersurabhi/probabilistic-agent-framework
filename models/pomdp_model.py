"""POMDP model configuration and matrix builders."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np

from models.state_space import ACTIONS, HIDDEN_STATES, OBSERVATIONS


@dataclass
class POMDPModel:
    """Container for POMDP matrices."""

    A: np.ndarray
    B: np.ndarray
    C: np.ndarray
    D: np.ndarray


def _normalize(vec: np.ndarray) -> np.ndarray:
    vec = vec.astype(float)
    total = vec.sum()
    return vec / total if total > 0 else np.ones_like(vec) / len(vec)


def build_default_model() -> POMDPModel:
    """Build deterministic-ish defaults from readable semantics."""
    n_obs = len(OBSERVATIONS)
    n_states = len(HIDDEN_STATES["task_stage"])
    n_actions = len(ACTIONS)

    A = np.full((n_obs, n_states), 0.05)
    # map task_stage -> likely observation
    A[0, 1] = 0.7  # relevant_doc_found when retrieving
    A[2, 2] = 0.7  # tool_success when solving
    A[4, 3] = 0.8  # answer_generated when complete
    A[3, 0] = 0.6  # tool_failure when start
    A = np.apply_along_axis(_normalize, 0, A)

    B = np.zeros((n_states, n_states, n_actions))
    for a_idx, action in enumerate(ACTIONS):
        trans = np.eye(n_states) * 0.65
        if action == "retrieve_docs":
            trans[1, 0] += 0.3
            trans[2, 1] += 0.15
        elif action == "call_calculator":
            trans[2, 1] += 0.3
            trans[3, 2] += 0.15
        elif action == "generate_answer":
            trans[3, 2] += 0.35
        else:  # ask_user
            trans[1, 0] += 0.2
        B[:, :, a_idx] = np.apply_along_axis(_normalize, 0, trans)

    C = _normalize(np.array([0.1, 0.05, 0.25, 0.05, 0.55]))
    D = _normalize(np.array([0.7, 0.2, 0.08, 0.02]))

    return POMDPModel(A=A, B=B, C=C, D=D)


def model_from_config(config: Dict[str, List[float]]) -> POMDPModel:
    """Build model from flat config dictionary for extensibility."""
    default = build_default_model()
    A = np.array(config.get("A", default.A.flatten())).reshape(default.A.shape)
    B = np.array(config.get("B", default.B.flatten())).reshape(default.B.shape)
    C = _normalize(np.array(config.get("C", default.C)))
    D = _normalize(np.array(config.get("D", default.D)))
    return POMDPModel(A=A, B=B, C=C, D=D)
