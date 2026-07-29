from __future__ import annotations

import json
import re

from ums.llm.interface import LLMProvider
from ums.llm.prompts import entity_extraction_prompt, observation_extraction_prompt
from ums.models.observation import Observation, ObservationCategory


def _parse_json_response(content: str) -> list | None:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None


async def extract_entities(
    llm: LLMProvider, conversation: str, model: str | None = None
) -> list[dict]:
    messages = entity_extraction_prompt(conversation)
    response = await llm.complete(messages=messages, model=model, json_mode=True)
    result = _parse_json_response(response.content)
    return result if isinstance(result, list) else []


async def extract_observations(
    llm: LLMProvider,
    conversation: str,
    model: str | None = None,
    min_confidence: float = 0.4,
) -> list[Observation]:
    messages = observation_extraction_prompt(conversation)
    response = await llm.complete(messages=messages, model=model, json_mode=True)
    result = _parse_json_response(response.content)
    if not isinstance(result, list):
        return []
    observations = []
    for item in result:
        confidence = item.get("confidence", 0.0)
        if confidence < min_confidence:
            continue
        try:
            category = ObservationCategory(item.get("category", "FACT").upper())
        except ValueError:
            category = ObservationCategory.CONVERSATION
        obs = Observation(
            source="",
            session_id="",
            raw_text=conversation[:500],
            statement=item.get("statement", ""),
            confidence=confidence,
            category=category,
        )
        observations.append(obs)
    return observations
