import pytest

from ums.recall.ranker import rank_and_deduplicate, score_relevance


class TestScoreRelevance:
    def test_perfect_score(self):
        score = score_relevance(confidence=1.0, recency_days=0, keyword_score=1.0)
        assert score == pytest.approx(1.0)

    def test_minimum_score(self):
        score = score_relevance(confidence=0.0, recency_days=1000, keyword_score=0.0)
        assert score == pytest.approx(0.0)

    def test_confidence_weight(self):
        score = score_relevance(confidence=0.5, recency_days=0, keyword_score=0.0)
        assert score == pytest.approx(0.5)

    def test_recency_penalty(self):
        recent = score_relevance(confidence=1.0, recency_days=0, keyword_score=0.0)
        old = score_relevance(confidence=1.0, recency_days=50, keyword_score=0.0)
        assert recent > old

    def test_recency_factor_decays(self):
        score = score_relevance(confidence=1.0, recency_days=100, keyword_score=0.0)
        assert score < 1.0

    def test_keyword_score_contributes(self):
        no_keyword = score_relevance(confidence=0.5, recency_days=0, keyword_score=0.0)
        with_keyword = score_relevance(confidence=0.5, recency_days=0, keyword_score=1.0)
        assert with_keyword > no_keyword

    def test_result_capped_at_one(self):
        score = score_relevance(confidence=2.0, recency_days=0, keyword_score=2.0)
        assert score == pytest.approx(1.0)

    def test_recency_factor_floor(self):
        score = score_relevance(confidence=0.5, recency_days=200, keyword_score=0.0)
        assert score == pytest.approx(0.3)

    def test_mixed_values(self):
        score = score_relevance(confidence=0.8, recency_days=10, keyword_score=0.5)
        expected = 0.8 * 0.6 + max(0.0, 1.0 - 10 * 0.01) * 0.2 + 0.5 * 0.2
        assert score == pytest.approx(expected)


class TestRankAndDeduplicate:
    def test_returns_all_items_below_limit(self):
        items = [{"id": "1"}, {"id": "2"}]
        result = rank_and_deduplicate(items, limit=20)
        assert len(result) == 2

    def test_respects_limit(self):
        items = [{"id": str(i)} for i in range(100)]
        result = rank_and_deduplicate(items, limit=10)
        assert len(result) == 10

    def test_deduplicates_by_id(self):
        items = [{"id": "1"}, {"id": "1"}, {"id": "2"}]
        result = rank_and_deduplicate(items)
        assert len(result) == 2

    def test_deduplicates_by_statement_fallback(self):
        items = [{"statement": "foo"}, {"statement": "foo"}, {"statement": "bar"}]
        result = rank_and_deduplicate(items)
        assert len(result) == 2

    def test_custom_dedup_key(self):
        items = [{"name": "a"}, {"name": "a"}, {"name": "b"}]
        result = rank_and_deduplicate(items, dedup_key=lambda x: x["name"])
        assert len(result) == 2

    def test_preserves_order(self):
        items = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
        result = rank_and_deduplicate(items, limit=2)
        assert result == [{"id": "1"}, {"id": "2"}]

    def test_empty_items(self):
        result = rank_and_deduplicate([])
        assert result == []

    def test_no_id_or_statement_deduplicates_by_empty_key(self):
        items = [{"foo": "bar"}, {"foo": "baz"}]
        result = rank_and_deduplicate(items)
        assert len(result) == 1
