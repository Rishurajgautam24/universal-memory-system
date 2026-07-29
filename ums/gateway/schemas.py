from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ObserveRequest(BaseModel):
    source: str
    conversation: str
    metadata: dict[str, Any] | None = None
    options: dict[str, Any] | None = None


class ObserveData(BaseModel):
    job_id: UUID
    status: str = "queued"
    estimated_processing_ms: int = 3000
    message: str = "Conversation queued for memory processing"


class RecallRequest(BaseModel):
    task: str
    context: dict[str, Any] | None = None
    options: dict[str, Any] | None = None


class RecallData(BaseModel):
    context: dict[str, Any]
    retrieval_metadata: dict[str, Any]


class SearchRequest(BaseModel):
    query: str
    filters: dict[str, Any] | None = None
    options: dict[str, Any] | None = None


class SearchData(BaseModel):
    results: list[dict[str, Any]] = Field(default_factory=list)
    total: int = 0
    query_interpretation: str = ""


class TimelineData(BaseModel):
    events: list[dict[str, Any]]
    pagination: dict[str, Any]


class ExplainRequest(BaseModel):
    target_id: UUID
    target_type: str
    options: dict[str, Any] | None = None


class ExplainData(BaseModel):
    target: dict[str, Any] | None = None
    evidence_chain: list[dict[str, Any]] = Field(default_factory=list)
    summary: str = ""
    confidence_history: list[dict[str, Any]] = Field(default_factory=list)


class ReflectRequest(BaseModel):
    period: dict[str, Any] | None = None
    focus: list[str] | None = None
    options: dict[str, Any] | None = None


class ReflectData(BaseModel):
    reflection_id: UUID | None = None
    status: str = "not_implemented"
    period: dict[str, Any] | None = None
    digest: str = ""
    summary: dict[str, Any] | None = None


class Meta(BaseModel):
    request_id: UUID


class SuccessResponse(BaseModel):
    ok: bool = True
    data: dict[str, Any]
    meta: Meta


class ErrorResponse(BaseModel):
    ok: bool = False
    error: str
    message: str
    meta: Meta
