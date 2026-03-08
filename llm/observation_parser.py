"""Convert tool outputs into observation booleans."""

from __future__ import annotations

from typing import Dict

from tools.tool_schema import ToolOutput


class ObservationParser:
    def parse(self, output: ToolOutput) -> Dict[str, bool]:
        relevant = bool(output.metadata.get("relevant_doc_found", False))
        answer_generated = bool(output.metadata.get("answer_generated", False)) or output.tool == "generate_answer"
        return {
            "relevant_doc_found": relevant,
            "doc_not_relevant": not relevant and output.tool == "retriever",
            "tool_success": output.success,
            "tool_failure": not output.success,
            "answer_generated": answer_generated,
        }
