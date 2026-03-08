# Repository Agent Notes and Change Log

All agents operating in this repository should read this file first to understand current status, architecture, and recent modifications.

## Current Status

- Initialized full Python 3.11 repository for a self-improving multi-agent Active Inference framework.
- Added benchmark suite comparing Standard LLM, ReAct, and Active Inference agents.
- Added deterministic mock environment, evaluation harness, metrics, plots, and tests.

## Change Log

## 2026-03-08
- Created repository scaffold:
  - `agents/`, `models/`, `tools/`, `environment/`, `llm/`, `evaluation/`, `logging/`, `experiments/`, `visualization/`, `benchmarks/`, `config/`, `results/`, `tests/`.
- Implemented POMDP model and matrix builders in `models/pomdp_model.py` and hidden state definitions in `models/state_space.py`.
- Implemented tool schema validation and tools (`calculator`, `retriever`) under `tools/`.
- Implemented deterministic tool environment in `environment/tool_environment.py`.
- Implemented mock LLM and observation parser in `llm/`.
- Implemented planner, critic, and learner agents in `agents/`.
- Implemented JSONL logger in `logging/run_logger.py`.
- Implemented evaluation metrics and benchmark runner in `evaluation/`.
- Added benchmark agent variants in `benchmarks/`.
- Added experiment scripts:
  - `experiments/run_agent.py`
  - `experiments/run_benchmark.py`
- Added visualization utilities in `visualization/belief_plots.py`.
- Added benchmark config in `config/benchmark_config.yaml`.
- Added datasets in `evaluation/datasets/`.
- Added pytest coverage for tools, agents, and evaluation.
- Added top-level `README.md` and `requirements.txt`.

## Notes for Next Agents

- Keep this file updated whenever files or behavior change.
- Benchmark outputs are deterministic by seeded runs.
- `pymdp` is optional at runtime; planner has a deterministic fallback policy scorer.
- Validation status:
  - `pytest -q` attempted but dependency installation is blocked by environment proxy/network restrictions.
  - `python -m compileall -q .` passes for syntax validation.

## 2026-03-08 (follow-up improvements)
- Implemented trace-aware benchmarking to evaluate full tool sequences instead of only first tool call:
  - Added sequence metrics (`sequence_tool_accuracy`, `prefix_accuracy`, `final_answer_accuracy`) in `evaluation/metrics.py`.
  - Reworked `evaluation/benchmark_runner.py` to score exact sequence match, prefix ratio, and per-task-type summaries.
- Standardized benchmark agent outputs to include `trace` payloads for all architectures:
  - Updated `benchmarks/standard_agent.py`, `benchmarks/react_agent.py`, and `benchmarks/active_inference_agent.py`.
- Updated benchmark dataset schema with `task_type` and explicit `expected_tools` sequences in `evaluation/datasets/benchmark_tasks.json`.
- Updated benchmark experiment report generation to include sequence-aware and per-task-type metrics in `experiments/run_benchmark.py`.
- Expanded tests for trace outputs and sequence-aware metrics in `tests/test_agents.py` and `tests/test_evaluation.py`.
- Updated `README.md` benchmark section to document trace-aware evaluation.

## 2026-03-08 (dashboard extension)
- Added lightweight real-time dashboard architecture:
  - Backend API in `api/server.py` using FastAPI.
  - Frontend in `ui/index.html`, `ui/dashboard.js`, `ui/styles.css`.
- Implemented dashboard endpoints:
  - `POST /run_task`
  - `GET /agent_steps`
  - `GET /belief_state`
  - `GET /benchmark_results`
- Added real-time polling (500ms) and visual panels for timeline, belief state, policy probabilities, expected free energy, tool execution, and benchmark results.
- Added plotting utilities in `visualization/policy_plots.py` for policy probability and expected free energy charts.
- Updated README with an Interactive Agent Visualization section and local run instructions (`uvicorn api.server:app --reload`).
- Added `uvicorn` dependency to `requirements.txt`.
- Added API smoke test in `tests/test_api.py`.

## 2026-03-08 (graph-based trace viewer)
- Added graph trace API router in `api/trace_api.py` with endpoint `GET /trace/{run_id}`.
- Extended `api/server.py` to:
  - generate per-run trace graphs with nodes/edges for query, belief updates, policy evaluation, action selection, tool execution, observation parsing, and critic evaluation.
  - persist trace JSON files in `traces/` using run IDs.
  - return `run_id` from `POST /run_task` and expose `last_run_id` via `GET /belief_state`.
  - serve trace viewer route at `/trace_viewer`.
- Added trace viewer frontend:
  - `ui/trace_viewer.html`
  - `ui/trace_graph.js` (D3-based directed graph rendering, zoom/pan, click-to-inspect metadata).
- Updated dashboard index with link to trace viewer.
- Added `traces/.gitkeep` to persist trace directory in repository.
- Extended API tests to validate trace retrieval endpoint and trace structure.
- Updated README with new "Agent Trace Visualization" section and usage instructions.

## 2026-03-08 (kubernetes + argo experiment pipeline)
- Added reproducible experiment pipeline infrastructure:
  - Argo workflow definition at `infra/argo/benchmark_workflow.yaml`
  - Docker experiment runner at `infra/docker/Dockerfile`
  - GitHub Actions workflow at `.github/workflows/benchmark.yml`
- Extended benchmark configuration in `config/benchmark_config.yaml` with:
  - `number_of_runs`
  - `agent_types`
- Extended `evaluation/benchmark_runner.py` to support configurable `agent_types` and repeated runs with mean aggregation.
- Updated `experiments/run_benchmark.py` to support `--config` + `--output-dir` and emit:
  - `benchmark_results.json`
  - `evaluation_report.json`
  - plots
  - `benchmark_report.md`
- Added pipeline helper scripts:
  - `experiments/evaluate_metrics.py`
  - `experiments/generate_visualizations.py`
  - `experiments/generate_report.py`
- Added `artifacts/.gitkeep` for artifact output directory tracking.
- Updated README with a new "Experiment Pipeline" section including Argo usage, local commands, and pipeline diagram.
