from __future__ import annotations

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from ums.gateway.app import AppContext, create_app


@pytest.fixture
def mock_ctx():
    ctx = AppContext(
        storage=AsyncMock(),
        llm=AsyncMock(),
        observation_engine=AsyncMock(),
        memory_engine=AsyncMock(),
        recall_engine=AsyncMock(),
        distillation_pipeline=AsyncMock(),
    )
    ctx.storage.initialize = AsyncMock()
    ctx.storage.close = AsyncMock()
    ctx.storage.health_check = AsyncMock(return_value=True)
    ctx.storage.get_events = AsyncMock(return_value=[])
    ctx.storage.count_events = AsyncMock(return_value=0)
    ctx.observation_engine.process = AsyncMock(return_value=uuid4())
    ctx.recall_engine.recall = AsyncMock(
        return_value={
            "context": {"identity_summary": "test", "relevant_beliefs": []},
            "retrieval_metadata": {"stages_used": [], "returned": 0},
        }
    )
    return ctx


@pytest.fixture
async def client(mock_ctx):
    app = create_app()
    with patch("ums.gateway.app.app_ctx", mock_ctx):
        with patch("ums.gateway.app.get_ctx", return_value=mock_ctx):
            async with LifespanManager(app):
                transport = ASGITransport(app=app)
                async with AsyncClient(
                    transport=transport, base_url="http://test"
                ) as c:
                    yield c
