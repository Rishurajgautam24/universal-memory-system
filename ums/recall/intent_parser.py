from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class RecallIntent:
    type: str = "general"
    project: str | None = None
    focus: list[str] = field(default_factory=lambda: ["preferences", "projects", "beliefs"])


def parse_intent(task: str) -> RecallIntent:
    if not task.strip():
        return RecallIntent()
    task_lower = task.lower()
    intent = RecallIntent()
    project_match = re.search(r"(?:project|repo|app)\s+[\"']?([a-zA-Z0-9_-]+)", task_lower)
    if project_match:
        intent.project = project_match.group(1)
    if any(w in task_lower for w in ["review", "code", "debug", "fix", "implement"]):
        intent.type = "code_review"
    elif any(w in task_lower for w in ["what", "how", "explain", "tell me about"]):
        intent.type = "information"
    return intent
