# Repository Agent Notes and Change Log

All agents operating in this repository should read this file first to understand current status, architecture, and recent modifications.

## Current Status

- Initialized full Python 3.11 repository for a self-improving multi-agent Active Inference framework.
- Added benchmark suite comparing Standard LLM, ReAct, and Active Inference agents.
- Added deterministic mock environment, evaluation harness, metrics, plots, and tests.

## Change Log

## 2026-03-09 (quickstart troubleshooting clarity)
- Updated `README.md` quickstart docs with a **Troubleshooting setup issues** section covering common local setup failures: `Repository not found` during `git clone` and `No pyproject.toml found` when running `uv` from the wrong directory.
- Added explicit guidance to run setup commands from an existing checkout (do not re-clone if already in repo) and included a corrected `cd /path/to/agent-arena` command sequence.

## 2026-03-09 (failure taxonomy analyzer)
- Added `agent_arena/evaluation/failure_taxonomy.py` with `FailureTaxonomyAnalyzer` for structured failure classification (`tool_selection_error`, `tool_argument_error`, `premature_action`, `missing_step`, `incorrect_sequence`, `reasoning_error`, `hallucination`).
- Updated `src/evaluation/failure_analyzer.py` to delegate to taxonomy analyzer while preserving the existing `FailureAnalyzer` API for runner compatibility.
- Updated `agent_arena/evaluation/__init__.py` exports to include `FailureTaxonomyAnalyzer` and refactored `agent_arena/__init__.py` to lazy-load public exports to avoid circular imports during evaluation module imports.
- Updated `tests/test_failure_analyzer.py` for taxonomy label expectations and added `tests/test_failure_taxonomy.py` to validate reasoning/hallucination classification behavior.
- Updated `README.md` with a new **Failure Taxonomy Analysis** section documenting categories and generated artifacts.

## 2026-03-09 (trace replay system)
- Added replay package `agent_arena/replay/`:
  - `replay_engine.py` with `ReplayEngine` for deterministic step-by-step trace playback, formatted step rendering, and trace summaries.
  - `__init__.py` export for replay interfaces.
- Updated `agent_arena/__init__.py` exports to include `ReplayEngine` in the public package API.
- Added CLI utility `scripts/replay_trace.py` with timed (`--delay`) and interactive (`--interactive`) replay modes.
- Added test coverage in `tests/test_replay.py` for replay output formatting and summary metadata.
- Updated `README.md` with a new **Replay System** subsection and CLI usage example.

## 2026-03-09 (agent observability tracing + metrics)
- Added new observability package `agent_arena/observability/`:
  - `tracer.py` with `AgentTracer` for per-run step logging (`run_id`, step timestamps, latency, errors, final status/result).
  - `metrics.py` with `MetricsCollector` for per-trace metrics and aggregate run metrics.
  - `__init__.py` exports for observability interfaces.
- Integrated observability instrumentation into `src/evaluation/benchmark_runner.py`:
  - wraps each task run with an `AgentTracer`,
  - emits per-step latency and total run latency into persisted traces,
  - attaches computed `observability_metrics` to trace artifacts,
  - stores per-agent observability rollups inside `failure_analysis.json`.
- Updated public package exports in `agent_arena/__init__.py` to include `AgentTracer` and `MetricsCollector`.
- Added `visualization/show_trace.py` CLI utility to print run timelines from saved trace JSON files.
- Added tests in `tests/test_observability.py` and extended `tests/test_benchmark_runner.py` to validate observability fields in generated trace artifacts.
- Updated `README.md` with a dedicated **Agent Observability (Tracing + Metrics)** section and trace viewer usage command.

## 2026-03-09 (developer workflow targets: demo/report/full-eval)
- Updated `Makefile` with additional reproducible DX targets:
  - `make demo` to run the flagship Agent Arena demo command.
  - `make report` to generate markdown benchmark reports from `artifacts/benchmark_results.json`.
  - `make full-eval` to run end-to-end evaluation workflow (`sync`, synthetic dataset generation, benchmark, report, and rag-eval).
- Updated `README.md` quickstart/workflow documentation to include the new one-command shortcuts and an explicit end-to-end `make full-eval` section.

## 2026-03-09 (baseline + trace/info-gain visualization polish)
- Added lightweight baseline agent `agents/react_agent.py` with injectable LLM/tools and prompt-construction flow for quick ReAct-vs-probabilistic comparisons.
- Updated `agents/__init__.py` to export the new top-level `ReActAgent` baseline.
- Added `visualization/trace_graph.py` with `plot_trace(...)` to render step-to-step reasoning trace diagrams.
- Added `visualization/information_gain_plot.py` with `plot_information_gain(...)` for expected information gain bar charts.
- Updated `visualization/__init__.py` exports to include new trace and information-gain plotting helpers.
- Added tests `tests/test_react_baseline.py` and `tests/test_reasoning_visualizations.py` to validate baseline output payloads and plot artifact generation.

## 2026-03-09 (uv workspace package management for arena + rag-eval)
- Updated root `pyproject.toml` to support `uv` workspace usage by:
  - adding `[dependency-groups]` with `dev` dependencies (pytest),
  - adding `[tool.uv.workspace]` members for the root package and `rag_eval` package.
- Added `rag_eval/pyproject.toml` so the RAG evaluation harness is a first-class workspace package (`agent-arena-rag-eval`) installable/runnable via `uv`.
- Updated `Makefile` targets to use `uv run` for benchmark/test/rag-eval flows and added `sync` / `sync-rag` helpers.
- Updated `README.md` with a new **uv Workspace Package Management** section plus `uv`-based quickstart and run commands for both Agent Arena and RAG eval workflows.

## 2026-03-09 (distributed benchmark runner)
- Added `src/evaluation/distributed_runner.py` with a multiprocessing-based `DistributedBenchmarkRunner` that schedules task-agent jobs across worker processes and aggregates benchmark metrics/failure analysis.
- Integrated distributed execution into `experiments/run_benchmark.py` via new `--workers` flag.
- Extended package exports in `src/evaluation/__init__.py` and `agent_arena/benchmark.py` to expose `DistributedBenchmarkRunner`.
- Updated `agent_arena/cli.py` with `--workers` support and distributed benchmark execution path for multi-worker runs.
- Added `tests/test_distributed_runner.py` coverage for distributed execution artifact generation.
- Updated `README.md` with a new **Distributed Benchmark Runner** section and usage examples.

## 2026-03-09 (synthetic dataset generation pipeline)
- Added synthetic data generation package under `agent_arena/data_generation/`:
  - `task_generator.py` with `TaskGenerator` plus deterministic `HeuristicTaskLLM` fallback client.
  - `task_validator.py` with schema/tool validation for generated tasks.
  - `dataset_builder.py` for writing assembled JSON datasets.
  - `__init__.py` exports for data-generation utilities.
- Added executable script `experiments/generate_dataset.py` to generate synthetic tasks (`--count`, `--output`) and write benchmark-ready datasets.
- Generated and added starter synthetic benchmark dataset at `src/evaluation/datasets/synthetic_tasks.json` (20 tasks).
- Updated `src/evaluation/dataset_loader.py` to register `synthetic_tasks` as a first-class dataset bundle.
- Added test coverage in `tests/test_data_generation.py` for generation, validation, builder output, and script end-to-end behavior.
- Updated `README.md` with a new **Synthetic Dataset Generator** section and a flagship demo command for dataset generation.

## 2026-03-08 (LLM judge evaluation module)
- Added prompt-based LLM-as-a-judge framework under `src/evaluation/judges/`:
  - `rubrics.py` with default RAG scoring rubric + prompt builder.
  - `llm_judge.py` with `LLMJudge`, typed `JudgeResult`, and deterministic `HeuristicJudgeClient` fallback for offline runs.
  - `judge_runner.py` for per-task judge execution and aggregate score computation.
  - `__init__.py` exports for judge utilities.
- Updated `src/evaluation/__init__.py` to export `LLMJudge` and `JudgeRunner`.
- Extended `rag_eval/src/rag_eval/evaluator.py` to optionally run judge scoring and emit task/aggregate judge fields (`judge_correctness`, `judge_faithfulness`, `judge_completeness`, `judge_explanation`).
- Updated `rag_eval/experiments/run_rag_eval.py` to:
  - invoke judge scoring by default using deterministic heuristic judge client,
  - write `rag_eval/results/rag_judge_results.json`,
  - generate `rag_eval/results/rag_judge_metrics.png`,
  - print judge summaries in CLI output.
- Added tests in `tests/test_judges.py` for judge evaluation and aggregation.
- Expanded `tests/test_rag_eval.py` to validate judge summary fields and `rag_judge_results.json` artifact generation.
- Updated `README.md` with LLM Judge Evaluation documentation and new RAG output artifacts.

## 2026-03-08 (RAG evaluation harness module)
- Added a standalone deterministic RAG evaluation module under `rag_eval/`:
  - `rag_eval/src/rag_eval/retriever.py` for keyword-overlap retrieval.
  - `rag_eval/src/rag_eval/generator.py` for heuristic answer extraction from retrieved context.
  - `rag_eval/src/rag_eval/metrics.py` implementing retrieval recall, context precision, answer accuracy, faithfulness, and hallucination rate.
  - `rag_eval/src/rag_eval/evaluator.py` with task-level scoring and aggregate metric computation.
  - `rag_eval/src/rag_eval/__init__.py` package exports.
- Added benchmark starter dataset `rag_eval/datasets/qa_dataset.json` with QA tasks, relevant docs, and corpora.
- Added executable experiment script `rag_eval/experiments/run_rag_eval.py`:
  - runs retrieval + generation + evaluation loop,
  - writes `rag_eval/results/rag_eval_results.json`,
  - writes `rag_eval/results/rag_eval_metrics.png` (or placeholder text artifact without matplotlib).
- Added test coverage in `tests/test_rag_eval.py` for metric behavior, pipeline integration, and end-to-end script artifact generation.
- Updated `README.md` with a new **RAG Evaluation Harness** section and run instructions.
- Updated `Makefile` with `make rag-eval` convenience target.

## 2026-03-08 (README GitHub page positioning refresh)
- Reworked `README.md` to a high-impact GitHub landing layout focused on immediate project comprehension and adoption.
- Updated top section branding to **Agent Arena** with subtitle, one-line positioning statement, and professional badges (Python, MIT, PyPI, Benchmark).
- Added dedicated sections for: live demo GIF placement, architecture flow, key features, benchmark results, visualization artifacts, quick start, dashboard routes, Agent Arena leaderboard, custom agent extension, example trace, datasets, roadmap, and contribution guidance.
- Aligned the README narrative to emphasize AI research/platform value (deterministic evaluation + active-inference planning + observability tooling).

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

## 2026-03-08 (websocket real-time dashboard streaming)
- Extended dashboard backend in `api/server.py` with websocket streaming endpoint `GET /stream` and broadcast manager for live events.
- Updated `POST /run_task` to emit `task_started`, per-step `agent_step`, and `task_completed` stream events.
- Added `POST /run_benchmark` in `api/server.py` to execute `src.evaluation.BenchmarkRunner` and stream benchmark-step events live.
- Extended `src/evaluation/benchmark_runner.py` with optional `event_callback` support so each task step can be emitted to the dashboard as `benchmark_step` events.
- Upgraded dashboard frontend (`ui/index.html`, `ui/dashboard.js`) to consume websocket events in real time, including:
  - live belief and policy charts (Chart.js),
  - action history,
  - incremental reasoning graph JSON,
  - benchmark stream trigger button.
- Updated `README.md` dashboard documentation to include websocket streaming and benchmark streaming capabilities.
- Expanded tests:
  - `tests/test_api.py` now validates websocket stream emission for task execution.
  - `tests/test_benchmark_runner.py` now validates benchmark event callback emission.

## 2026-03-08 (README portfolio and recruiter-facing refresh)
- Reworked `README.md` into a recruiter-friendly, portfolio-style format optimized for fast scanning (<30s value comprehension).
- Updated top-level README structure to include:
  - title + subtitle aligned to "Probabilistic Agent Framework"
  - one-line project description
  - demo section guidance
  - architecture overview flow
  - repository structure snapshot
  - key feature highlights
  - benchmark results table
  - visualization artifact callouts
  - quick start and dashboard run flow
  - dataset bundle summary and example trace
  - interview demo flow and recruiter-signal framing
  - advanced next-step recommendation for side-by-side planning strategy comparison.

## 2026-03-08 (side-by-side agent reasoning comparison)
- Added side-by-side comparison harness at `src/evaluation/agent_comparison.py`:
  - runs Standard, ReAct, and Active Inference agents on the same task query,
  - normalizes step traces,
  - writes JSON artifacts under `results/comparisons/{task_id}.json`.
- Updated `src/evaluation/__init__.py` exports to include `AgentComparisonRunner`.
- Added comparison experiment script `experiments/compare_agents.py` with CLI flags:
  - `--task-id`
  - `--query`
  - `--output-dir`
- Extended API server (`api/server.py`) with:
  - `POST /compare_agents` to run and return side-by-side comparison payloads,
  - `GET /agent_comparison` route serving a dedicated UI page.
- Added comparison UI pages/components:
  - `ui/agent_comparison.html`
  - `ui/agent_comparison.js`
  - dashboard integration in `ui/index.html` + `ui/dashboard.js` with an in-dashboard Agent Comparison panel.
- Added test coverage:
  - `tests/test_agent_comparison.py` for artifact generation and payload schema.
  - extended `tests/test_api.py` to validate `POST /compare_agents`.
- Updated `README.md` with a new **Agent Reasoning Comparison** section documenting CLI usage, UI routes, and expected behavioral differences.

## 2026-03-08 (automatic failure analysis in benchmark + dashboard)
- Added `src/evaluation/failure_analyzer.py` with deterministic failure classification labels:
  - `wrong_tool`
  - `incorrect_arguments`
  - `premature_action`
  - `incomplete_plan`
  - `incorrect_sequence`
- Extended `src/evaluation/benchmark_runner.py` to:
  - classify each task outcome with `FailureAnalyzer`,
  - aggregate per-agent and overall failure counts,
  - persist `results/failure_analysis.json`,
  - add `failure_rate` to benchmark metrics,
  - include failure labels in benchmark step stream events,
  - generate `results/plots/failure_distribution.png`.
- Extended `experiments/generate_report.py` to include failure-analysis sections in markdown reports and include failure distribution plot links.
- Updated exports in `src/evaluation/__init__.py` to include `FailureAnalyzer`.
- Extended dashboard/backend failure visibility:
  - added `GET /failure_analysis` in `api/server.py`,
  - added a "Failure Analysis" panel in `ui/index.html`,
  - updated `ui/dashboard.js` to fetch and render failure analysis results.
- Added/updated tests:
  - `tests/test_failure_analyzer.py` for failure category classification,
  - `tests/test_benchmark_runner.py` now verifies `failure_analysis.json` artifact creation,
  - `tests/test_api.py` now validates `/failure_analysis` endpoint availability.
- Updated `README.md` with a new "Failure Analysis" section and artifact list additions.

## 2026-03-08 (Agent Arena head-to-head competition)
- Added pluggable arena agent interface under `src/agents/`:
  - `src/agents/base_agent.py` (`BaseAgent` contract with `run(query)`)
  - `src/agents/builtin_agents.py` (built-in plugins: `StandardArenaAgent`, `ReActArenaAgent`, `ActiveInferenceArenaAgent`)
  - `src/agents/__init__.py` exports.
- Added `src/evaluation/arena.py` implementing `AgentArena` with:
  - automatic plugin discovery from `src/agents/`
  - per-task head-to-head execution and winner selection
  - leaderboard and battle-log artifact generation.
- Added CLI runner `experiments/arena.py` to execute the arena and print sample battle + leaderboard output.
- Extended API/UI for arena mode:
  - `api/server.py`: `GET /arena`, `GET /arena_results`, `POST /run_arena`
  - `ui/arena.html`: dedicated arena leaderboard page
  - `ui/index.html` + `ui/dashboard.js`: dashboard button/panel integration for Agent Arena.
- Added tests:
  - `tests/test_arena.py` for arena artifact/leaderboard generation
  - updated `tests/test_api.py` to validate arena endpoints.
- Updated `README.md` with a new **Agent Arena** section covering usage, artifacts, plugin extension model, and API/UI routes.

## 2026-03-08 (pip-installable package surface)
- Added packaging metadata and distribution entry points:
  - `pyproject.toml` with project name `agent-arena`, runtime dependencies, setuptools build backend, and CLI script `agent-arena`.
  - `LICENSE` (MIT).
- Added new public package namespace `agent_arena/` to provide installable library ergonomics while preserving existing internal `src/` modules.
- Implemented stable public API exports:
  - `agent_arena/__init__.py` exports `Arena`, `BenchmarkRunner`, and dataset helper functions.
  - `agent_arena/benchmark.py` exports benchmark runner.
  - `agent_arena/datasets.py` adds dataset listing/loading helpers plus friendly aliases (e.g., `tool_confusion`).
- Added user-facing arena wrapper `agent_arena/arena.py`:
  - supports custom-agent mode (`agents=[...]`) with per-task scoring,
  - supports built-in mode delegating to internal `AgentArena` when no custom agents are provided.
- Added CLI entrypoint `agent_arena/cli.py` supporting:
  - `--dataset`
  - `--max-tasks`
  - prints leaderboard-friendly output.
- Added compatibility subpackage exports for requested package layout:
  - `agent_arena/agents/`, `planning/`, `evaluation/`, `visualization/`, `tools/`, `environment/`.
- Updated `README.md` with package install and quick-usage sections:
  - editable install (`pip install -e .`),
  - PyPI install command (`pip install agent-arena`),
  - import example (`from agent_arena import Arena`),
  - CLI example (`agent-arena --dataset ...`).

## 2026-03-09 (portfolio packaging polish: two flagship demos)
- Added flagship demo script `experiments/run_agent_arena.py` to present head-to-head Agent Arena output in a portfolio-friendly format and highlight `results/leaderboard.json`.
- Added flagship demo script `experiments/run_rag_eval.py` as a top-level RAG evaluation entrypoint that delegates to `rag_eval/experiments/run_rag_eval.py`, prints key summary metrics, and copies canonical output to `results/rag_eval_results.json`.
- Extended API routes in `api/server.py` with:
  - `GET /dashboard` (dashboard alias route)
  - `GET /rag_eval` (RAG evaluation info page route)
- Added UI pages:
  - `ui/dashboard.html` redirect page for dashboard route compatibility
  - `ui/rag_eval.html` with RAG eval run command and artifact references
- Updated `README.md` positioning/subtitle and demo commands to emphasize a unified platform for both Agent Arena and RAG evaluation, including new flagship demos and `/dashboard` entry URL.

## 2026-03-09 (follow-up: PR tooling compatibility for binary assets)
- Removed committed binary demo asset `docs/dashboard_demo.gif` because PR creation tooling rejects binary file payloads.
- Updated `README.md` demo section to reference a local GIF placeholder workflow instead of embedding a tracked binary.
- Added `docs/dashboard_demo_placeholder.md` with instructions for adding the GIF locally/out-of-band when publishing.

## 2026-03-09 (README positioning upgrade: hiring-manager clarity)
- Updated `README.md` with a new **Why Probabilistic Planning Matters** section to explicitly frame the project's research and platform value beyond prompt-only agent heuristics.
- Added a **Reproducible Baseline Comparison** subsection in `README.md` with a one-command benchmark rerun (`uv run python experiments/run_benchmark.py`) and direct pointers to the primary comparison artifacts under `results/`.
- Added a text-based **Planning Loop Visualization** diagram in `README.md` to make belief updates, policy evaluation, and action-selection flow immediately legible to reviewers.
