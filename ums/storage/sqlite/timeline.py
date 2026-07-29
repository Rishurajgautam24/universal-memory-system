from __future__ import annotations

from uuid import UUID

from ums.models.timeline import TimelineEvent
from ums.storage.sqlite.connection import DatabaseManager


class SQLiteTimelineStore:
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

    async def append_event(self, event: TimelineEvent) -> TimelineEvent:
        data = event.model_dump()
        await self._db.execute(
            "INSERT INTO timeline_events (id, event_type, object_id, object_type, description, confidence, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                str(data["id"]),
                data["event_type"],
                str(data["object_id"]),
                data["object_type"],
                data["description"],
                data["confidence"],
                data["created_at"],
            ),
        )
        await self._db.commit()
        return event

    async def get_events(self, limit: int = 100, offset: int = 0) -> list[TimelineEvent]:
        rows = await self._db.fetch_all(
            "SELECT * FROM timeline_events ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        events = []
        for row in rows:
            row["id"] = UUID(row["id"])
            row["object_id"] = UUID(row["object_id"])
            events.append(TimelineEvent(**row))
        return events

    async def count_events(self) -> int:
        row = await self._db.fetch_one("SELECT COUNT(*) AS cnt FROM timeline_events")
        return row["cnt"] if row else 0
