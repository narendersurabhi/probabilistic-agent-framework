from agents.react_agent import ReActAgent


class DummyLLM:
    def generate(self, prompt: str) -> str:
        return "use retrieve_docs"


def test_react_baseline_returns_prompt_and_response() -> None:
    agent = ReActAgent(llm=DummyLLM(), tools={"retrieve_docs": lambda query: query})
    result = agent.run("What is the population of Japan?")

    assert "Question: What is the population of Japan?" in result["prompt"]
    assert result["response"] == "use retrieve_docs"
    assert result["available_tools"] == ["retrieve_docs"]
