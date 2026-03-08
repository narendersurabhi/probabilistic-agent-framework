from fastapi.testclient import TestClient

from api.server import app


def test_api_endpoints_basic() -> None:
    client = TestClient(app)

    run_resp = client.post('/run_task', json={'query': 'What is 12 percent of 350'})
    assert run_resp.status_code == 200
    payload = run_resp.json()
    assert 'steps' in payload
    assert 'run_id' in payload

    steps_resp = client.get('/agent_steps')
    assert steps_resp.status_code == 200
    assert isinstance(steps_resp.json(), list)

    belief_resp = client.get('/belief_state')
    assert belief_resp.status_code == 200
    assert 'knowledge_state' in belief_resp.json()

    bench_resp = client.get('/benchmark_results')
    assert bench_resp.status_code == 200

    failure_resp = client.get('/failure_analysis')
    assert failure_resp.status_code == 200

    trace_resp = client.get(f"/trace/{payload['run_id']}")
    assert trace_resp.status_code == 200
    trace_payload = trace_resp.json()
    assert 'nodes' in trace_payload
    assert 'edges' in trace_payload

    compare_resp = client.post('/compare_agents', json={'task_id': 'task_001', 'query': 'What is 20 percent of the population of Spain?'})
    assert compare_resp.status_code == 200
    compare_payload = compare_resp.json()
    assert 'standard_agent' in compare_payload
    assert 'active_inference_agent' in compare_payload

    arena_run_resp = client.post('/run_arena')
    assert arena_run_resp.status_code == 200

    arena_resp = client.get('/arena_results')
    assert arena_resp.status_code == 200


def test_websocket_stream_emits_step_events() -> None:
    client = TestClient(app)

    with client.websocket_connect('/stream') as ws:
        ws.send_text('ping')
        run_resp = client.post('/run_task', json={'query': 'What is 12 percent of 350'})
        assert run_resp.status_code == 200

        seen_event_types = set()
        for _ in range(8):
            payload = ws.receive_json()
            event = payload.get('event')
            if event:
                seen_event_types.add(event)
            if 'task_completed' in seen_event_types:
                break

    assert 'task_started' in seen_event_types
    assert 'agent_step' in seen_event_types
    assert 'task_completed' in seen_event_types
