"""Reasoning-trace graph builders for benchmark artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json


def _format_compact(value: Any) -> str:
    if isinstance(value, dict):
        pairs = [f"{k}={v}" for k, v in value.items()]
        return ", ".join(pairs)
    return str(value)


def build_reasoning_graph(trace: Dict[str, Any]) -> Dict[str, List[Any]]:
    """Build a directed reasoning graph from a trace payload."""
    nodes: List[Dict[str, Any]] = []
    edges: List[List[str]] = []

    query_text = trace.get("query", "User Query")
    nodes.append({"id": "query", "label": f"Query: {query_text}", "type": "query"})
    previous = "query"

    for index, step in enumerate(trace.get("steps", []), start=1):
        belief_state = step.get("belief_state")
        belief_label = "Belief update"
        if belief_state:
            knowledge = belief_state.get("knowledge_state", belief_state)
            belief_label = f"Belief: {_format_compact(knowledge)}"

        belief_node = f"belief_{index}"
        action_node = f"action_{index}"
        obs_node = f"obs_{index}"

        nodes.append({"id": belief_node, "label": belief_label, "type": "belief"})
        nodes.append({"id": action_node, "label": f"Action: {step.get('action', 'unknown')}", "type": "action"})

        observation = step.get("observation")
        if observation is None:
            observation = step.get("arguments", {})
        nodes.append({"id": obs_node, "label": f"Observation: {_format_compact(observation)}", "type": "observation"})

        edges.append([previous, belief_node])
        edges.append([belief_node, action_node])
        edges.append([action_node, obs_node])
        previous = obs_node

    result = trace.get("result", {})
    result_node = "result"
    result_label = "Final: completed" if result.get("tool_correct") else "Final: incomplete"
    nodes.append({"id": result_node, "label": result_label, "type": "result"})
    edges.append([previous, result_node])

    return {"nodes": nodes, "edges": edges}


def save_reasoning_graph(graph: Dict[str, List[Any]], path: str | Path) -> Path:
    """Persist graph JSON to disk."""
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    return out_path
