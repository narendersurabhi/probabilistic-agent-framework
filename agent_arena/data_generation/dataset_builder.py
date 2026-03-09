"""Dataset assembly helpers for synthetic benchmark tasks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


class DatasetBuilder:
    """Build and persist synthetic datasets."""

    def build(self, tasks: List[Dict[str, Any]], output_path: str | Path) -> Path:
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(tasks, indent=2), encoding="utf-8")
        return out_path
