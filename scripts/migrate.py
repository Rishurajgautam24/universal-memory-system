#!/usr/bin/env python3
import asyncio
import os

import structlog

from ums.config import settings
from ums.storage.sqlite import SQLiteStorage

logger = structlog.get_logger()


async def main():
    db_path = settings.database_url.replace("sqlite+aiosqlite://", "")
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    storage = SQLiteStorage(settings.database_url)
    await storage.initialize()
    logger.info("migrations_complete", database=settings.database_url)
    await storage.close()


if __name__ == "__main__":
    asyncio.run(main())
