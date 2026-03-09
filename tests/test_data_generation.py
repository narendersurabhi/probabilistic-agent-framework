import json
import subprocess
import sys

from agent_arena.data_generation import DatasetBuilder, HeuristicTaskLLM, TaskGenerator, TaskValidator


def test_task_generation_and_validation() -> None:
    generator = TaskGenerator(llm=HeuristicTaskLLM())
    validator = TaskValidator()

    task = generator.generate_task()

    assert validator.validate(task)
    assert set(task.keys()) >= {"task_id", "query", "expected_tool_sequence"}


def test_dataset_builder_writes_file(tmp_path) -> None:
    out_path = tmp_path / "synthetic_tasks.json"
    builder = DatasetBuilder()
    tasks = [{"task_id": "synthetic_001", "query": "What is 2+2?", "expected_tool_sequence": ["call_calculator"]}]

    built = builder.build(tasks, out_path)

    assert built.exists()
    payload = json.loads(built.read_text(encoding="utf-8"))
    assert payload == tasks


def test_generate_dataset_script(tmp_path) -> None:
    out_path = tmp_path / "generated.json"

    result = subprocess.run(
        [sys.executable, "experiments/generate_dataset.py", "--count", "5", "--output", str(out_path)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Wrote 5 tasks" in result.stdout
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert len(payload) == 5
    assert payload[0]["task_id"] == "synthetic_001"
