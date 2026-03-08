from agent_arena import Arena, list_datasets, load_dataset


class DummyAgent:
    name = "Dummy"

    def run(self, query: str):
        return {"selected_tool": "generate_answer", "arguments": {"text": query}}


def test_public_dataset_helpers() -> None:
    datasets = list_datasets()
    assert "tool_benchmark" in datasets
    payload = load_dataset("tool_confusion")
    assert isinstance(payload, list)
    assert payload


def test_arena_custom_agents_mode() -> None:
    arena = Arena(agents=[DummyAgent()], dataset="tool_benchmark")
    results = arena.run(max_tasks=3)
    assert "leaderboard" in results
    assert results["leaderboard"][0]["agent"] == "Dummy"
    assert results["leaderboard"][0]["tasks"] == 3
