"""CLI utility for replaying a trace artifact step-by-step."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent_arena.replay import ReplayEngine


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay an agent run trace JSON file.")
    parser.add_argument("trace_path", help="Path to trace JSON file (example: results/traces/run_001.json).")
    parser.add_argument("--delay", type=float, default=0.0, help="Seconds to wait between replayed steps.")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Pause for ENTER between steps instead of automatic delay playback.",
    )
    args = parser.parse_args()

    engine = ReplayEngine(args.trace_path)
    engine.replay(delay=args.delay, interactive=args.interactive)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
