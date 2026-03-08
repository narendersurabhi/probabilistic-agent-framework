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

## 2026-03-08 (standalone pymdp active inference planner module)
- Added new planning module at `src/planning/active_inference_planner.py` implementing:
  - hidden-state factors (`knowledge_state`, `task_stage`, `tool_effectiveness`)
  - observation model `A`, transition model `B`, preference vector `C`, prior beliefs `D`
  - belief inference (`infer_state` / `update_beliefs`)
  - policy evaluation via expected free energy (`evaluate_policies`)
  - action selection (`select_action`) and structured step output (`PlannerSnapshot`)
  - optional `pymdp` Agent initialization when available.
- Added `src/planning/__init__.py` package marker.
- Added tests in `tests/test_planner.py` covering belief update behavior, policy probability validity, and valid action selection.

## 2026-03-08 (100-task tool-selection benchmark dataset)
- Added new dataset `evaluation/datasets/agent_tool_benchmark.json` with 100 tasks for tool-selection evaluation.
- Dataset distribution:
  - 30 arithmetic tasks (`expected_tool: calculator`, `expected_args.expression`)
  - 30 retrieval tasks (`expected_tool: retriever`, `expected_args.query`)
  - 20 multi-step tasks (`expected_tool: retriever` plus `expected_tools` and `expected_args_sequence` for retriever->calculator chains)
  - 20 direct-answer tasks (`expected_tool: generate_answer`, `expected_args.text`)
- Validated dataset length, required schema fields, and category distribution via local Python checks.

## 2026-03-08 (tool confusion robustness benchmark dataset)
- Added `evaluation/datasets/tool_confusion_benchmark.json` with 50 tasks focused on tool-selection robustness under confusion scenarios.
- Dataset includes required fields:
  - `task_id`
  - `task_type`
  - `query`
  - `expected_tool_sequence`
- Distribution implemented:
  - 15 `false_calculator` tasks (numeric-looking questions that should use `generate_answer`)
  - 10 `hidden_calculator` tasks (informational-looking prompts that require `call_calculator`)
  - 15 `retrieve_then_compute` tasks (two-step `retrieve_docs -> call_calculator`)
  - 10 `misleading_retrieval` tasks (retrieval-looking but common-knowledge prompts that should use `generate_answer`)
- Validated task count, category distribution, and schema shape via local Python checks.

## 2026-03-08 (benchmark runner harness hardening)
- Hardened `evaluation/benchmark_runner.py` to act as a true evaluation harness:
  - normalizes heterogeneous agent output shapes (`selected_tool/arguments/steps` and `tool/args/trace`)
  - evaluates tasks using `expected_tool_sequence` when present (in addition to existing expected fields)
  - records task-level execution traces to JSONL via `trace_log_path`
- Updated `experiments/run_benchmark.py` to emit `benchmark_traces.jsonl` along with benchmark metrics/reports/plots.
- Added `Makefile` with `make benchmark` and `make test` convenience targets.
- Added evaluation test coverage for result normalization path in `tests/test_evaluation.py`.
- Updated README benchmark usage and artifact list to include `make benchmark` and benchmark trace logs.

## 2026-03-08 (expanded benchmark dataset suite)
- Added five new benchmark dataset bundles in `evaluation/datasets/` aligned to research-style tool-use evaluation prompts:
  - `tool_benchmark.json` (100-task mixed benchmark: arithmetic/retrieval/multi-step/direct-answer)
  - `tool_confusion_tasks.json` (50-task confusion robustness benchmark)
  - `uncertainty_tasks.json` (40-task uncertainty-seeking / information-first benchmark)
  - `argument_accuracy_tasks.json` (40-task tool-argument correctness benchmark)
  - `multi_step_tasks.json` (40-task multi-step planning benchmark)
- Added dataset integrity tests in `tests/test_evaluation.py` to validate dataset presence, expected sizes, and `tool_benchmark.json` task-type distribution.
- Updated `README.md` with a new "Dataset Bundles" section documenting the new dataset files and intended use.

## 2026-03-08 (deterministic benchmark tooling under src/)
- Added explicit deterministic benchmark modules under `src/` for CI/offline evaluation:
  - `src/environment/tool_environment.py` with `execute(tool_name, args)` dispatcher for `call_calculator`, `retrieve_docs`, and `generate_answer`.
  - `src/tools/calculator_tool.py` deterministic expression evaluator.
  - `src/tools/retrieval_tool.py` static knowledge-base retriever.
  - `src/llm/mock_llm.py` mock provider-driven state extraction (`LLM_PROVIDER` defaults to `fake`).
  - `src/llm/observation_parser.py` deterministic tool-output to observation label mapping.
- Added package markers and exports for new `src/environment`, `src/tools`, and `src/llm` modules.
- Strengthened top-level deterministic retriever (`tools/retriever.py`) to use a static knowledge base and explicit success/failure behavior on unmatched queries.
- Expanded tool tests in `tests/test_tools.py` to cover deterministic retriever failure, new `src` tool environment outputs, and observation parser mapping.

## 2026-03-08 (uncertainty-planning metric extension)
- Added explicit `first_step_accuracy` metric in `evaluation/metrics.py` to measure whether agents choose the correct initial action on information-seeking tasks.
- Extended `evaluation/benchmark_runner.py` to record `first_step_correct` per task, aggregate `first_step_accuracy` across runs, and include per-task-type first-step summaries.
- Updated benchmark reporting in `experiments/run_benchmark.py` to include first-step columns in markdown and JSON evaluation reports.
- Expanded `tests/test_evaluation.py` to validate first-step metric calculations and benchmark output fields.
- Updated `README.md` benchmark table and narrative to highlight first-step accuracy as a planning-sensitive metric for uncertainty tasks.

## 2026-03-08 (delayed-reward planning benchmark extension)
- Added new delayed-reward dataset `evaluation/datasets/delayed_reward_tasks.json` with 40 long-horizon tasks:
  - all tasks include `expected_tool_sequence` with at least 3 steps.
  - includes 3-step and 4-step retrieval-plus-calculation planning trajectories.
- Extended `evaluation/metrics.py` with planning-focused metrics:
  - `planning_accuracy`
  - `average_planning_depth`
  - `premature_action_rate`
- Extended `evaluation/benchmark_runner.py` to emit delayed-reward metrics at global and per-task-type levels.
- Updated benchmark reporting in `experiments/run_benchmark.py` to include planning depth and premature action rate in markdown/JSON outputs.
- Expanded evaluation tests in `tests/test_evaluation.py` to validate:
  - delayed-reward dataset presence and schema expectations
  - new planning metric behavior
  - benchmark runner output fields for new metrics
- Updated `README.md` benchmark and dataset sections to document delayed-reward tasks and planning-centric metrics.

## 2026-03-08 (master benchmark dataset suite under src/)
- Added a new benchmark dataset bundle in `src/evaluation/datasets/` for prompt-driven suite generation with ~200 tasks total:
  - `tool_benchmark.json` (60 tasks; `task_id`, `task_type`, `query`, `expected_tool`, `expected_args`)
  - `tool_confusion_tasks.json` (40 tasks; `task_id`, `task_type`, `query`, `expected_tool_sequence`)
  - `uncertainty_tasks.json` (40 tasks; `task_id`, `query`, `expected_tool_sequence`)
  - `argument_accuracy_tasks.json` (30 tasks; `task_id`, `query`, `expected_tool`, `expected_args`)
  - `delayed_reward_tasks.json` (30 tasks; `task_id`, `query`, `expected_tool_sequence`)
- Ensured task ID naming follows requested prefixes (`benchmark_*`, `confusion_*`, `uncertainty_*`, `args_*`, `delayed_*`).
- Used tool names `retrieve_docs`, `call_calculator`, and `generate_answer` with country/city population and world-fact prompts.

## 2026-03-08 (src evaluation harness + one-command benchmark pipeline refresh)
- Added `src/evaluation` package modules for a full benchmark/evaluation harness aligned to the tool-use architecture comparison workflow:
  - `src/evaluation/dataset_loader.py` for loading all dataset bundles in `src/evaluation/datasets/`.
  - `src/evaluation/metrics.py` with benchmark metrics: `tool_selection_accuracy`, `argument_accuracy`, `sequence_accuracy`, `first_step_accuracy`, and `task_completion_rate`.
  - `src/evaluation/trace_logger.py` for structured per-task trace persistence under `results/traces/`.
  - `src/evaluation/benchmark_runner.py` introducing `BenchmarkRunner` to run agents, normalize outputs, score tasks, write traces/results, and generate comparison plots in `results/plots/`.
  - `src/evaluation/__init__.py` export for `BenchmarkRunner`.
- Reworked benchmark scripts to match a one-command evaluation flow:
  - Updated `experiments/run_benchmark.py` to run `BenchmarkRunner`, support optional `--agent` filters (`standard`, `react`, `active_inference`), save artifacts, and trigger markdown report generation.
  - Updated `experiments/generate_report.py` to build `results/benchmark_report.md` with summary tables and embedded plot image links.
- Added test coverage for the new harness:
  - `tests/test_metrics.py` validating metric calculations and aggregate output keys.
  - `tests/test_benchmark_runner.py` validating dataset loader behavior and benchmark execution/artifact generation with a deterministic dummy agent.
- Refined `src/evaluation/benchmark_runner.py` to include lightweight deterministic in-module benchmark agent implementations (`StandardAgent`, `ReActAgent`, `ActiveInferenceAgent`) built on `src/environment/tool_environment.py` so `python experiments/run_benchmark.py` works without importing heavier optional benchmark stack dependencies.
- Added resilient plotting behavior: if `matplotlib` is unavailable in an execution environment, plot artifacts are still produced as placeholder files while preserving benchmark pipeline outputs.

## 2026-03-08 (active-inference trace dynamics plots)
- Extended `src/evaluation/benchmark_runner.py` Active Inference execution steps to include per-step planner snapshots with:
  - `belief_state.knowledge_state` probabilities (`unknown`, `partial`, `confident`)
  - `policy_probabilities` over `retrieve_docs`, `call_calculator`, `generate_answer`
  - `expected_free_energy` values per action
- Extended trace creation in `src/evaluation/benchmark_runner.py` so benchmark trace files persist the planner-state fields for each step.
- Added new trace-visualization package under `src/visualization/`:
  - `belief_plots.py` with `plot_belief_evolution(trace, out_path=...)`
  - `policy_plots.py` with `plot_policy_probabilities(trace, out_path=...)`
  - `free_energy_plot.py` with `plot_expected_free_energy(trace, out_path=...)`
  - `__init__.py` exports for all three plotting helpers.
- Updated `experiments/run_benchmark.py` to auto-load an Active Inference trace and generate:
  - `results/plots/belief_evolution.png`
  - `results/plots/policy_probabilities.png`
  - `results/plots/free_energy.png`
- Added tests:
  - `tests/test_visualization.py` validates all three trace plotting helpers write output files.
  - `tests/test_benchmark_runner.py` validates Active Inference traces include belief, policy-probability, and expected-free-energy fields.
- Updated `README.md` benchmark artifacts and documentation with an "Active Inference Trace Dynamics Visualization" section.

## 2026-03-08 (reasoning trace graph artifacts for benchmark runs)
- Added `src/visualization/trace_graph.py` with:
  - `build_reasoning_graph(trace)` to convert benchmark traces into node/edge graph JSON.
  - `save_reasoning_graph(graph, path)` to persist graph artifacts.
- Extended `src/visualization/__init__.py` exports to include reasoning-graph helpers.
- Extended `src/evaluation/benchmark_runner.py` to:
  - include per-step tool `observation` values in agent steps and persisted traces,
  - generate a reasoning graph for every task trace,
  - save graph artifacts under `results/graphs/` as `{agent}__{task_id}_graph.json`.
- Added graph output directory tracking with `results/graphs/.gitkeep`.
- Added tests:
  - `tests/test_trace_graph.py` for graph construction and file persistence.
  - updated `tests/test_benchmark_runner.py` to assert graph artifact generation.
- Updated `README.md` benchmark artifacts/docs with a new "Reasoning Trace Graphs" section and `results/graphs/` output details.
