#!/usr/bin/env python3
import asyncio

import structlog

from ums.config import settings
from ums.distillation.pipeline import DistillationPipeline
from ums.memory.candidate import MemoryEngine
from ums.storage.sqlite import SQLiteStorage

logger = structlog.get_logger()


async def main():
    storage = SQLiteStorage(settings.database_url)
    await storage.initialize()
    engine = MemoryEngine(storage)
    pipeline = DistillationPipeline(storage, engine)
    cycle = await pipeline.run()
    logger.info("result", status=cycle.status.value, obs=cycle.observations_read, promoted=cycle.candidates_promoted)


if __name__ == "__main__":
    asyncio.run(main())
