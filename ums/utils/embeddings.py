from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ums.llm.interface import LLMProvider  # type: ignore[import-not-found]


class EmbeddingService:
    def __init__(self, provider: "LLMProvider", model: str):
        self._provider = provider
        self._model = model

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return await self._provider.embed(texts, model=self._model)

    async def embed_one(self, text: str) -> list[float]:
        results = await self._provider.embed([text], model=self._model)
        return results[0] if results else []
