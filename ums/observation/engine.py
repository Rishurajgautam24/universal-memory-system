from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID, uuid4

from ums.llm.interface import LLMProvider
from ums.observation.extractors import extract_observations
from ums.observation.segmenter import segment_conversation
from ums.storage.interface import Storage

from ums.models.observation import ObservationStage

logger = logging.getLogger(__name__)


class ObservationEngine:
    def __init__(
        self,
        llm: LLMProvider,
        storage: Storage,
        min_confidence: float = 0.4,
        max_observations: int = 50,
    ):
        self._llm = llm
        self._storage = storage
        self._min_confidence = min_confidence
        self._max_observations = max_observations

    async def process(
        self,
        source: str,
        conversation: str,
        session_id: str,
        metadata: Optional[dict] = None,
    ) -> UUID:
        if not conversation.strip():
            raise ValueError("conversation is empty")
        if len(conversation.split()) < 10:
            raise ValueError("conversation too short (min 10 words)")
        metadata = metadata or {}
        job_id = uuid4()
        segments = segment_conversation(conversation)
        all_observations = []
        for segment in segments:
            observations = await extract_observations(
                self._llm, segment, min_confidence=self._min_confidence
            )
            for obs in observations:
                obs.source = source
                obs.session_id = session_id
                obs.set_stage(ObservationStage.PROCESSED)
            all_observations.extend(observations)
            if len(all_observations) >= self._max_observations:
                break
        for obs in all_observations[: self._max_observations]:
            await self._storage.enqueue(obs)
        logger.info(
            "observation_processed",
            extra={"job_id": str(job_id), "count": len(all_observations)},
        )
        return job_id
