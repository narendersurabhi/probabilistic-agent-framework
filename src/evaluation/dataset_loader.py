"""Dataset loading utilities for benchmark tasks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

DATASET_FILENAMES = {
    "tool_benchmark": "tool_benchmark.json",
    "tool_confusion_tasks": "tool_confusion_tasks.json",
    "uncertainty_tasks": "uncertainty_tasks.json",
    "argument_accuracy_tasks": "argument_accuracy_tasks.json",
    "delayed_reward_tasks": "delayed_reward_tasks.json",
}


class DatasetLoader:
    """Loads benchmark datasets from a dataset directory."""

    def __init__(self, dataset_dir: str | Path = "src/evaluation/datasets") -> None:
        self.dataset_dir = Path(dataset_dir)

    def load_dataset(self, dataset_name: str) -> List[Dict]:
        filename = DATASET_FILENAMES.get(dataset_name, dataset_name)
        path = self.dataset_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError(f"Dataset must be a list: {path}")
        return payload

    def load_all(self) -> Dict[str, List[Dict]]:
        return {name: self.load_dataset(name) for name in DATASET_FILENAMES}
