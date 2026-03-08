.PHONY: benchmark test

benchmark:
	python experiments/run_benchmark.py --config config/benchmark_config.yaml --output-dir artifacts

test:
	pytest -q
