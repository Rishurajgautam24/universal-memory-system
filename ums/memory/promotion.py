from ums.config import settings
from ums.models.candidate import CandidateStatus, MemoryCandidate


def calculate_new_confidence(current: float, new_obs: float, decay: float = 1.0) -> float:
    if current <= 0.0:
        return min(new_obs, 1.0)
    result = 1 - (1 - current) * (1 - new_obs) * decay
    return min(max(result, 0.0), 1.0)


def check_promotion_eligibility(candidate: MemoryCandidate, min_confidence: float | None = None,
                                min_evidence: int | None = None) -> tuple[bool, str]:
    if candidate.status == CandidateStatus.PROMOTED:
        return False, "Already PROMOTED"
    threshold = candidate.promotion_threshold if min_confidence is None else min_confidence
    evidence_count = settings.min_evidence_for_promotion if min_evidence is None else min_evidence
    if candidate.confidence < threshold:
        return False, f"Confidence {candidate.confidence:.2f} < {threshold}"
    if len(candidate.supporting_obs) < evidence_count:
        return False, f"Evidence {len(candidate.supporting_obs)} < {evidence_count}"
    if candidate.status != CandidateStatus.ACCUMULATING:
        return False, f"Status {candidate.status} != ACCUMULATING"
    return True, ""