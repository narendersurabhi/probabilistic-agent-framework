import json

from agent_arena.replay import ReplayEngine


def test_replay_engine_formats_messages_and_summary(tmp_path, capsys):
    trace = {
        "run_id": "run_014",
        "query": "What is 20% of Spain's population?",
        "status": "success",
        "steps": [
            {"step": 1, "action": "retrieve_docs", "observation": "population_of_spain=47M"},
            {"step": 2, "action": "call_calculator", "result": "9.4M"},
        ],
    }
    path = tmp_path / "run_014.json"
    path.write_text(json.dumps(trace), encoding="utf-8")

    engine = ReplayEngine(path)
    messages = engine.replay(delay=0.0)

    assert len(messages) == 2
    assert "Observation: population_of_spain=47M" in messages[0]
    assert "Result: 9.4M" in messages[1]

    output = capsys.readouterr().out
    assert "Run ID: run_014" in output
    assert "Status: success" in output

    summary = engine.summary()
    assert summary["steps"] == 2
    assert summary["run_id"] == "run_014"
