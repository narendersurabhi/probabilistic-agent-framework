.PHONY: benchmark test rag-eval

benchmark:
	python experiments/run_benchmark.py --config config/benchmark_config.yaml --output-dir artifacts

test:
	pytest -q

rag-eval:
	python rag_eval/experiments/run_rag_eval.py
