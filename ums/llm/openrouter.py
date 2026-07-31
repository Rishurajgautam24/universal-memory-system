
from openai import AsyncOpenAI

from ums.config import settings
from ums.llm.interface import LLMMessage, LLMProvider, LLMResponse


class OpenRouterProvider(LLMProvider):
    def __init__(self, client: AsyncOpenAI | None = None):
        self._client = client or AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
        )

    @property
    def name(self) -> str:
        return "openrouter"

    @property
    def default_model(self) -> str:
        return settings.extraction_model

    async def complete(
        self,
        messages: list[LLMMessage],
        model: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        kwargs = dict(
            model=model or self.default_model,
            messages=[m.model_dump() for m in messages],
            temperature=temperature,
        )
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        response = await self._client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        return LLMResponse(
            content=choice.message.content or "",
            usage=response.usage.model_dump() if response.usage else None,
            model=response.model,
            provider=self.name,
        )

    async def embed(
        self, texts: list[str], model: str | None = None
    ) -> list[list[float]]:
        model = model or settings.embedding_model
        response = await self._client.embeddings.create(model=model, input=texts)
        return [d.embedding for d in response.data]
