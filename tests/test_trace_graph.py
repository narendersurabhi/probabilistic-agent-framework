import json

from src.visualization.trace_graph import build_reasoning_graph, save_reasoning_graph


def test_build_reasoning_graph_contains_expected_chain() -> None:
    trace = {
        "query": "What is 20 percent of the population of Spain?",
        "steps": [
            {
                "step": 1,
                "action": "retrieve_docs",
                "arguments": {"query": "population of Spain"},
                "observation": {"result": "Population of Spain is approximately 47 million."},
                "belief_state": {"knowledge_state": {"unknown": 0.7, "partial": 0.2, "confident": 0.1}},
            },
            {
                "step": 2,
                "action": "call_calculator",
                "arguments": {"expression": "47000000 * 0.2"},
                "observation": {"result": 9400000},
                "belief_state": {"knowledge_state": {"unknown": 0.2, "partial": 0.3, "confident": 0.5}},
            },
        ],
        "result": {"tool_correct": True},
    }

    graph = build_reasoning_graph(trace)

    ids = {node["id"] for node in graph["nodes"]}
    assert "query" in ids
    assert "belief_1" in ids
    assert "action_1" in ids
    assert "obs_1" in ids
    assert "result" in ids
    assert ["query", "belief_1"] in graph["edges"]
    assert ["action_2", "obs_2"] in graph["edges"]


def test_save_reasoning_graph_writes_json(tmp_path) -> None:
    graph = {"nodes": [{"id": "query", "label": "Query", "type": "query"}], "edges": []}
    out = save_reasoning_graph(graph, tmp_path / "graphs" / "run_001_graph.json")
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["nodes"][0]["id"] == "query"
