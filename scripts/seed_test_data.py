#!/usr/bin/env python3
import asyncio
import os

import structlog

from ums.config import settings
from ums.models.belief import Belief
from ums.models.candidate import MemoryCandidate
from ums.models.entity import Entity
from ums.storage.sqlite import SQLiteStorage
from ums.utils.datetime import now_utc

logger = structlog.get_logger()

SAMPLE_CONVERSATION = (
    "Alice: I'm building the Universal Memory System. "
    "It provides persistent memory for AI assistants across sessions. "
    "We use SQLite for storage with aiosqlite. "
    "The API is built with FastAPI and uses Bearer token auth. "
    "Bob: What about LLM integration? "
    "Alice: We use OpenRouter for access to GPT-4o for extraction and synthesis. "
    "The recall engine ranks beliefs by semantic similarity to the user's intent."
)

SEED_OBSERVATIONS = [
    {
        "statement": "Universal Memory System provides persistent memory for AI assistants",
        "confidence": 0.95,
        "category": "CONVERSATION",
    },
    {
        "statement": "UMS uses SQLite with aiosqlite for async database storage",
        "confidence": 0.9,
        "category": "CONVERSATION",
    },
    {
        "statement": "UMS API is built with FastAPI and uses Bearer token authentication",
        "confidence": 0.9,
        "category": "CONVERSATION",
    },
    {
        "statement": "UMS uses OpenRouter for GPT-4o access for extraction and synthesis",
        "confidence": 0.85,
        "category": "CONVERSATION",
    },
]


async def main():
    db_path = settings.database_url.replace("sqlite+aiosqlite://", "")
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    storage = SQLiteStorage(settings.database_url)
    await storage.initialize()

    now = now_utc().isoformat().replace("+00:00", "Z")

    for obs_data in SEED_OBSERVATIONS:
        candidate = MemoryCandidate(
            statement=obs_data["statement"],
            confidence=obs_data["confidence"],
            category=obs_data["category"],
            created_at=now,
            updated_at=now,
        )
        await storage.create_candidate(candidate)

    entity = Entity(
        name="Universal Memory System",
        entity_type="CONCEPT",
        confidence=0.95,
        description="A persistent memory layer for AI applications",
        created_at=now,
        updated_at=now,
    )
    await storage.create_entity(entity)

    belief = Belief(
        statement="UMS provides persistent memory for AI assistants across sessions",
        confidence=0.95,
        supporting_memory_ids=[],
        created_at=now,
        updated_at=now,
    )
    await storage.create_belief(belief)

    logger.info(
        "seed_data_loaded",
        observations=len(SEED_OBSERVATIONS),
        entities=1,
        beliefs=1,
    )
    await storage.close()


if __name__ == "__main__":
    asyncio.run(main())
