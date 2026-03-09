import json

from agent_arena.observability import AgentTracer, MetricsCollector


def test_agent_tracer_records_steps_and_saves(tmp_path):
    tracer = AgentTracer(run_id="run_001", query="What is 20% of 100?", agent_name="standard", task_id="task_001")
    tracer.record_step("retrieve_docs", arguments={"query": "population"}, observation="population=100", latency_ms=120.5)
    tracer.record_step("call_calculator", arguments={"expression": "100*0.2"}, observation="20", latency_ms=25.0)
    payload = tracer.finish(status="success", result={"final_answer": "20"})

    assert payload["run_id"] == "run_001"
    assert payload["status"] == "success"
    assert payload["total_latency_ms"] >= 0
    assert len(payload["steps"]) == 2

    out = tmp_path / "run_001.json"
    tracer.save(out)
    saved = json.loads(out.read_text(encoding="utf-8"))
    assert saved["run_id"] == "run_001"


def test_metrics_collector_compute_and_aggregate():
    traces = [
        {
            "status": "success",
            "total_latency_ms": 200.0,
            "steps": [
                {"action": "retrieve_docs", "latency_ms": 150.0},
                {"action": "call_calculator", "latency_ms": 50.0},
            ],
        },
        {
            "status": "failed",
            "total_latency_ms": 100.0,
            "steps": [{"action": "generate_answer", "latency_ms": 100.0, "error": "tool timeout"}],
        },
    ]

    per_run = MetricsCollector.compute(traces[0])
    assert per_run["steps"] == 2
    assert per_run["tool_calls"] == 2

    agg = MetricsCollector.aggregate(traces)
    assert agg["runs"] == 2
    assert agg["avg_steps_per_task"] == 1.5
    assert agg["avg_latency_ms"] == 150.0
    assert agg["failure_rate"] == 0.5
