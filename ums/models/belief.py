from __future__ import annotations

from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from ums.utils.datetime import now_utc


class Belief(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    statement: str
    confidence: float
    supporting_memory_ids: list[UUID] = Field(default_factory=list)
    contradicting_memory_ids: list[UUID] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: now_utc().isoformat().replace("+00:00", "Z"))
    updated_at: str = Field(default_factory=lambda: now_utc().isoformat().replace("+00:00", "Z"))

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {v}")
        return v
