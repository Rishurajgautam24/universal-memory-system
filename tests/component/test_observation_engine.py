from __future__ import annotations

import json
from typing import List, Optional
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from ums.llm.interface import LLMProvider, LLMResponse
from ums.models.observation import Observation, ObservationStage
from ums.observation.engine import ObservationEngine


class MockLLM(LLMProvider):
    def __init__(self) -> None:
        self._responses: list[LLMResponse] = []

    @property
    def name(self) -> str:
        return "mock"

    @property
    def default_model(self) -> str:
        return "mock-model"

    async def complete(
        self,
        messages: List,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        if self._responses:
            return self._responses.pop(0)
        return LLMResponse(
            content='[{"statement": "Test observation.", "confidence": 0.95, "category": "FACT"}]',
            model="mock-model",
            provider="mock",
        )

    async def embed(
        self, texts: List[str], model: Optional[str] = None
    ) -> List[List[float]]:
        return [[0.0] * 128 for _ in texts]


@pytest.fixture
def llm() -> MockLLM:
    return MockLLM()


@pytest.fixture
def storage():
    mock = AsyncMock()
    mock.enqueue = AsyncMock()
    return mock


A_CONVERSATION = (
    "I had a discussion with Alice about AI safety. "
    "She believes that artificial intelligence will transform healthcare. "
    "We also talked about the importance of regulation. "
    "Bob joined later and shared his views on open source AI models. "
    "The conversation lasted for about an hour."
)


class TestObservationEngine:
    async def test_process_creates_observations(
        self, llm: MockLLM, storage: AsyncMock
    ) -> None:
        engine = ObservationEngine(llm=llm, storage=storage)
        job_id = await engine.process(
            source="test", conversation=A_CONVERSATION, session_id="session-1"
        )
        assert isinstance(job_id, UUID)
        assert storage.enqueue.await_count > 0
        call_args = storage.enqueue.await_args_list[0].args[0]
        assert call_args.source == "test"
        assert call_args.session_id == "session-1"
        assert call_args.stage == ObservationStage.PROCESSED

    async def test_low_confidence_filtered(
        self, llm: MockLLM, storage: AsyncMock
    ) -> None:
        llm._responses = [
            LLMResponse(
                content=(
                    '[{"statement": "High confidence fact.", "confidence": 0.95,'
                    ' "category": "FACT"},'
                    ' {"statement": "Low confidence guess.", "confidence": 0.1,'
                    ' "category": "FACT"},'
                    ' {"statement": "Medium confidence claim.", "confidence": 0.5,'
                    ' "category": "FACT"}]'
                ),
                model="mock-model",
                provider="mock",
            )
        ]
        engine = ObservationEngine(llm=llm, storage=storage, min_confidence=0.4)
        await engine.process(
            source="test", conversation=A_CONVERSATION, session_id="session-2"
        )
        enqueued = [c[0][0] for c in storage.enqueue.await_args_list]
        statements = {o.statement for o in enqueued}
        assert "High confidence fact." in statements
        assert "Low confidence guess." not in statements
        assert "Medium confidence claim." in statements

    async def test_empty_conversation_raises(
        self, llm: MockLLM, storage: AsyncMock
    ) -> None:
        engine = ObservationEngine(llm=llm, storage=storage)
        with pytest.raises(ValueError, match="conversation is empty"):
            await engine.process(
                source="test", conversation="", session_id="session-3"
            )

    async def test_short_conversation_raises(
        self, llm: MockLLM, storage: AsyncMock
    ) -> None:
        engine = ObservationEngine(llm=llm, storage=storage)
        with pytest.raises(ValueError, match="conversation too short"):
            await engine.process(
                source="test", conversation="Hello world", session_id="session-4"
            )

    async def test_max_observations_respected(
        self, llm: MockLLM, storage: AsyncMock
    ) -> None:
        items = [
            {"statement": f"Fact {i}.", "confidence": 0.9, "category": "FACT"}
            for i in range(100)
        ]
        llm._responses = [
            LLMResponse(
                content=json.dumps(items),
                model="mock-model",
                provider="mock",
            )
        ]
        engine = ObservationEngine(llm=llm, storage=storage, max_observations=10)
        await engine.process(
            source="test", conversation=A_CONVERSATION, session_id="session-5"
        )
        assert storage.enqueue.await_count == 10
