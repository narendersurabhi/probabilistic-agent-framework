"""Mock deterministic retriever."""

from __future__ import annotations

from tools.tool_schema import RetrieverArgs, ToolOutput


def run_retriever(args: RetrieverArgs) -> ToolOutput:
    query = args.query.lower()
    relevant = "reinforcement learning" in query or "population of france" in query
    return ToolOutput(
        tool="retriever",
        success=True,
        result=[{"title": "MockDoc", "snippet": query}],
        metadata={"relevant_doc_found": relevant},
    )
