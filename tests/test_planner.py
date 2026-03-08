from src.planning.active_inference_planner import ActiveInferencePlanner


def test_belief_update_changes_distribution() -> None:
    planner = ActiveInferencePlanner()
    before = planner.get_belief_state()["knowledge_state"]["unknown"]
    planner.update_beliefs("relevant_doc_found")
    after = planner.get_belief_state()["knowledge_state"]["unknown"]
    assert before != after


def test_policy_eval_returns_probabilities() -> None:
    planner = ActiveInferencePlanner()
    planner.update_beliefs("tool_success")
    policy_probs, g_vals = planner.evaluate_policies()
    assert set(policy_probs.keys()) == {"retrieve_docs", "call_calculator", "generate_answer"}
    assert set(g_vals.keys()) == {"retrieve_docs", "call_calculator", "generate_answer"}
    assert abs(sum(policy_probs.values()) - 1.0) < 1e-6


def test_select_action_valid() -> None:
    planner = ActiveInferencePlanner()
    planner.update_beliefs("relevant_doc_found")
    planner.evaluate_policies()
    action = planner.select_action()
    assert action in {"retrieve_docs", "call_calculator", "generate_answer"}
