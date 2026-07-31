from __future__ import annotations

from uuid import UUID

from ums.models.observation import Observation, ObservationStage
from ums.storage.interface import Storage
from ums.storage.sqlite.audit import SQLiteAuditLog
from ums.storage.sqlite.connection import DatabaseManager
from ums.storage.sqlite.graph import SQLiteGraphStore, _build_observation
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

    async def enqueue(self, observation: Observation) -> None:
        await self.create_observation(observation)

    async def dequeue_batch(self, batch_size: int = 10) -> list[Observation]:
        rows = await self._db.fetch_all(
            "SELECT * FROM observations WHERE stage = 'PENDING' ORDER BY created_at ASC LIMIT ?",
            (batch_size,),
        )
        observations = []
        for row in rows:
            obs = _build_observation(row)
            await self._db.execute(
                "UPDATE observations SET stage = 'PROCESSED', updated_at = ? WHERE id = ?",
                (obs.updated_at, str(obs.id)),
            )
            observations.append(obs)
        await self._db.commit()
        return observations

    async def requeue(self, observation_id: UUID) -> None:
        from ums.utils.datetime import now_utc

        now = now_utc().isoformat().replace("+00:00", "Z")
        await self._db.execute(
            "UPDATE observations SET stage = 'PENDING', updated_at = ? WHERE id = ?",
            (now, str(observation_id)),
        )
        await self._db.commit()

    async def mark_processed(self, observation_id: UUID) -> None:
        from ums.utils.datetime import now_utc

        now = now_utc().isoformat().replace("+00:00", "Z")
        await self._db.execute(
            "UPDATE observations SET stage = 'ARCHIVED', updated_at = ? WHERE id = ?",
            (now, str(observation_id)),
        )
        await self._db.commit()

    async def get_pending_count(self) -> int:
        row = await self._db.fetch_one(
            "SELECT COUNT(*) AS cnt FROM observations WHERE stage = 'PENDING'"
        )
        return row["cnt"] if row else 0

    async def get_by_stage(self, stage: str) -> list[Observation]:
        rows = await self._db.fetch_all(
            "SELECT * FROM observations WHERE stage = ? ORDER BY created_at ASC",
            (stage,),
        )
        return [_build_observation(row) for row in rows]