# Self-Improving Multi-Agent LLM Framework with Active Inference (POMDP)

A production-style Python 3.11 repository demonstrating a probabilistic multi-agent system with:

- **Planner Agent** (Active Inference / POMDP planning)
- **Critic Agent** (tool/argument/progress evaluation)
- **Learner Agent** (preference and transition updates)

It also includes a **benchmark suite** comparing:

1. Standard LLM Tool Agent
2. ReAct Agent
3. Active Inference Agent

The benchmark is now **trace-aware**: it evaluates full tool sequences (not just first tool call).

## System Overview

Agent loop:

`User Query -> State Extraction -> Planner -> Tool Execution -> Observation Parsing -> Critic -> Logging -> Learner Update -> Next Step`

Hidden states:

- `knowledge_state`: unknown, partial, confident
- `task_stage`: start, retrieving, solving, complete
- `tool_effectiveness`: low, medium, high

Observations:

- `relevant_doc_found`
- `doc_not_relevant`
- `tool_success`
- `tool_failure`
- `answer_generated`

Actions (tools):

- `retrieve_docs`
- `call_calculator`
- `ask_user`
- `generate_answer`

## Architecture (text diagram)

```text
+--------------------+
| User Query         |
+---------+----------+
          |
          v
+--------------------+      +----------------------+
| Planner Agent      | ---> | Tool Environment     |
| (Active Inference) |      | + validated tools     |
+---------+----------+      +----------+-----------+
          |                            |
          v                            v
+--------------------+      +----------------------+
| Observation Parser | ---> | Critic Agent         |
+---------+----------+      +----------+-----------+
          |                            |
          +------------+   +-----------+
                       v   v
                 +----------------------+
                 | Learner Agent        |
                 | (policy updates)     |
                 +----------+-----------+
                            |
                            v
                    JSONL Run Logger
```

## Active Inference Explanation

The planner maintains a belief distribution over hidden states. At each step it:

- predicts outcomes under each candidate action,
- computes expected free energy (heuristic + preference fit),
- samples/selects low-EFE policies,
- emits policy probabilities and chosen action.

The learner then adjusts preference matrix `C` and transition matrix `B` using critic + tool outcome signals, enabling self-improvement over episodes.

## Example Run

```bash
python experiments/run_agent.py
```

Outputs:

- step-wise structured JSON
- run logs at `logs/agent_runs.jsonl`
- belief plots in `results/plots/`

## Evaluation & Benchmark

Run benchmark:

```bash
python experiments/run_benchmark.py
```

Artifacts:

- `results/benchmark_results.json`
- `results/benchmark_report.md`
- plots in `results/plots/`

### Benchmark Results (example)

| Agent | Tool Accuracy | Sequence Accuracy | Prefix Accuracy | Argument Accuracy | Completion Rate | Avg Steps |
|---|---:|---:|---:|---:|---:|---:|
| Standard LLM | 0.65 | 0.52 | 0.61 | 0.62 | 0.50 | 1.00 |
| ReAct | 0.74 | 0.63 | 0.72 | 0.71 | 0.62 | 1.40 |
| Active Inference | 0.86 | 0.78 | 0.84 | 0.81 | 0.76 | 1.20 |

Why Active Inference helps:

- explicit uncertainty tracking and entropy reduction,
- preference-guided policy optimization,
- iterative updates from critic feedback,
- improved multi-step sequence performance under trace-aware scoring.


## Interactive Agent Visualization

A lightweight dashboard is included with:

- **FastAPI backend**: `api/server.py`
- **Vanilla frontend**: `ui/index.html`, `ui/dashboard.js`, `ui/styles.css`

### Features

- Submit tasks via `/run_task`
- Observe step-by-step agent decisions from `/agent_steps`
- Inspect belief distributions from `/belief_state`
- View benchmark metrics from `/benchmark_results`
- Real-time UI polling every 500ms

### Run the dashboard

```bash
uvicorn api.server:app --reload
```

Then open:

```text
http://localhost:8000
```

### How to interpret the dashboard

- **Belief State** panel shows task-stage and knowledge-state distributions evolving over time.
- **Policy Probabilities** shows action selection likelihoods at the latest step.
- **Expected Free Energy** shows per-action objective values (lower is preferred).
- **Tool Execution** shows validated tool calls and outputs.
- **Benchmark Comparison** shows architecture-level performance metrics.

### Example screenshot

See `results/plots/dashboard_screenshot.png` after running the UI capture flow.


## Agent Trace Visualization

Each dashboard run now generates a graph-structured trace file in `traces/`:

- Node types: `query`, `belief_update`, `policy_eval`, `action_selection`, `tool_execution`, `observation`, `critic`
- Directed edges represent the execution chain across agent steps
- Trace API endpoint: `GET /trace/{run_id}`

Open the graph viewer at:

```text
http://localhost:8000/trace_viewer
```

The trace viewer uses **D3.js** for:

- force-directed graph rendering,
- zoom and pan interactions,
- click-to-inspect metadata panel.

### Trace screenshot

See `results/plots/trace_viewer_screenshot.png` for an example graph visualization.


## Experiment Pipeline

A reproducible, production-style experiment pipeline is included for local and Kubernetes execution.

### Pipeline stages

1. **Benchmark Execution**: run all configured agent architectures and write `benchmark_results.json`
2. **Evaluation**: compute summary metrics and write `evaluation_report.json`
3. **Visualization**: generate matplotlib comparison plots in `artifacts/plots/`
4. **Report Generation**: create `benchmark_report.md`

### Pipeline architecture (text diagram)

```text
User triggers experiment
  -> Argo workflow starts
  -> benchmark step runs
  -> evaluation step computes metrics
  -> visualization step generates plots
  -> report step produces benchmark report
```

### Kubernetes + Argo

- Workflow file: `infra/argo/benchmark_workflow.yaml`
- Container definition: `infra/docker/Dockerfile`

Submit on cluster:

```bash
argo submit infra/argo/benchmark_workflow.yaml
```

### Local execution

```bash
python experiments/run_benchmark.py --config config/benchmark_config.yaml --output-dir artifacts
python experiments/evaluate_metrics.py --input artifacts/benchmark_results.json --output artifacts/evaluation_report.json
python experiments/generate_visualizations.py --input artifacts/benchmark_results.json --out-dir artifacts/plots
python experiments/generate_report.py --input artifacts/benchmark_results.json --output artifacts/benchmark_report.md
```

### CI integration

GitHub Actions workflow: `.github/workflows/benchmark.yml`

It builds the experiment image, runs the benchmark pipeline locally, and uploads the generated `artifacts/` directory.

## Testing

```bash
pytest -q
```

## Future Work

- replace mock LLM with production LLM adapters,
- add richer tool APIs and external retrieval backends,
- learn observation and transition models online,
- support distributed multi-agent execution.
