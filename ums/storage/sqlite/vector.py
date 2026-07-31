from __future__ import annotations

import json
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
        vector_json = json.dumps(vector)
        metadata_json = json.dumps(metadata) if metadata else None
        await self._db.execute(
            "INSERT OR REPLACE INTO embeddings (id, vector, metadata, updated_at) "
            "VALUES (?, ?, ?, datetime('now'))",
            (str(object_id), vector_json, metadata_json),
        )
        await self._db.commit()

    async def search(
        self, query_vector: list[float], top_k: int = 10
    ) -> list[tuple[UUID, float]]:
        # In-memory cosine similarity search for SQLite (no vector extension)
        rows = await self._db.fetch_all("SELECT id, vector FROM embeddings")
        if not rows:
            return []

        results: list[tuple[UUID, float]] = []
        import math

        q_norm = math.sqrt(sum(x * x for x in query_vector))
        if q_norm == 0.0:
            return []

        for row in rows:
            vec = json.loads(row["vector"])
            dot = sum(x * y for x, y in zip(query_vector, vec))
            v_norm = math.sqrt(sum(x * x for x in vec))
            if v_norm == 0.0:
                continue
            sim = dot / (q_norm * v_norm)
            results.append((UUID(row["id"]), sim))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    async def delete_embedding(self, object_id: UUID) -> None:
        await self._db.execute("DELETE FROM embeddings WHERE id = ?", (str(object_id),))
        await self._db.commit()