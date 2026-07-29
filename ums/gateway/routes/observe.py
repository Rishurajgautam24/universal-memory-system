from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import APIRouter, Request

from ums.gateway.exceptions import ValidationError
from ums.gateway.schemas import ObserveRequest

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/v1/observe", status_code=202)
async def observe(request: Request, body: ObserveRequest):
    from ums.gateway.app import get_ctx
    app_ctx = get_ctx()

    if not body.source.strip():
        raise ValidationError("source is required")
    if not body.conversation.strip():
        raise ValidationError("Conversation is empty")
    try:
        job_id = await app_ctx.observation_engine.process(
            source=body.source,
            conversation=body.conversation,
            session_id=body.metadata.get("session_id", str(uuid4())) if body.metadata else str(uuid4()),
            metadata=body.metadata,
        )
    except ValueError as e:
        raise ValidationError(str(e))

    return {
        "ok": True,
        "data": {
            "job_id": str(job_id),
            "status": "queued",
            "estimated_processing_ms": 3000,
            "message": "Conversation queued for memory processing",
        },
        "meta": {"request_id": str(uuid4())},
    }
