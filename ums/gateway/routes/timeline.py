from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/v1/timeline")
async def timeline(
    from_: str | None = Query(None, alias="from"),
    to: str | None = Query(None),
    project: str | None = Query(None),
    event_type: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    page: int = Query(1, ge=1),
):
    from ums.gateway.app import get_ctx
    app_ctx = get_ctx()

    offset = (page - 1) * limit
    events = await app_ctx.storage.get_events(limit=limit, offset=offset)

    event_list = []
    for ev in events:
        if from_ and ev.created_at < from_:
            continue
        if to and ev.created_at > to:
            continue
        entry = {
            "id": str(ev.id),
            "when": ev.created_at,
            "what": ev.description,
            "event_type": ev.event_type.value if hasattr(ev.event_type, "value") else str(ev.event_type),
            "object_type": ev.object_type,
            "confidence": ev.confidence,
        }
        event_list.append(entry)

    # Count total matching events for accurate pagination
    total = await app_ctx.storage.count_events()
    has_more = (offset + limit) < total
    return {
        "ok": True,
        "data": {
            "events": event_list,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "has_more": has_more,
            },
        },
        "meta": {"request_id": str(uuid4())},
    }