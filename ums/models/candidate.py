from __future__ import annotations

from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from ums.utils.datetime import now_utc


class CandidateStatus(str, Enum):
    ACCUMULATING = "ACCUMULATING"
    CORROBORATED = "CORROBORATED"
    CONFLICTED = "CONFLICTED"
    CONTRADICTED = "CONTRADICTED"
    ARCHIVED = "ARCHIVED"
    PROMOTED = "PROMOTED"


class MemoryCandidate(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    statement: str
    confidence: float
    category: str | None = None
    observation_ids: list[UUID] = Field(default_factory=list)
    supporting_obs: list[dict] = Field(default_factory=list)
    contradicting_obs: list[dict] = Field(default_factory=list)
    notes: str | None = None
    promotion_threshold: float = 0.75
    status: CandidateStatus = CandidateStatus.ACCUMULATING
    created_at: str = Field(default_factory=lambda: now_utc().isoformat().replace("+00:00", "Z"))
    updated_at: str = Field(default_factory=lambda: now_utc().isoformat().replace("+00:00", "Z"))

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {v}")
        return v

    def set_stage(self, new_status: CandidateStatus) -> None:
        stages = list(CandidateStatus)
        current_idx = stages.index(self.status)
        new_idx = stages.index(new_status)
        if new_idx < current_idx:
            raise ValueError(f"Cannot move from {self.status} to {new_status}")
        self.status = new_status
