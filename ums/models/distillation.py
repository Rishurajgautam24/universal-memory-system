from __future__ import annotations

from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from ums.utils.datetime import now_utc


class Distillation(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    content: str
    confidence: float
    source_reflection_ids: list[UUID] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: now_utc().isoformat().replace("+00:00", "Z"))
    updated_at: str = Field(default_factory=lambda: now_utc().isoformat().replace("+00:00", "Z"))

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {v}")
        return v


class CycleStatus(str, Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DistillationCycle(BaseModel):
    started_at: str
    status: CycleStatus
    observations_read: int = 0
    candidates_promoted: int = 0
    candidates_created: int = 0
    completed_at: str | None = None
    summary: str | None = None
    errors: list[str] = Field(default_factory=list)
