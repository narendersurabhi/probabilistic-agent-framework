from pathlib import Path

from src.evaluation.arena import AgentArena


def test_arena_generates_leaderboard_and_artifacts(tmp_path: Path) -> None:
    arena = AgentArena(results_dir=tmp_path)
    payload = arena.run(max_tasks=5)

    assert payload["total_tasks"] == 5
    assert payload["leaderboard"]
    assert (tmp_path / "leaderboard.json").exists()
    assert (tmp_path / "arena_results.json").exists()
