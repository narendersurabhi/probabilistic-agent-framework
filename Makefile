.PHONY: benchmark test rag-eval sync sync-rag demo report full-eval

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

demo:
	uv run python experiments/run_agent_arena.py

report:
	uv run python experiments/generate_report.py --input artifacts/benchmark_results.json --output artifacts/benchmark_report.md

full-eval: sync
	uv run python experiments/generate_dataset.py --count 50 --output src/evaluation/datasets/synthetic_tasks.json
	$(MAKE) benchmark
	$(MAKE) report
	$(MAKE) rag-eval
