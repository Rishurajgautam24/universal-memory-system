from __future__ import annotations

from collections.abc import Callable
from typing import Any


def score_relevance(confidence: float, recency_days: int = 0, keyword_score: float = 0.0) -> float:
    recency_factor = max(0.0, 1.0 - recency_days * 0.01)
    return min(1.0, confidence * 0.6 + recency_factor * 0.2 + keyword_score * 0.2)


def rank_and_deduplicate(
    items: list[dict],
    dedup_key: Callable[[dict], Any] | None = None,
    limit: int = 20,
) -> list[dict]:
    seen: set = set()
    result: list[dict] = []
    for item in items:
        key = dedup_key(item) if dedup_key else item.get("id", item.get("statement", ""))
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result[:limit]
