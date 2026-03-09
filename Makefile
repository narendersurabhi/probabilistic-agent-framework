.PHONY: benchmark test rag-eval sync sync-rag

sync:
	uv sync --all-packages --group dev

sync-rag:
	uv sync --package agent-arena-rag-eval

benchmark:
	uv run python experiments/run_benchmark.py --config config/benchmark_config.yaml --output-dir artifacts

test:
	uv run pytest -q

rag-eval:
	uv run --package agent-arena-rag-eval python rag_eval/experiments/run_rag_eval.py
