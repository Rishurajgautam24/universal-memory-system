from __future__ import annotations

from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from ums.utils.datetime import now_utc


class EventType(str, Enum):
    OBSERVATION = "OBSERVATION"
    CANDIDATE = "CANDIDATE"
    MEMORY = "MEMORY"
    ENTITY = "ENTITY"
    RELATIONSHIP = "RELATIONSHIP"
    BELIEF = "BELIEF"
    PROJECT = "PROJECT"
    REFLECTION = "REFLECTION"
    DISTILLATION = "DISTILLATION"
    SYSTEM = "SYSTEM"


class TimelineEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    object_id: UUID
    object_type: str
    description: str
    confidence: float
    created_at: str = Field(default_factory=lambda: now_utc().isoformat().replace("+00:00", "Z"))

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {v}")
        return v
