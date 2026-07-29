from __future__ import annotations

from uuid import UUID

from ums.models.candidate import MemoryCandidate
from ums.storage.interface import Storage
from ums.storage.sqlite.audit import SQLiteAuditLog
from ums.storage.sqlite.connection import DatabaseManager
from ums.storage.sqlite.graph import SQLiteGraphStore, _build_candidate
from ums.storage.sqlite.timeline import SQLiteTimelineStore
from ums.storage.sqlite.vector import SQLiteVectorStore


class SQLiteStorage(SQLiteGraphStore, SQLiteTimelineStore, SQLiteVectorStore, SQLiteAuditLog, Storage):
    def __init__(self, database_url: str):
        self._db = DatabaseManager(database_url)
        SQLiteGraphStore.__init__(self, self._db)
        SQLiteTimelineStore.__init__(self, self._db)
        SQLiteVectorStore.__init__(self, self._db)
        SQLiteAuditLog.__init__(self, self._db)

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

    # --- CandidateQueueInterface ---

    async def enqueue(self, candidate: MemoryCandidate) -> None:
        await self.create_candidate(candidate)

    async def dequeue_batch(self, batch_size: int = 10) -> list[MemoryCandidate]:
        rows = await self._db.fetch_all(
            "SELECT * FROM candidates WHERE status = 'ACCUMULATING' ORDER BY created_at ASC LIMIT ?",
            (batch_size,),
        )
        candidates = []
        for row in rows:
            candidate = _build_candidate(row)
            await self._db.execute(
                "UPDATE candidates SET status = 'CORROBORATED', updated_at = ? WHERE id = ?",
                (candidate.updated_at, str(candidate.id)),
            )
            candidates.append(candidate)
        await self._db.commit()
        return candidates

    async def requeue(self, candidate_id: UUID) -> None:
        from ums.utils.datetime import now_utc

        now = now_utc().isoformat().replace("+00:00", "Z")
        await self._db.execute(
            "UPDATE candidates SET status = 'ACCUMULATING', updated_at = ? WHERE id = ?",
            (now, str(candidate_id)),
        )
        await self._db.commit()

    async def mark_processed(self, candidate_id: UUID) -> None:
        from ums.utils.datetime import now_utc

        now = now_utc().isoformat().replace("+00:00", "Z")
        await self._db.execute(
            "UPDATE candidates SET status = 'PROMOTED', updated_at = ? WHERE id = ?",
            (now, str(candidate_id)),
        )
        await self._db.commit()

    async def get_pending_count(self) -> int:
        row = await self._db.fetch_one(
            "SELECT COUNT(*) AS cnt FROM candidates WHERE status = 'ACCUMULATING'"
        )
        return row["cnt"] if row else 0

    async def get_by_stage(self, stage: str) -> list[MemoryCandidate]:
        rows = await self._db.fetch_all(
            "SELECT * FROM candidates WHERE status = ? ORDER BY created_at ASC",
            (stage,),
        )
        return [_build_candidate(row) for row in rows]


