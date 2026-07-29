from __future__ import annotations

from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from ums.utils.datetime import now_utc


class EntityType(str, Enum):
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    CONCEPT = "CONCEPT"
    LOCATION = "LOCATION"
    EVENT = "EVENT"
    DOCUMENT = "DOCUMENT"
    OTHER = "OTHER"


class Entity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    entity_type: EntityType
    aliases: list[str] = Field(default_factory=list)
    description: str | None = None
    confidence: float
    created_at: str = Field(default_factory=lambda: now_utc().isoformat().replace("+00:00", "Z"))
    updated_at: str = Field(default_factory=lambda: now_utc().isoformat().replace("+00:00", "Z"))

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {v}")
        return v
