"""Trace API endpoints for graph-based run inspection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

router = APIRouter()
TRACE_DIR = Path(__file__).resolve().parent.parent / "traces"


@router.get("/trace/{run_id}")
def get_trace(run_id: str) -> Dict[str, Any]:
    path = TRACE_DIR / f"{run_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Trace {run_id} not found")
    return json.loads(path.read_text(encoding="utf-8"))
