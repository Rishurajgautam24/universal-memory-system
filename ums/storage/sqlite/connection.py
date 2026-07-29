from __future__ import annotations

import aiosqlite

from ums.storage.sqlite.migrations import MIGRATIONS


class DatabaseManager:
    def __init__(self, database_url: str):
        self._url = database_url.replace("sqlite+aiosqlite://", "")
        if not self._url:
            self._url = ":memory:"
        self._db: aiosqlite.Connection | None = None

    async def initialize(self):
        self._db = await aiosqlite.connect(self._url)
        self._db.row_factory = aiosqlite.Row
        await self._db.execute("PRAGMA journal_mode=WAL")
        await self._db.execute("PRAGMA foreign_keys=ON")
        await self._run_migrations()

    async def close(self):
        if self._db:
            await self._db.close()
            self._db = None

    async def execute(self, sql, params=()) -> aiosqlite.Cursor:
        if not self._db:
            raise RuntimeError("DB not initialized")
        return await self._db.execute(sql, params)

    async def execute_many(self, sql, params):
        if not self._db:
            raise RuntimeError("DB not initialized")
        await self._db.executemany(sql, params)

    async def fetch_all(self, sql, params=()) -> list[dict]:
        cursor = await self.execute(sql, params)
        return [dict(r) for r in await cursor.fetchall()]

    async def fetch_one(self, sql, params=()) -> dict | None:
        cursor = await self.execute(sql, params)
        row = await cursor.fetchone()
        return dict(row) if row else None

    async def commit(self):
        if self._db:
            await self._db.commit()

    async def _run_migrations(self):
        await self._db.execute(
            "CREATE TABLE IF NOT EXISTS _migrations (version INTEGER PRIMARY KEY, applied_at TEXT)"
        )
        existing = await self.fetch_all("SELECT version FROM _migrations")
        applied = {r["version"] for r in existing}
        for version, sql in MIGRATIONS:
            if version not in applied:
                await self._db.executescript(sql)
                await self._db.execute(
                    "INSERT INTO _migrations (version, applied_at) VALUES (?, datetime('now'))",
                    (version,),
                )
        await self._db.commit()
