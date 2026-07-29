from __future__ import annotations

from ums.config import settings
from ums.recall.assembler import ContextAssembler
from ums.recall.intent_parser import parse_intent
from ums.recall.loaders import RecallLoaders
from ums.storage.interface import Storage


class RecallEngine:
    def __init__(self, storage: Storage):
        self._storage = storage
        self._loaders = RecallLoaders(storage)
        self._assembler = ContextAssembler(self._loaders)

    async def recall(
        self, task: str, context: dict | None = None, options: dict | None = None
    ) -> dict:
        context = context or {}
        options = options or {}
        intent = parse_intent(task)
        project = context.get("project") or intent.project
        focus = context.get("focus") or intent.focus
        user_id = "default"

        ctx = await self._assembler.assemble(
            user_id=user_id,
            project_filter=project,
            focus=focus,
            max_tokens=options.get("max_tokens", settings.recall_max_tokens),
        )

        return {
            "context": ctx,
            "retrieval_metadata": {
                "stages_used": ["intent", "projects", "beliefs", "timeline"],
                "returned": len(ctx.get("relevant_beliefs", [])),
            },
        }
