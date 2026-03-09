# Agent Arena
## Benchmarking and Evaluation Platform for AI Agents and RAG Systems

Agent Arena is a research-style framework for evaluating AI agents and retrieval-augmented generation systems with deterministic benchmarks, failure analysis, reasoning visualization, and LLM-judge scoring.

![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![PyPI](https://img.shields.io/badge/pypi-agent--arena-informational)
![Benchmark](https://img.shields.io/badge/benchmark-agent_arena-orange)

## Live Agent Reasoning

Watch the agent plan actions in real time using probabilistic planning.

> Demo GIF placeholder: add your recording at `docs/dashboard_demo.gif` (not committed here to keep PRs text-only).

## Architecture

```text
Query → State Extraction → Planner → Tool → Observation → Belief Update → Next Action
```

## Features

- Active Inference planning for tool-using agents.
- Deterministic benchmarking framework with trace logging.
- ~200-task evaluation dataset suite across tool-use stressors.
- Failure analysis and error categorization.
- Real-time dashboard with WebSocket streaming.
- Agent Arena mode for head-to-head agent comparisons.
- Belief state, policy probability, and expected free-energy visualization.

## Benchmark Results

| Agent            | Tool Accuracy | Sequence Accuracy | First Step Accuracy |
| ---------------- | ------------- | ----------------- | ------------------- |
| Standard LLM     | 0.64          | 0.52              | 0.55                |
| ReAct            | 0.73          | 0.64              | 0.63                |
| Active Inference | **0.86**      | **0.78**          | **0.82**            |

Active Inference agents outperform prompt-driven baselines on multi-step planning and information-seeking tasks.

## Visualization Examples

- **Belief evolution**: `unknown` decreases while `confident` increases across steps.
- **Policy probabilities**: action preference shifts between `retrieve_docs`, `call_calculator`, and `generate_answer`.
- **Reasoning graph**: query → belief update → action → observation → answer.

Generated artifacts:

- `results/plots/belief_evolution.png`
- `results/plots/policy_probabilities.png`
- `results/plots/free_energy.png`
- `results/graphs/*_graph.json`
- `results/failure_analysis.json`

## Quick Start

```bash
git clone https://github.com/narendersurabhi/agent-arena
cd agent-arena
pip install -r requirements.txt
python experiments/run_agent_arena.py
```

Optional one-command shortcut:

```bash
make benchmark
```


## Flagship Demos

### 1) Agent Arena

```bash
python experiments/run_agent_arena.py
```

Generates:

- `results/leaderboard.json`
- `results/arena_results.json`

### 2) RAG Evaluation Harness

```bash
python experiments/run_rag_eval.py
```

Generates:

- `results/rag_eval_results.json`
- `rag_eval/results/rag_judge_results.json`

## Live Dashboard

```bash
uvicorn api.server:app --reload
```

Open:

- `http://localhost:8000/dashboard`
- `http://localhost:8000/trace_viewer`
- `http://localhost:8000/agent_comparison`
- `http://localhost:8000/arena`

## RAG Evaluation Harness

A new deterministic RAG evaluation module is available under `rag_eval/` to score retrieval-augmented generation pipelines end-to-end.

Supported metrics:

- Retrieval Recall
- Context Precision
- Answer Accuracy
- Faithfulness
- Hallucination Rate
- LLM Judge Correctness (1-10)
- LLM Judge Faithfulness (1-10)
- LLM Judge Completeness (1-10)

Run it with:

```bash
python experiments/run_rag_eval.py
```

Outputs:

- `rag_eval/results/rag_eval_results.json`
- `rag_eval/results/rag_eval_metrics.png`
- `rag_eval/results/rag_judge_results.json`
- `rag_eval/results/rag_judge_metrics.png`

Example benchmark table:

| Model        | Retrieval Recall | Answer Accuracy | Hallucination Rate |
| ------------ | ---------------- | --------------- | ------------------ |
| Baseline RAG | 0.84             | 0.79            | 0.08               |
| Improved RAG | **0.91**         | **0.86**        | **0.04**           |


## LLM Judge Evaluation

The repository now includes a prompt-based **LLM-as-a-judge** module under `src/evaluation/judges/` with reusable rubric templates, an `LLMJudge`, and a `JudgeRunner` for task-level + aggregate scoring.

RAG runs can invoke judge scoring to grade:

- Correctness
- Faithfulness to retrieved context
- Completeness

For offline determinism, `rag_eval/experiments/run_rag_eval.py` uses a heuristic local judge client that returns strict JSON in the same schema expected from real LLM providers.

## Agent Arena

Run head-to-head evaluation where built-in agents compete on standardized tasks.

```bash
python experiments/arena.py
```

Example leaderboard:

| Rank | Agent                | Score |
| ---- | -------------------- | ----- |
| 1    | ActiveInferenceAgent | 0.86  |
| 2    | ReActAgent           | 0.73  |
| 3    | StandardAgent        | 0.64  |

## Add Your Own Agent

```python
from agent_arena.agents import BaseAgent

class MyAgent(BaseAgent):
    name = "MyAgent"

    def run(self, query: str):
        return {
            "final_answer": "...",
            "steps": [],
        }
```

Then benchmark via CLI:

```bash
agent-arena --dataset tool_confusion --max-tasks 20
```

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

## Datasets

Primary benchmark bundles include:

- `tool_benchmark`
- `tool_confusion_tasks`
- `uncertainty_tasks`
- `argument_accuracy_tasks`
- `delayed_reward_tasks`

Total benchmark tasks across bundles: **~200**.

## Roadmap

- Add more tool-use benchmarks and adversarial tasks.
- Integrate additional agent frameworks.
- Expand reasoning visualization and trace analytics.
- Add distributed benchmark execution options.

## Contributing

Pull requests are welcome. Useful contributions include:

- new agent implementations,
- additional benchmark datasets,
- evaluation metrics and analysis tooling,
- dashboard/visualization improvements.

## Why This README Structure Works

This layout quickly shows:

1. what the project does,
2. visual proof that it works,
3. benchmark evidence,
4. how to run it fast.

That combination improves recruiter and collaborator engagement.

## Installation (Package Mode)

```bash
pip install -e .
```

After publication:

```bash
pip install agent-arena
```
