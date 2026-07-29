from __future__ import annotations

from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from ums.utils.datetime import now_utc


class MemoryStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    SUPERSEDED = "SUPERSEDED"


class VerifiedMemory(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    statement: str
    confidence: float
    source_candidate_id: UUID | None = None
    status: MemoryStatus = MemoryStatus.ACTIVE
    version: int = Field(default=1, ge=1)
    superseded_by: UUID | None = None
    created_at: str = Field(default_factory=lambda: now_utc().isoformat().replace("+00:00", "Z"))
    updated_at: str = Field(default_factory=lambda: now_utc().isoformat().replace("+00:00", "Z"))

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {v}")
        return v

    def set_stage(self, new_status: MemoryStatus) -> None:
        stages = list(MemoryStatus)
        current_idx = stages.index(self.status)
        new_idx = stages.index(new_status)
        if new_idx < current_idx:
            raise ValueError(f"Cannot move from {self.status} to {new_status}")
        self.status = new_status
