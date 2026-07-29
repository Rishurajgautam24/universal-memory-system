from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter

router = APIRouter()


@router.post("/v1/reflect")
async def reflect():
    return {
        "ok": True,
        "data": {
            "reflection_id": None,
            "status": "not_implemented",
            "period": None,
            "digest": "",
            "summary": None,
        },
        "meta": {"request_id": str(uuid4())},
    }
