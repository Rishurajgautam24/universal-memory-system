from __future__ import annotations

import re


def segment_conversation(text: str, max_chunk_tokens: int = 4000) -> list[str]:
    if not text.strip():
        return []
    max_chars = max_chunk_tokens * 4
    if len(text) <= max_chars:
        return [text]
    segments = []
    current = ""
    for paragraph in re.split(r"\n\n+", text):
        candidate = current + ("\n\n" if current else "") + paragraph
        if len(candidate) > max_chars and current:
            segments.append(current)
            current = paragraph
        else:
            current = candidate
    if current:
        segments.append(current)
    return segments


def estimate_tokens(text: str) -> int:
    return len(text) // 4
