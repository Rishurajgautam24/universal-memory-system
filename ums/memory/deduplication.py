from ums.models.candidate import MemoryCandidate
from ums.models.observation import Observation


def semantic_similarity(text_a: str, text_b: str) -> float:
    if text_a == text_b:
        return 1.0
    if not text_a or not text_b:
        return 0.99 if not text_a and not text_b else 0.0
    a_grams = set(text_a.lower().split())
    b_grams = set(text_b.lower().split())
    if not a_grams or not b_grams:
        return 0.0
    return len(a_grams & b_grams) / len(a_grams | b_grams)


def is_duplicate(statement_a: str, statement_b: str, threshold: float = 0.85) -> bool:
    return semantic_similarity(statement_a, statement_b) >= threshold


def merge_observation_into_candidate(candidate: MemoryCandidate, observation: Observation,
                                     decay: float = 1.0) -> MemoryCandidate:
    from ums.memory.promotion import calculate_new_confidence
    from ums.utils.datetime import now_utc
    obs_ref = {"obs_id": str(observation.id), "source": observation.source,
               "statement": observation.statement, "confidence": observation.confidence}
    candidate.supporting_obs.append(obs_ref)
    candidate.confidence = calculate_new_confidence(candidate.confidence, observation.confidence, decay)
    candidate.updated_at = now_utc().isoformat()
    return candidate
