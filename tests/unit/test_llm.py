import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ums.llm.interface import LLMMessage, LLMResponse, LLMProvider
from ums.llm.openrouter import OpenRouterProvider
from ums.llm.router import ModelRouter
from ums.llm.prompts import (
    entity_extraction_prompt,
    observation_extraction_prompt,
    relationship_extraction_prompt,
)
from ums.llm import create_llm_router


def test_llm_provider_cannot_be_instantiated():
    with pytest.raises(TypeError):
        LLMProvider()  # type: ignore[abstract]


class TestLLMMessage:
    def test_has_role_and_content(self):
        msg = LLMMessage(role="user", content="hello")
        assert msg.role == "user"
        assert msg.content == "hello"

    def test_model_dump(self):
        msg = LLMMessage(role="system", content="be helpful")
        data = msg.model_dump()
        assert data == {"role": "system", "content": "be helpful"}


class TestLLMResponse:
    def test_minimal(self):
        resp = LLMResponse(content="hi", model="gpt-4", provider="openrouter")
        assert resp.content == "hi"
        assert resp.model == "gpt-4"
        assert resp.provider == "openrouter"
        assert resp.usage is None

    def test_with_usage(self):
        resp = LLMResponse(
            content="hi", model="gpt-4", provider="openrouter", usage={"a": 1}
        )
        assert resp.usage == {"a": 1}


class TestOpenRouterProvider:
    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client.chat = MagicMock()
        client.chat.completions = MagicMock()
        client.chat.completions.create = AsyncMock()
        client.embeddings = MagicMock()
        client.embeddings.create = AsyncMock()
        return client

    @pytest.fixture
    def provider(self, mock_client):
        return OpenRouterProvider(client=mock_client)

    @pytest.mark.asyncio
    async def test_complete_basic(self, provider, mock_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello!"
        mock_response.usage = None
        mock_response.model = "gpt-4o-mini"
        mock_client.chat.completions.create.return_value = mock_response

        result = await provider.complete(
            messages=[LLMMessage(role="user", content="Say hi")]
        )
        assert result.content == "Hello!"
        assert result.model == "gpt-4o-mini"
        assert result.provider == "openrouter"
        assert result.usage is None

    @pytest.mark.asyncio
    async def test_complete_with_json_mode(self, provider, mock_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"key": "value"}'
        mock_response.usage = None
        mock_response.model = "gpt-4o-mini"
        mock_client.chat.completions.create.return_value = mock_response

        result = await provider.complete(
            messages=[LLMMessage(role="user", content="Return JSON")],
            json_mode=True,
        )
        assert result.content == '{"key": "value"}'
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["response_format"] == {"type": "json_object"}

    @pytest.mark.asyncio
    async def test_complete_with_max_tokens(self, provider, mock_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "short"
        mock_response.usage = None
        mock_response.model = "gpt-4o-mini"
        mock_client.chat.completions.create.return_value = mock_response

        await provider.complete(
            messages=[LLMMessage(role="user", content="Be brief")],
            max_tokens=10,
        )
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["max_tokens"] == 10

    @pytest.mark.asyncio
    async def test_embed(self, provider, mock_client):
        mock_response = MagicMock()
        mock_response.data = [MagicMock(), MagicMock()]
        mock_response.data[0].embedding = [0.1, 0.2, 0.3]
        mock_response.data[1].embedding = [0.4, 0.5, 0.6]
        mock_client.embeddings.create.return_value = mock_response

        result = await provider.embed(texts=["hello", "world"])
        assert result == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        mock_client.embeddings.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_complete_default_model(self, provider, mock_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "ok"
        mock_response.usage = None
        mock_response.model = "gpt-4o-mini"
        mock_client.chat.completions.create.return_value = mock_response

        await provider.complete(
            messages=[LLMMessage(role="user", content="test")]
        )
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == "openai/gpt-4o-mini"

    @pytest.mark.asyncio
    async def test_complete_custom_model(self, provider, mock_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "ok"
        mock_response.usage = None
        mock_response.model = "custom-model"
        mock_client.chat.completions.create.return_value = mock_response

        await provider.complete(
            messages=[LLMMessage(role="user", content="test")],
            model="custom-model",
        )
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == "custom-model"

    def test_name(self, provider):
        assert provider.name == "openrouter"

    def test_default_model(self, provider):
        assert provider.default_model == "openai/gpt-4o-mini"


class TestModelRouter:
    def test_provider_property(self):
        provider = MagicMock(spec=LLMProvider)
        router = ModelRouter(provider)
        assert router.provider is provider

    def test_get_returns_provider(self):
        provider = MagicMock(spec=LLMProvider)
        router = ModelRouter(provider)
        assert router.get("extraction") is provider

    def test_get_any_task_same_provider(self):
        provider = MagicMock(spec=LLMProvider)
        router = ModelRouter(provider)
        assert router.get("synthesis") is provider
        assert router.get("embedding") is provider


class TestPrompts:
    def test_entity_extraction_prompt(self):
        messages = entity_extraction_prompt("Alice met Bob")
        assert len(messages) == 2
        assert messages[0].role == "system"
        assert "entity" in messages[0].content.lower()
        assert messages[1].role == "user"
        assert messages[1].content == "Alice met Bob"

    def test_observation_extraction_prompt(self):
        messages = observation_extraction_prompt("Alice is a developer")
        assert len(messages) == 2
        assert messages[0].role == "system"
        assert "observation" in messages[0].content.lower()
        assert messages[1].content == "Alice is a developer"

    def test_relationship_extraction_prompt(self):
        messages = relationship_extraction_prompt("Alice works with Bob")
        assert len(messages) == 2
        assert messages[0].role == "system"
        assert "relationship" in messages[0].content.lower()
        assert messages[1].content == "Alice works with Bob"

    def test_prompt_messages_are_llmmessage(self):
        for prompt_fn in [
            entity_extraction_prompt,
            observation_extraction_prompt,
            relationship_extraction_prompt,
        ]:
            messages = prompt_fn("test")
            for m in messages:
                assert isinstance(m, LLMMessage)


class TestCreateLLMRouter:
    def test_returns_model_router(self):
        provider = MagicMock(spec=LLMProvider)
        router = create_llm_router(provider=provider)
        assert isinstance(router, ModelRouter)

    def test_uses_provided_provider(self):
        provider = MagicMock(spec=LLMProvider)
        provider.name = "test-provider"
        router = create_llm_router(provider=provider)
        assert router.provider.name == "test-provider"

    def test_default_creates_openrouter_provider(self):
        with patch("ums.llm.OpenRouterProvider") as mock_cls:
            create_llm_router()
            mock_cls.assert_called_once()
