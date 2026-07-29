from __future__ import annotations

from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from ums.utils.datetime import now_utc


class ObservationStage(str, Enum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    ARCHIVED = "ARCHIVED"


class ObservationCategory(str, Enum):
    CONVERSATION = "CONVERSATION"
    DOCUMENT = "DOCUMENT"
    CODE = "CODE"
    REFLECTION = "REFLECTION"
    WEB = "WEB"
    MANUAL = "MANUAL"
    SYSTEM = "SYSTEM"


class Observation(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    source: str
    session_id: str
    raw_text: str
    statement: str
    confidence: float
    category: ObservationCategory | None = None
    stage: ObservationStage = ObservationStage.PENDING
    created_at: str = Field(default_factory=lambda: now_utc().isoformat().replace("+00:00", "Z"))
    updated_at: str = Field(default_factory=lambda: now_utc().isoformat().replace("+00:00", "Z"))

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {v}")
        return v

    def set_stage(self, new_stage: ObservationStage) -> None:
        stages = list(ObservationStage)
        current_idx = stages.index(self.stage)
        new_idx = stages.index(new_stage)
        if new_idx < current_idx:
            raise ValueError(f"Cannot move from {self.stage} to {new_stage}")
        self.stage = new_stage
