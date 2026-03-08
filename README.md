# Probabilistic Agent Framework
## Active Inference Planning for Tool-Using LLM Agents

A research-oriented framework for evaluating AI agents that use tools, featuring Active Inference planning, deterministic benchmarks, and real-time reasoning visualization.

## Demo

This repository includes a live dashboard and trace viewer for inspecting agent reasoning in real time:

- belief updates over hidden states,
- policy probabilities and expected free energy,
- tool calls and observations,
- reasoning graph artifacts per run.

> Tip: capture a 10-second GIF from the dashboard (`/`) and trace viewer (`/trace_viewer`) and place it under `results/plots/` for portfolio-ready presentation.

## Architecture Overview

```text
User Query
    ↓
State Extraction
    ↓
Active Inference Planner
    ↓
Tool Execution
    ↓
Observation Parsing
    ↓
Belief Update
    ↓
Next Action
```

## Repository Structure

```text
.
├── README.md
├── Makefile
├── requirements.txt
├── config/
├── src/
│   ├── agents/
│   ├── planning/
│   ├── tools/
│   ├── environment/
│   ├── evaluation/
│   ├── visualization/
│   └── llm/
├── api/
├── ui/
├── experiments/
├── evaluation/datasets/
├── results/
└── tests/
```

This structure highlights framework design, experiment reproducibility, deterministic evaluation, and observability.

## Key Features

- Active Inference planning for tool selection.
- Deterministic benchmarking framework with structured traces.
- Multi-dataset evaluation suite for tool-use behavior.
- Belief state and policy probability visualization.
- Reasoning trace graphs for every benchmark task.
- Real-time dashboard with WebSocket streaming.

## Benchmark Results (Example)

| Agent            | Tool Accuracy | Sequence Accuracy | First Step Accuracy |
|------------------|---------------|-------------------|---------------------|
| Standard LLM     | 0.64          | 0.52              | 0.55                |
| ReAct            | 0.73          | 0.64              | 0.63                |
| Active Inference | **0.86**      | **0.78**          | **0.82**            |

## Visualization Examples

- **Belief evolution**: unknown → partial → confident as evidence accumulates.
- **Policy probabilities**: preference shifts between `retrieve_docs`, `call_calculator`, and `generate_answer`.
- **Reasoning graph**: query → belief update → action → observation → final answer.

Generated artifacts:

- `results/plots/belief_evolution.png`
- `results/plots/policy_probabilities.png`
- `results/plots/free_energy.png`
- `results/graphs/*_graph.json`
- `results/failure_analysis.json`
- `results/plots/failure_distribution.png`

## Quick Start

```bash
git clone https://github.com/narendersurabhi/probabilistic-agent-framework
cd probabilistic-agent-framework
pip install -r requirements.txt
python experiments/run_benchmark.py
```

Or use:

```bash
make benchmark
```

## Run the Dashboard

```bash
uvicorn api.server:app --reload
```

Open:

```text
http://localhost:8000/
```

Trace viewer:

```text
http://localhost:8000/trace_viewer
```


## Agent Reasoning Comparison

Run the same query side-by-side across all three agent architectures:

```bash
python experiments/compare_agents.py --task-id task_001 --query "What is 20 percent of the population of Spain?"
```

This writes a comparison artifact to `results/comparisons/task_001.json` and includes:

- `standard_agent` steps (often greedy single-tool behavior),
- `react_agent` steps (retrieve-then-compute chains),
- `active_inference_agent` steps with belief/policy/expected-free-energy fields.

You can also use the dashboard's **Agent Comparison** panel or open `http://localhost:8000/agent_comparison` for a dedicated side-by-side view.

| Agent            | Typical First Action | Why it matters |
|------------------|----------------------|----------------|
| Standard         | `call_calculator`    | Can fail without missing facts |
| ReAct            | `retrieve_docs`      | Explicit intermediate reasoning |
| Active Inference | `retrieve_docs`      | Probabilistic planning + belief updates |


## Failure Analysis

The benchmark harness now classifies failed tasks automatically into:

- `wrong_tool`
- `incorrect_arguments`
- `premature_action`
- `incomplete_plan`
- `incorrect_sequence`

Per-agent and overall failure summaries are written to `results/failure_analysis.json`, and a failure distribution bar chart is generated at `results/plots/failure_distribution.png`.

Example failure table:

| Failure Type        | Count |
|---------------------|------:|
| wrong_tool          | 19    |
| premature_action    | 16    |
| incorrect_arguments | 12    |
| incorrect_sequence  | 7     |

## Benchmark Datasets

Primary bundles under `evaluation/datasets/` include:

- tool benchmark tasks,
- tool confusion tasks,
- uncertainty / information-seeking tasks,
- argument-accuracy tasks,
- delayed-reward planning tasks.

The `src/evaluation/datasets/` suite provides additional prompt-driven benchmark bundles for deterministic harness execution.

## Example Trace

```text
Query: What is 20 percent of the population of Spain?

Step 1
Action: retrieve_docs

Step 2
Observation: population = 47M

Step 3
Action: call_calculator

Answer: 9.4M
```

## Research Inspiration

- Active Inference
- POMDP planning
- Tool-use architecture comparisons (Standard vs ReAct vs Active Inference)

## Interview Demo Flow

1. Open repository and scan architecture + benchmark sections.
2. Run benchmark and show `results/benchmark_results.json`.
3. Launch dashboard and stream a task live.
4. Open reasoning graph artifact in trace viewer.
5. Walk through `src/planning/active_inference_planner.py`.

## What This Signals

This project demonstrates:

- agent architecture and probabilistic decision loops,
- ML evaluation methodology with deterministic datasets,
- reproducible experiment pipeline design,
- system observability via logs, traces, and dashboards,
- full-stack AI tooling (backend API + frontend visualization).

## Advanced Extension (Recommended Next)

Add side-by-side planning strategy comparison for the same task:

- ReAct trace vs Active Inference trace,
- aligned step timelines,
- comparative tool choices and outcomes.

This makes architectural trade-offs immediately visible to reviewers.

## Testing

```bash
pytest -q
```
