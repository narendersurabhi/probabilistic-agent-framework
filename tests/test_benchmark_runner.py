import json
from pathlib import Path

from src.evaluation.benchmark_runner import BenchmarkRunner
from src.evaluation.dataset_loader import DatasetLoader


class DummyAgent:
    def run(self, query: str):
        if "percent" in query:
            return {
                "selected_tool": "call_calculator",
                "arguments": {"expression": "200 * 0.15"},
                "steps": [{"action": "call_calculator", "arguments": {"expression": "200 * 0.15"}}],
            }
        return {
            "selected_tool": "generate_answer",
            "arguments": {"text": "answer"},
            "steps": [{"action": "generate_answer", "arguments": {"text": "answer"}}],
        }


def test_dataset_loader_loads_all() -> None:
    datasets = DatasetLoader().load_all()
    assert "tool_benchmark" in datasets
    assert "delayed_reward_tasks" in datasets
    assert len(datasets["tool_benchmark"]) > 0


def test_benchmark_runner_executes_and_writes_artifacts(tmp_path: Path) -> None:
    dataset_dir = tmp_path / "datasets"
    dataset_dir.mkdir(parents=True)

    (dataset_dir / "tool_benchmark.json").write_text(
        json.dumps(
            [
                {
                    "task_id": "benchmark_001",
                    "query": "What is 15 percent of 200?",
                    "expected_tool": "call_calculator",
                    "expected_args": {"expression": "200 * 0.15"},
                }
            ]
        ),
        encoding="utf-8",
    )
    (dataset_dir / "tool_confusion_tasks.json").write_text(
        json.dumps(
            [
                {
                    "task_id": "confusion_001",
                    "query": "What is the capital of France?",
                    "expected_tool_sequence": ["generate_answer"],
                }
            ]
        ),
        encoding="utf-8",
    )
    for name in ["uncertainty_tasks.json", "argument_accuracy_tasks.json", "delayed_reward_tasks.json"]:
        (dataset_dir / name).write_text("[]", encoding="utf-8")

    runner = BenchmarkRunner(dataset_dir=dataset_dir, results_dir=tmp_path / "results")
    runner._build_agent = lambda agent_name: DummyAgent()  # type: ignore[assignment]

    results = runner.run(agent_filter=["standard"])

    assert "standard" in results
    assert (tmp_path / "results" / "benchmark_results.json").exists()
    assert (tmp_path / "results" / "plots" / "tool_accuracy_comparison.png").exists()
    trace_files = list((tmp_path / "results" / "traces").glob("*.json"))
    assert trace_files
    graph_files = list((tmp_path / "results" / "graphs").glob("*_graph.json"))
    assert graph_files


def test_active_inference_trace_contains_planner_state(tmp_path: Path) -> None:
    dataset_dir = tmp_path / "datasets"
    dataset_dir.mkdir(parents=True)

    (dataset_dir / "tool_benchmark.json").write_text(
        json.dumps(
            [
                {
                    "task_id": "benchmark_001",
                    "query": "What is 15 percent of the population of France?",
                    "expected_tool_sequence": ["retrieve_docs", "call_calculator"],
                }
            ]
        ),
        encoding="utf-8",
    )
    for name in ["tool_confusion_tasks.json", "uncertainty_tasks.json", "argument_accuracy_tasks.json", "delayed_reward_tasks.json"]:
        (dataset_dir / name).write_text("[]", encoding="utf-8")

    runner = BenchmarkRunner(dataset_dir=dataset_dir, results_dir=tmp_path / "results")
    runner.run(agent_filter=["active_inference"])

    trace_file = tmp_path / "results" / "traces" / "active_inference__benchmark_001.json"
    trace_payload = json.loads(trace_file.read_text(encoding="utf-8"))
    first_step = trace_payload["steps"][0]

    assert "belief_state" in first_step
    assert "policy_probabilities" in first_step
    assert "expected_free_energy" in first_step
