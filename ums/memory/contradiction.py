from typing import List, Tuple

from ums.models.candidate import MemoryCandidate, CandidateStatus
from ums.models.verified_memory import VerifiedMemory
from ums.memory.deduplication import semantic_similarity

CONTRADICTION_PAIRS = [
    ("likes", "dislikes"), ("prefers", "avoids"),
    ("is", "is not"), ("loves", "hates"),
    ("uses", "stopped using"), ("interested in", "not interested in"),
    ("good", "bad"), ("recommends", "advises against"),
]


def detect_contradiction(candidate: MemoryCandidate, existing_memories: List[VerifiedMemory],
                         threshold: float = 0.85) -> Tuple[bool, List[VerifiedMemory]]:
    conflicting = []
    for mem in existing_memories:
        sim = semantic_similarity(candidate.statement, mem.statement)
        a, b = candidate.statement.lower(), mem.statement.lower()
        has_pair = any((pos in a and neg in b) or (neg in a and pos in b) for pos, neg in CONTRADICTION_PAIRS)
        if sim >= threshold and has_pair:
            conflicting.append(mem)
    return len(conflicting) > 0, conflicting


def create_contradicted_candidate(candidate: MemoryCandidate,
                                  contradicting_memories: List[VerifiedMemory]) -> MemoryCandidate:
    candidate.status = CandidateStatus.CONTRADICTED
    candidate.notes = f"Contradicts {len(contradicting_memories)} memory(ies)"
    for mem in contradicting_memories:
        candidate.contradicting_obs.append({"memory_id": str(mem.id), "statement": mem.statement})
    return candidate
