from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import APIRouter, Request

from ums.gateway.exceptions import ValidationError
from ums.gateway.schemas import RecallRequest

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/v1/recall")
async def recall(request: Request, body: RecallRequest):
    from ums.gateway.app import get_ctx
    app_ctx = get_ctx()

    if not body.task.strip():
        raise ValidationError("task is required")

    result = await app_ctx.recall_engine.recall(
        task=body.task,
        context=body.context,
        options=body.options,
    )

    return {
        "ok": True,
        "data": result,
        "meta": {"request_id": str(uuid4())},
    }
