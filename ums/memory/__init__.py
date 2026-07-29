from ums.memory.candidate import MemoryEngine
from ums.memory.deduplication import is_duplicate, merge_observation_into_candidate, semantic_similarity
from ums.memory.contradiction import CONTRADICTION_PAIRS, create_contradicted_candidate, detect_contradiction
from ums.memory.promotion import calculate_new_confidence, check_promotion_eligibility

__all__ = [
    "CONTRADICTION_PAIRS",
    "MemoryEngine",
    "calculate_new_confidence",
    "check_promotion_eligibility",
    "create_contradicted_candidate",
    "detect_contradiction",
    "is_duplicate",
    "merge_observation_into_candidate",
    "semantic_similarity",
]
