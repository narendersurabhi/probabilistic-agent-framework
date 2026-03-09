from src.evaluation.judges import HeuristicJudgeClient, JudgeRunner, LLMJudge


def test_llm_judge_returns_structured_scores() -> None:
    judge = LLMJudge(HeuristicJudgeClient())
    result = judge.evaluate(
        question="What is the capital of France?",
        context="France's capital city is Paris.",
        answer="Paris",
        ground_truth="Paris",
    )

    assert result.correctness_score == 10
    assert result.faithfulness_score == 10
    assert result.completeness_score >= 1
    assert result.explanation


def test_judge_runner_aggregate_scores() -> None:
    runner = JudgeRunner(LLMJudge(HeuristicJudgeClient()))
    results = [
        runner.evaluate_task(
            question="What is the capital of France?",
            context_docs=["France's capital city is Paris."],
            answer="Paris",
            ground_truth="Paris",
        ),
        runner.evaluate_task(
            question="What is 2 + 2?",
            context_docs=["2 + 2 equals 4."],
            answer="4",
            ground_truth="4",
        ),
    ]

    aggregate = runner.aggregate(results).to_dict()
    assert aggregate["judge_correctness"] == 10.0
    assert aggregate["judge_faithfulness"] == 10.0
    assert aggregate["judge_completeness"] >= 1.0
