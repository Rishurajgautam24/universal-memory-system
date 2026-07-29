from __future__ import annotations

from ums.config import settings
from ums.recall.loaders import RecallLoaders


class ContextAssembler:
    def __init__(self, loaders: RecallLoaders):
        self._loaders = loaders

    async def assemble(
        self,
        user_id: str,
        project_filter: str | None = None,
        focus: list[str] | None = None,
        max_tokens: int | None = None,
    ) -> dict:
        focus = focus or []
        max_tokens = max_tokens or settings.recall_max_tokens
        context: dict = {
            "identity_summary": "",
            "relevant_beliefs": [],
            "active_projects": [],
            "relevant_preferences": [],
            "recent_timeline": [],
            "skills": [],
            "prompt_ready_summary": "",
        }

        if not focus or "projects" in focus:
            context["active_projects"] = await self._loaders.load_projects(user_id)

        if not focus or "beliefs" in focus:
            context["relevant_beliefs"] = await self._loaders.load_beliefs(user_id)

        timeline = await self._loaders.load_timeline(user_id, limit=10)
        context["recent_timeline"] = timeline

        lines = []
        if context["active_projects"]:
            lines.append("## Active Projects")
            for p in context["active_projects"][:3]:
                lines.append(f"- {p['name']} (confidence: {p['confidence']:.2f})")
        if context["relevant_beliefs"]:
            lines.append("## Relevant Beliefs")
            for b in context["relevant_beliefs"][:5]:
                lines.append(f"- {b['statement']} (confidence: {b['confidence']:.2f})")
        context["prompt_ready_summary"] = "\n".join(lines[: int(max_tokens / 20)])

        return context
