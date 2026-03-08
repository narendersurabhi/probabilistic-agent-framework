"""FastAPI server for interactive Active Inference dashboard."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from src.evaluation.agent_comparison import AgentComparisonRunner
from src.evaluation.benchmark_runner import BenchmarkRunner

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agents.critic_agent import CriticAgent
from agents.learner_agent import LearnerAgent
from agents.planner_agent import PlannerAgent
from api.trace_api import router as trace_router
from environment.tool_environment import ToolEnvironment
from llm.mock_llm import MockLLM
from llm.observation_parser import ObservationParser
from models.pomdp_model import build_default_model
from visualization.belief_plots import plot_belief_entropy
from visualization.policy_plots import plot_expected_free_energy, plot_policy_probabilities


class TaskRequest(BaseModel):
    query: str


class ComparisonRequest(BaseModel):
    task_id: str = "task_001"
    query: str


app = FastAPI(title="Active Inference Dashboard API", version="0.2.0")
app.include_router(trace_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = Path(__file__).resolve().parent.parent
UI_DIR = ROOT / "ui"
RESULTS_DIR = ROOT / "results"
TRACE_DIR = ROOT / "traces"
TRACE_DIR.mkdir(parents=True, exist_ok=True)

model = build_default_model()
planner = PlannerAgent(model=model)
critic = CriticAgent()
learner = LearnerAgent(model=model)
environment = ToolEnvironment()
parser = ObservationParser()
llm = MockLLM()

AGENT_STEPS: List[Dict[str, Any]] = []
LAST_QUERY: str = ""
LAST_RUN_ID: str = ""
CURRENT_OBS: Dict[str, bool] = {"tool_success": True}
CURRENT_KNOWLEDGE_BELIEF: Dict[str, float] = {"unknown": 0.7, "partial": 0.2, "confident": 0.1}


class StreamManager:
    """Tracks active websocket clients for real-time trace broadcasting."""

    def __init__(self) -> None:
        self.clients: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.clients.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.clients:
            self.clients.remove(websocket)

    async def broadcast(self, event: Dict[str, Any]) -> None:
        stale_clients: List[WebSocket] = []
        for client in self.clients:
            try:
                await client.send_json(event)
            except Exception:
                stale_clients.append(client)
        for client in stale_clients:
            self.disconnect(client)


stream_manager = StreamManager()


def _args_for_action(action: str, query: str) -> Dict[str, str]:
    if action == "retrieve_docs":
        return {"query": query}
    if action == "call_calculator":
        _, args = llm.choose_tool(query)
        if "expression" in args:
            return args
        return {"expression": "2 * 10"}
    if action == "ask_user":
        return {"clarification_question": "Could you clarify your intent?"}
    return {"draft": "Based on retrieved information, here is an answer."}


def _update_knowledge_belief(observation: Dict[str, bool]) -> Dict[str, float]:
    global CURRENT_KNOWLEDGE_BELIEF
    unknown = CURRENT_KNOWLEDGE_BELIEF["unknown"]
    partial = CURRENT_KNOWLEDGE_BELIEF["partial"]
    confident = CURRENT_KNOWLEDGE_BELIEF["confident"]

    if observation.get("relevant_doc_found"):
        unknown -= 0.15
        partial += 0.1
        confident += 0.05
    if observation.get("tool_success"):
        unknown -= 0.1
        partial += 0.05
        confident += 0.05
    if observation.get("answer_generated"):
        unknown -= 0.1
        partial -= 0.05
        confident += 0.15
    if observation.get("tool_failure"):
        unknown += 0.1
        partial -= 0.05
        confident -= 0.05

    vec = np.clip(np.array([unknown, partial, confident], dtype=float), 1e-3, 1.0)
    vec /= vec.sum()
    CURRENT_KNOWLEDGE_BELIEF = {"unknown": float(vec[0]), "partial": float(vec[1]), "confident": float(vec[2])}
    return CURRENT_KNOWLEDGE_BELIEF


def _new_run_id() -> str:
    return f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"


def _add_node(nodes: List[Dict[str, Any]], edges: List[Dict[str, str]], node_type: str, label: str, data: Dict[str, Any], previous_id: str | None) -> str:
    node_id = f"node_{len(nodes) + 1}"
    nodes.append({"id": node_id, "type": node_type, "label": label, "data": data})
    if previous_id:
        edges.append({"source": previous_id, "target": node_id})
    return node_id


def _build_trace(run_id: str, query: str, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, str]] = []

    previous = _add_node(nodes, edges, "query", "User Query", {"query": query, "run_id": run_id}, None)

    for step in steps:
        previous = _add_node(nodes, edges, "belief_update", f"Belief Update (Step {step['step']})", step["belief_state"], previous)
        previous = _add_node(nodes, edges, "policy_eval", f"Policy Evaluation (Step {step['step']})", {
            "policy_probabilities": step["policy_probabilities"],
            "expected_free_energy": step["expected_free_energy"],
        }, previous)
        previous = _add_node(nodes, edges, "action_selection", f"Action Selection (Step {step['step']})", {"action": step["action"]}, previous)
        previous = _add_node(nodes, edges, "tool_execution", f"Tool Execution (Step {step['step']})", step["tool_execution"], previous)
        previous = _add_node(nodes, edges, "observation", f"Observation Parsing (Step {step['step']})", step["observation"], previous)
        previous = _add_node(nodes, edges, "critic", f"Critic Evaluation (Step {step['step']})", step["critic"], previous)

    return {"run_id": run_id, "nodes": nodes, "edges": edges}


@app.get("/")
def root() -> FileResponse:
    return FileResponse(UI_DIR / "index.html")


@app.get("/trace_viewer")
def trace_viewer() -> FileResponse:
    return FileResponse(UI_DIR / "trace_viewer.html")


@app.get("/agent_comparison")
def agent_comparison_view() -> FileResponse:
    return FileResponse(UI_DIR / "agent_comparison.html")


app.mount("/ui", StaticFiles(directory=str(UI_DIR)), name="ui")


@app.post("/run_task")
async def run_task(req: TaskRequest) -> Dict[str, Any]:
    global AGENT_STEPS, LAST_QUERY, CURRENT_OBS, LAST_RUN_ID
    AGENT_STEPS = []
    LAST_QUERY = req.query
    CURRENT_OBS = {"tool_success": True}
    LAST_RUN_ID = _new_run_id()

    await stream_manager.broadcast({"event": "task_started", "task_id": LAST_RUN_ID, "query": req.query})

    entropies: List[float] = []
    for i in range(1, 6):
        plan = planner.step(CURRENT_OBS)
        action = plan.selected_action
        arguments = _args_for_action(action, req.query)
        tool_output = environment.execute(action, arguments)
        observation = parser.parse(tool_output)
        eval_result = critic.evaluate(expected_tool=action, selected_tool=action, arguments=arguments, expected_args=arguments, observation=observation)
        learner.update(action, observation)
        knowledge_belief = _update_knowledge_belief(observation)

        belief_vec = np.array(list(plan.belief_state.values()), dtype=float)
        entropies.append(float(-(belief_vec * np.log(belief_vec + 1e-9)).sum()))

        step_event = {
            "event": "agent_step",
            "task_id": LAST_RUN_ID,
            "query": req.query,
            "step": i,
            "belief_state": {
                "task_stage": plan.belief_state,
                "knowledge_state": knowledge_belief,
            },
            "action": action,
            "policy_probabilities": plan.policy_probabilities,
            "expected_free_energy": plan.expected_free_energy,
            "tool_execution": {
                "tool": tool_output.tool,
                "arguments": arguments,
                "success": tool_output.success,
                "result": tool_output.result,
                "metadata": tool_output.metadata,
            },
            "observation": observation,
            "critic": eval_result,
        }
        AGENT_STEPS.append(step_event)
        await stream_manager.broadcast(step_event)
        CURRENT_OBS = observation
        if observation.get("answer_generated"):
            break

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    plot_belief_entropy(entropies, str(RESULTS_DIR / "plots" / "dashboard_belief_entropy.png"))
    if AGENT_STEPS:
        plot_policy_probabilities(AGENT_STEPS[-1]["policy_probabilities"], str(RESULTS_DIR / "plots" / "dashboard_policy_probs.png"))
        plot_expected_free_energy(AGENT_STEPS[-1]["expected_free_energy"], str(RESULTS_DIR / "plots" / "dashboard_efe.png"))

    trace_payload = _build_trace(LAST_RUN_ID, req.query, AGENT_STEPS)
    (TRACE_DIR / f"{LAST_RUN_ID}.json").write_text(json.dumps(trace_payload, indent=2), encoding="utf-8")

    await stream_manager.broadcast({"event": "task_completed", "task_id": LAST_RUN_ID, "steps": len(AGENT_STEPS)})

    return {"query": req.query, "run_id": LAST_RUN_ID, "steps": AGENT_STEPS}


@app.get("/agent_steps")
def get_agent_steps() -> List[Dict[str, Any]]:
    return AGENT_STEPS


@app.get("/belief_state")
def get_belief_state() -> Dict[str, Any]:
    task_stage = AGENT_STEPS[-1]["belief_state"]["task_stage"] if AGENT_STEPS else planner.select_action().belief_state
    return {
        "knowledge_state": CURRENT_KNOWLEDGE_BELIEF,
        "task_stage": task_stage,
        "last_run_id": LAST_RUN_ID,
    }


@app.get("/benchmark_results")
def get_benchmark_results() -> Dict[str, Any]:
    path = RESULTS_DIR / "benchmark_results.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


@app.post("/compare_agents")
def compare_agents(req: ComparisonRequest) -> Dict[str, Any]:
    runner = AgentComparisonRunner(results_dir=RESULTS_DIR)
    return runner.compare_task({"task_id": req.task_id, "query": req.query})


@app.post("/run_benchmark")
async def run_benchmark() -> Dict[str, Any]:
    runner = BenchmarkRunner(results_dir=RESULTS_DIR)

    def emit(event: Dict[str, Any]) -> None:
        import asyncio

        asyncio.create_task(stream_manager.broadcast(event))

    results = runner.run(event_callback=emit)
    await stream_manager.broadcast({"event": "benchmark_completed", "results": results})
    return results


@app.websocket("/stream")
async def stream_trace(websocket: WebSocket) -> None:
    await stream_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        stream_manager.disconnect(websocket)
