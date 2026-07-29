import pytest

from ums.utils.embeddings import EmbeddingService


class FakeProvider:
    async def embed(self, texts: list[str], model: str) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]


@pytest.mark.asyncio
async def test_embed_returns_embeddings_for_texts():
    provider = FakeProvider()
    service = EmbeddingService(provider=provider, model="test-model")
    result = await service.embed(["hello", "world"])
    assert len(result) == 2
    assert all(len(vec) == 3 for vec in result)


@pytest.mark.asyncio
async def test_embed_one_returns_single_embedding():
    provider = FakeProvider()
    service = EmbeddingService(provider=provider, model="test-model")
    result = await service.embed_one("hello")
    assert result == [0.1, 0.2, 0.3]


@pytest.mark.asyncio
async def test_embed_one_returns_empty_on_empty_results():
    class EmptyProvider:
        async def embed(self, texts: list[str], model: str) -> list[list[float]]:
            return []

    service = EmbeddingService(provider=EmptyProvider(), model="test-model")
    result = await service.embed_one("hello")
    assert result == []
