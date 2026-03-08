from benchmarks.active_inference_agent import ActiveInferenceBenchmarkAgent
from benchmarks.react_agent import ReActAgent
from benchmarks.standard_agent import StandardToolAgent
from evaluation.harness import AgentHarness


def test_harness_step_execution() -> None:
    harness = AgentHarness()
    row = harness.run_step(
        step=0,
        query="Find documents about reinforcement learning",
        expected_tool="retrieve_docs",
        arguments={"query": "Find documents about reinforcement learning"},
    )
    assert "selected_action" in row
    assert "critic_evaluation" in row


def test_benchmark_agents_emit_trace() -> None:
    query = "What is 12 percent of 350"
    for agent in (StandardToolAgent(), ReActAgent(max_steps=2), ActiveInferenceBenchmarkAgent(max_steps=2)):
        result = agent.run(query)
        assert "trace" in result
        assert len(result["trace"]) >= 1
        assert "tool" in result["trace"][0]
