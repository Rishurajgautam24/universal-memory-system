from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter

router = APIRouter()


@router.post("/v1/explain")
async def explain():
    return {
        "ok": True,
        "data": {
            "target": None,
            "evidence_chain": [],
            "summary": "",
            "confidence_history": [],
        },
        "meta": {"request_id": str(uuid4())},
    }
