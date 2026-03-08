"""Generate benchmark visualization artifacts from benchmark result JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from visualization.belief_plots import plot_benchmark_bars


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    metrics = json.loads(Path(args.input).read_text(encoding="utf-8"))
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)
    plot_benchmark_bars(metrics, args.out_dir)


if __name__ == "__main__":
    main()
