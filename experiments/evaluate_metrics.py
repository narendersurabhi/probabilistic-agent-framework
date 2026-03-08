"""Generate evaluation report JSON from benchmark results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    metrics = json.loads(Path(args.input).read_text(encoding="utf-8"))
    report = {
        agent: {
            "tool_selection_accuracy": vals.get("tool_accuracy", 0.0),
            "argument_accuracy": vals.get("argument_accuracy", 0.0),
            "task_completion_rate": vals.get("task_completion", 0.0),
            "belief_entropy_reduction": vals.get("belief_entropy_reduction", 0.0),
        }
        for agent, vals in metrics.items()
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
