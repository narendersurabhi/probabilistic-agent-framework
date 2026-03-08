import json
from pathlib import Path

from src.evaluation.agent_comparison import AgentComparisonRunner


def test_agent_comparison_runner_writes_artifact(tmp_path: Path) -> None:
    runner = AgentComparisonRunner(results_dir=tmp_path)
    payload = runner.compare_task(
        {
            "task_id": "task_001",
            "query": "What is 20 percent of the population of Spain?",
        }
    )

    assert payload["task_id"] == "task_001"
    assert "standard_agent" in payload
    assert "react_agent" in payload
    assert "active_inference_agent" in payload

    artifact_path = Path(payload["artifact_path"])
    assert artifact_path.exists()
    on_disk = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert on_disk["query"] == "What is 20 percent of the population of Spain?"
    assert len(on_disk["active_inference_agent"]["steps"]) >= 1
