"""Mock deterministic retriever backed by a static knowledge base."""

from __future__ import annotations

from tools.tool_schema import RetrieverArgs, ToolOutput

KNOWLEDGE_BASE = {
    "population of france": {"population": 67_000_000},
    "population of germany": {"population": 83_000_000},
    "reinforcement learning": {
        "description": "A machine learning paradigm where agents learn by interacting with environments."
    },
}


def run_retriever(args: RetrieverArgs) -> ToolOutput:
    query = args.query.lower()

    for key, value in KNOWLEDGE_BASE.items():
        if key in query:
            return ToolOutput(
                tool="retriever",
                success=True,
                result=[{"title": key.title(), "snippet": value}],
                metadata={"relevant_doc_found": True, "matched_key": key},
            )

    return ToolOutput(
        tool="retriever",
        success=False,
        result=None,
        metadata={"relevant_doc_found": False},
    )
