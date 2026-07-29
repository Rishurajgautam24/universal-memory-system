from ums.memory.promotion import calculate_new_confidence, check_promotion_eligibility
from ums.models.candidate import MemoryCandidate, CandidateStatus


class TestCalculateNewConfidence:
    def test_zero_current(self):
        assert calculate_new_confidence(0.0, 0.8) == 0.8

    def test_combined_confidence(self):
        result = calculate_new_confidence(0.5, 0.5)
        assert round(result, 4) == 0.75

    def test_clamps_to_one(self):
        result = calculate_new_confidence(0.9, 0.9)
        assert round(result, 2) == 0.99

    def test_with_decay(self):
        result = calculate_new_confidence(0.5, 0.5, decay=0.5)
        assert round(result, 4) == 0.875


class TestCheckPromotionEligibility:
    def test_below_confidence_returns_false(self):
        c = MemoryCandidate(statement="x", confidence=0.3, supporting_obs=[{"obs_id": "1"}])
        eligible, reason = check_promotion_eligibility(c, min_confidence=0.7, min_evidence=1)
        assert eligible is False
        assert "Confidence" in reason

    def test_below_evidence_count_returns_false(self):
        c = MemoryCandidate(statement="x", confidence=0.9, supporting_obs=[{"obs_id": "1"}])
        eligible, reason = check_promotion_eligibility(c, min_confidence=0.7, min_evidence=3)
        assert eligible is False
        assert "Evidence" in reason

    def test_already_promoted_returns_false(self):
        c = MemoryCandidate(statement="x", confidence=0.9, status=CandidateStatus.PROMOTED,
                            supporting_obs=[{"obs_id": "1"} for _ in range(3)])
        eligible, reason = check_promotion_eligibility(c, min_confidence=0.7, min_evidence=1)
        assert eligible is False
        assert "Already PROMOTED" in reason

    def test_not_accumulating_returns_false(self):
        c = MemoryCandidate(statement="x", confidence=0.9, status=CandidateStatus.CONFLICTED,
                            supporting_obs=[{"obs_id": "1"} for _ in range(3)])
        eligible, reason = check_promotion_eligibility(c, min_confidence=0.7, min_evidence=1)
        assert eligible is False
        assert "ACCUMULATING" in reason

    def test_eligible_returns_true(self):
        c = MemoryCandidate(statement="x", confidence=0.9,
                            supporting_obs=[{"obs_id": "1"}, {"obs_id": "2"}])
        eligible, reason = check_promotion_eligibility(c, min_confidence=0.7, min_evidence=2)
        assert eligible is True
        assert reason == ""
