from __future__ import annotations

from ums.config import settings
from ums.models.observation import ObservationCategory
from ums.storage.interface import Storage


class RecallLoaders:
    def __init__(self, storage: Storage):
        self._storage = storage

    async def load_projects(self, user_id: str) -> list[dict]:
        memories = await self._storage.find_all_verified_memories(limit=50)
        projects = {}
        for m in memories:
            if m.category == ObservationCategory.CONVERSATION.value:
                projects[m.statement] = {
                    "name": m.statement,
                    "confidence": m.confidence,
                    "last_active": m.updated_at,
                }
        return list(projects.values())

    async def load_beliefs(self, user_id: str, min_confidence: float | None = None) -> list[dict]:
        beliefs = await self._storage.find_all_beliefs(
            min_confidence=settings.recall_min_confidence if min_confidence is None else min_confidence
        )
        return [
            {
                "statement": b.statement,
                "confidence": b.confidence,
                "last_updated": b.updated_at,
            }
            for b in beliefs
        ]

    async def load_timeline(self, user_id: str, limit: int = 10) -> list[dict]:
        events = await self._storage.get_events(limit=limit)
        return [
            {
                "what": e.description,
                "when": e.created_at,
                "where": e.object_type,
                "type": e.event_type.value,
                "summary": e.description,
            }
            for e in events
        ]