from __future__ import annotations

import json
from uuid import UUID

from ums.models.audit import AuditLogEntry
from ums.storage.sqlite.connection import DatabaseManager


class SQLiteAuditLog:
    def __init__(self, db: DatabaseManager):
        self._db = db

    async def initialize(self) -> None:
        await self._db.initialize()

    async def close(self) -> None:
        await self._db.close()

    async def health_check(self) -> bool:
        try:
            await self._db.execute("SELECT 1")
            return True
        except BaseException:  # noqa: BLE001
            return False

    async def append(self, entry: AuditLogEntry) -> AuditLogEntry:
        data = entry.model_dump()
        details = json.dumps(data["details"]) if data.get("details") else None
        await self._db.execute(
            "INSERT INTO audit_log (id, action, object_type, object_id, actor, details, confidence, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                str(data["id"]),
                data["action"],
                data["object_type"],
                str(data["object_id"]),
                data["actor"],
                details,
                data["confidence"],
                data["created_at"],
            ),
        )
        await self._db.commit()
        return entry

    async def get_logs(self, limit: int = 100, offset: int = 0) -> list[AuditLogEntry]:
        rows = await self._db.fetch_all(
            "SELECT * FROM audit_log ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        entries = []
        for row in rows:
            row["id"] = UUID(row["id"])
            row["object_id"] = UUID(row["object_id"])
            if row.get("details"):
                row["details"] = json.loads(row["details"])
            entries.append(AuditLogEntry(**row))
        return entries
