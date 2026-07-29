from __future__ import annotations

from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from ums.utils.datetime import now_utc


class AuditAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    ARCHIVE = "ARCHIVE"
    SUPERSEDE = "SUPERSEDE"
    PROMOTE = "PROMOTE"
    DELETE_FLAG = "DELETE_FLAG"


class AuditLogEntry(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    action: AuditAction
    object_type: str
    object_id: UUID
    actor: str
    details: dict | None = None
    confidence: float = 1.0
    created_at: str = Field(default_factory=lambda: now_utc().isoformat().replace("+00:00", "Z"))

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {v}")
        return v
