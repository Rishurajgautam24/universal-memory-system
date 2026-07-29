import logging
from typing import Optional

from ums.config import settings
from ums.models.audit import AuditLogEntry, AuditAction
from ums.models.candidate import MemoryCandidate, CandidateStatus
from ums.models.observation import Observation
from ums.models.timeline import TimelineEvent, EventType
from ums.models.verified_memory import VerifiedMemory, MemoryStatus
from ums.storage.interface import Storage
from ums.memory.deduplication import is_duplicate, merge_observation_into_candidate
from ums.memory.contradiction import detect_contradiction, create_contradicted_candidate
from ums.memory.promotion import check_promotion_eligibility
from ums.utils.datetime import now_utc

logger = logging.getLogger(__name__)


class MemoryEngine:
    def __init__(self, storage: Storage):
        self._storage = storage

    async def process_observation(self, observation: Observation) -> Optional[MemoryCandidate]:
        existing = await self._find_similar_candidate(observation)
        if existing:
            return await self._reinforce_candidate(existing, observation)
        return await self._create_candidate(observation)

    async def _find_similar_candidate(self, observation: Observation) -> Optional[MemoryCandidate]:
        candidates = await self._storage.find_candidates(status=CandidateStatus.ACCUMULATING.value)
        for cand in candidates:
            if is_duplicate(observation.statement, cand.statement, threshold=settings.semantic_dedup_threshold):
                return cand
        return None

    async def _create_candidate(self, observation: Observation) -> MemoryCandidate:
        obs_ref = {"obs_id": str(observation.id), "source": observation.source,
                   "statement": observation.statement, "confidence": observation.confidence}
        candidate = MemoryCandidate(
            statement=observation.statement,
            category=observation.category.value if observation.category else None,
            confidence=observation.confidence,
            supporting_obs=[obs_ref],
            status=CandidateStatus.ACCUMULATING,
        )
        existing = await self._storage.find_all_verified_memories(limit=100)
        has_conflict, conflicting = detect_contradiction(candidate, existing)
        if has_conflict:
            candidate = create_contradicted_candidate(candidate, conflicting)
        await self._storage.upsert_candidate(candidate)
        return candidate

    async def _reinforce_candidate(self, candidate: MemoryCandidate, observation: Observation) -> MemoryCandidate:
        candidate = merge_observation_into_candidate(candidate, observation)
        eligible, reason = check_promotion_eligibility(candidate)
        if eligible:
            candidate = await self._promote_candidate(candidate)
        await self._storage.upsert_candidate(candidate)
        return candidate

    async def _promote_candidate(self, candidate: MemoryCandidate) -> MemoryCandidate:
        candidate.status = CandidateStatus.PROMOTED
        memory = VerifiedMemory(
            statement=candidate.statement,
            category=candidate.category,
            confidence=candidate.confidence,
            source_candidate_id=candidate.id,
            supporting_obs=candidate.supporting_obs,
            status=MemoryStatus.ACTIVE,
        )
        await self._storage.upsert_verified_memory(memory)
        event = TimelineEvent(
            event_type=EventType.CANDIDATE_PROMOTED,
            object_id=memory.id,
            object_type="verified_memory",
            description=f"New memory: {candidate.statement[:100]}",
            confidence=candidate.confidence,
        )
        await self._storage.append_event(event)
        audit = AuditLogEntry(
            action=AuditAction.PROMOTE,
            object_type="verified_memory",
            object_id=memory.id,
            actor="MemoryEngine",
            details={"statement": memory.statement, "confidence": memory.confidence},
        )
        await self._storage.append(audit)
        logger.info("candidate_promoted", extra={"id": str(candidate.id)})
        return candidate
