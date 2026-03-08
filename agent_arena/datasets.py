"""Dataset convenience helpers for users of the public package API."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from src.evaluation.dataset_loader import DATASET_FILENAMES, DatasetLoader

_DATASET_ALIASES = {
    "tool_confusion": "tool_confusion_tasks",
    "uncertainty": "uncertainty_tasks",
    "argument_accuracy": "argument_accuracy_tasks",
    "delayed_reward": "delayed_reward_tasks",
}


def _canonical_name(dataset_name: str) -> str:
    return _DATASET_ALIASES.get(dataset_name, dataset_name)


def list_datasets() -> Dict[str, str]:
    """Return supported named datasets and backing JSON files."""
    return dict(DATASET_FILENAMES)


def load_dataset(dataset_name: str, dataset_dir: str | Path = "src/evaluation/datasets") -> List[Dict[str, Any]]:
    """Load a dataset by canonical name or user-friendly alias."""
    loader = DatasetLoader(dataset_dir=dataset_dir)
    return loader.load_dataset(_canonical_name(dataset_name))
