from ums.memory.deduplication import is_duplicate, merge_observation_into_candidate, semantic_similarity
from ums.models.candidate import MemoryCandidate
from ums.models.observation import Observation


class TestSemanticSimilarity:
    def test_identical_texts(self):
        assert semantic_similarity("hello world", "hello world") == 1.0

    def test_empty_strings(self):
        assert semantic_similarity("", "") == 1.0
        assert semantic_similarity("hello", "") == 0.0
        assert semantic_similarity("", "world") == 0.0

    def test_partial_overlap(self):
        sim = semantic_similarity("hello world foo", "hello world bar")
        assert 0.4 < sim < 1.0

    def test_no_overlap(self):
        assert semantic_similarity("abc def", "ghi jkl") == 0.0

    def test_case_insensitive(self):
        sim = semantic_similarity("Hello World", "hello world")
        assert sim == 1.0


class TestIsDuplicate:
    def test_identical_is_duplicate(self):
        assert is_duplicate("User likes python", "user likes python") is True

    def test_high_similarity(self):
        assert is_duplicate("a b c d e f g", "a b c d e f g h") is True

    def test_low_similarity(self):
        assert is_duplicate("User likes python", "user hates java") is False

    def test_custom_threshold(self):
        assert is_duplicate("a b c", "a b d", threshold=0.5) is True
        assert is_duplicate("a b c", "a b d", threshold=0.8) is False


class TestMergeObservationIntoCandidate:
    def test_merges_and_updates_confidence(self):
        candidate = MemoryCandidate(statement="test", confidence=0.5)
        obs = Observation(source="user", session_id="s1", raw_text="test", statement="test", confidence=0.8)
        merged = merge_observation_into_candidate(candidate, obs)
        assert len(merged.supporting_obs) == 1
        assert merged.supporting_obs[0]["source"] == "user"
        assert merged.confidence > 0.5

    def test_multiple_merges(self):
        candidate = MemoryCandidate(statement="test", confidence=0.5)
        obs1 = Observation(source="a", session_id="s1", raw_text="x", statement="test", confidence=0.6)
        obs2 = Observation(source="b", session_id="s1", raw_text="x", statement="test", confidence=0.7)
        merged = merge_observation_into_candidate(candidate, obs1)
        merged = merge_observation_into_candidate(merged, obs2)
        assert len(merged.supporting_obs) == 2
