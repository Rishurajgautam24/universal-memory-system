from __future__ import annotations

from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

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
def client(mock_ctx):
    with patch("ums.gateway.app.app_ctx", mock_ctx):
        with patch("ums.gateway.app.get_ctx", return_value=mock_ctx):
            app = create_app()
            with TestClient(app) as c:
                yield c


class TestHealth:
    def test_health_ok(self, client: TestClient):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["database"] == "connected"

    def test_health_no_auth_required(self, client: TestClient):
        resp = client.get("/health", headers={})
        assert resp.status_code == 200


class TestAuth:
    def test_missing_auth_header(self, client: TestClient):
        resp = client.post("/v1/observe", json={})
        assert resp.status_code == 401
        data = resp.json()
        assert data["ok"] is False
        assert data["error"] == "unauthorized"

    def test_empty_token(self, client: TestClient):
        resp = client.post(
            "/v1/observe", json={}, headers={"Authorization": "Bearer "}
        )
        assert resp.status_code == 401

    def test_invalid_scheme(self, client: TestClient):
        resp = client.post(
            "/v1/observe", json={}, headers={"Authorization": "Basic token"}
        )
        assert resp.status_code == 401

    def test_valid_token_accepted(self, client: TestClient):
        resp = client.post(
            "/v1/observe",
            json={"source": "test", "conversation": "Hello world this is a test conversation with enough words"},
            headers={"Authorization": "Bearer any-token"},
        )
        assert resp.status_code == 202


class TestObserve:
    def test_success(self, client: TestClient, mock_ctx):
        job_id = uuid4()
        mock_ctx.observation_engine.process.return_value = job_id
        resp = client.post(
            "/v1/observe",
            json={
                "source": "Claude",
                "conversation": "Hello world this is a test conversation with enough words for processing",
                "metadata": {"session_id": "sess-1"},
            },
            headers={"Authorization": "Bearer test-key"},
        )
        assert resp.status_code == 202
        data = resp.json()
        assert data["ok"] is True
        assert data["data"]["job_id"] == str(job_id)
        assert data["data"]["status"] == "queued"

    def test_missing_source(self, client: TestClient):
        resp = client.post(
            "/v1/observe",
            json={"source": "", "conversation": "test"},
            headers={"Authorization": "Bearer test-key"},
        )
        assert resp.status_code == 422
        data = resp.json()
        assert data["ok"] is False

    def test_empty_conversation(self, client: TestClient):
        resp = client.post(
            "/v1/observe",
            json={"source": "test", "conversation": ""},
            headers={"Authorization": "Bearer test-key"},
        )
        assert resp.status_code == 422

    def test_validation_error_from_engine(self, client: TestClient, mock_ctx):
        mock_ctx.observation_engine.process.side_effect = ValueError("too short")
        resp = client.post(
            "/v1/observe",
            json={
                "source": "test",
                "conversation": "short",
            },
            headers={"Authorization": "Bearer test-key"},
        )
        assert resp.status_code == 422


class TestRecall:
    def test_success(self, client: TestClient):
        resp = client.post(
            "/v1/recall",
            json={"task": "review my code"},
            headers={"Authorization": "Bearer test-key"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert "context" in data["data"]
        assert "retrieval_metadata" in data["data"]

    def test_empty_task(self, client: TestClient):
        resp = client.post(
            "/v1/recall",
            json={"task": ""},
            headers={"Authorization": "Bearer test-key"},
        )
        assert resp.status_code == 422

    def test_with_context_and_options(self, client: TestClient, mock_ctx):
        resp = client.post(
            "/v1/recall",
            json={
                "task": "review my code",
                "context": {"project": "UMS", "focus": ["beliefs"]},
                "options": {"max_tokens": 1000},
            },
            headers={"Authorization": "Bearer test-key"},
        )
        assert resp.status_code == 200
        mock_ctx.recall_engine.recall.assert_called_once_with(
            task="review my code",
            context={"project": "UMS", "focus": ["beliefs"]},
            options={"max_tokens": 1000},
        )


class TestSearch:
    def test_returns_empty(self, client: TestClient):
        resp = client.post(
            "/v1/search",
            json={"query": "test"},
            headers={"Authorization": "Bearer test-key"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["data"]["results"] == []
        assert data["data"]["total"] == 0


class TestTimeline:
    def test_empty_timeline(self, client: TestClient):
        resp = client.get(
            "/v1/timeline",
            headers={"Authorization": "Bearer test-key"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["data"]["events"] == []
        assert data["data"]["pagination"]["total"] == 0

    def test_with_events(self, client: TestClient, mock_ctx):
        from ums.models.timeline import EventType, TimelineEvent
        from ums.utils.datetime import now_utc

        ev = TimelineEvent(
            id=uuid4(),
            event_type=EventType.OBSERVATION,
            object_id=uuid4(),
            object_type="observation",
            description="test event",
            confidence=0.9,
            created_at=now_utc().isoformat().replace("+00:00", "Z"),
        )
        mock_ctx.storage.get_events.return_value = [ev]
        mock_ctx.storage.count_events.return_value = 1
        resp = client.get(
            "/v1/timeline?limit=10&page=1",
            headers={"Authorization": "Bearer test-key"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]["events"]) == 1
        assert data["data"]["events"][0]["what"] == "test event"
        assert data["data"]["pagination"]["total"] == 1

    def test_pagination(self, client: TestClient, mock_ctx):
        mock_ctx.storage.count_events.return_value = 100
        resp = client.get(
            "/v1/timeline?limit=10&page=1",
            headers={"Authorization": "Bearer test-key"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["pagination"]["page"] == 1
        assert data["data"]["pagination"]["limit"] == 10
        assert data["data"]["pagination"]["has_more"] is True

    def test_invalid_limit(self, client: TestClient):
        resp = client.get(
            "/v1/timeline?limit=0",
            headers={"Authorization": "Bearer test-key"},
        )
        assert resp.status_code == 422


class TestExplain:
    def test_returns_stub(self, client: TestClient):
        resp = client.post(
            "/v1/explain",
            json={"target_id": str(uuid4()), "target_type": "belief"},
            headers={"Authorization": "Bearer test-key"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["data"]["target"] is None


class TestReflect:
    def test_returns_not_implemented(self, client: TestClient):
        resp = client.post(
            "/v1/reflect",
            json={},
            headers={"Authorization": "Bearer test-key"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["data"]["status"] == "not_implemented"


class TestRateLimit:
    def test_rate_limit_headers(self, client: TestClient):
        resp = client.post(
            "/v1/observe",
            json={"source": "test", "conversation": "X" * 50},
            headers={"Authorization": "Bearer test-key"},
        )
        assert resp.status_code == 202
        assert "X-RateLimit-Limit" in resp.headers
        assert "X-RateLimit-Remaining" in resp.headers
        assert "X-RateLimit-Reset" in resp.headers


class TestErrorHandling:
    def test_ums_exception_returns_envelope(self, client: TestClient):
        resp = client.post(
            "/v1/observe",
            json={"source": "", "conversation": "test"},
            headers={"Authorization": "Bearer test-key"},
        )
        assert resp.status_code == 422
        data = resp.json()
        assert data["ok"] is False
        assert data["error"] == "validation_error"
        assert "meta" in data
