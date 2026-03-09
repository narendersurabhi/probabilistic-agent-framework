import json
from pathlib import Path

from src.evaluation.distributed_runner import DistributedBenchmarkRunner


def test_distributed_runner_executes_and_writes_outputs(tmp_path: Path) -> None:
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
    for name in [
        "tool_confusion_tasks.json",
        "uncertainty_tasks.json",
        "argument_accuracy_tasks.json",
        "delayed_reward_tasks.json",
        "synthetic_tasks.json",
    ]:
        (dataset_dir / name).write_text("[]", encoding="utf-8")

    runner = DistributedBenchmarkRunner(dataset_dir=dataset_dir, results_dir=tmp_path / "results", workers=2)
    results = runner.run(agent_filter=["standard"])

    assert "standard" in results
    assert (tmp_path / "results" / "benchmark_results.json").exists()
    assert (tmp_path / "results" / "failure_analysis.json").exists()
    assert list((tmp_path / "results" / "traces").glob("*.json"))
    assert list((tmp_path / "results" / "graphs").glob("*_graph.json"))
