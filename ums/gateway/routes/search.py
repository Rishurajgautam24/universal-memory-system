from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter

router = APIRouter()


@router.post("/v1/search")
async def search():
    return {
        "ok": True,
        "data": {
            "results": [],
            "total": 0,
            "query_interpretation": "",
        },
        "meta": {"request_id": str(uuid4())},
    }
