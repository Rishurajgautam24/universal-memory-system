from __future__ import annotations

from uuid import UUID

from ums.storage.sqlite.connection import DatabaseManager


class SQLiteVectorStore:
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

    async def upsert_embedding(
        self, object_id: UUID, vector: list[float], metadata: dict | None = None
    ) -> None:
        pass

    async def search(
        self, vector: list[float], top_k: int = 10
    ) -> list[tuple[UUID, float]]:
        return []

    async def delete_embedding(self, object_id: UUID) -> None:
        pass
