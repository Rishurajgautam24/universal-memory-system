import pytest

from ums.utils.similarity import cosine_similarity


def test_identical_vectors():
    a = [1.0, 2.0, 3.0]
    assert cosine_similarity(a, a) == pytest.approx(1.0)


def test_orthogonal_vectors():
    a = [1.0, 0.0]
    b = [0.0, 1.0]
    assert cosine_similarity(a, b) == pytest.approx(0.0)


def test_opposite_vectors():
    a = [1.0, 2.0]
    b = [-1.0, -2.0]
    assert cosine_similarity(a, b) == pytest.approx(-1.0)


def test_zero_vector_returns_zero():
    a = [1.0, 2.0]
    b = [0.0, 0.0]
    assert cosine_similarity(a, b) == 0.0
    assert cosine_similarity(b, a) == 0.0
