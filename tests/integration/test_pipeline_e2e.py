from __future__ import annotations

import pytest
from httpx import AsyncClient


class TestPipelineE2E:
    async def test_observe_returns_job_id(self, client: AsyncClient):
        resp = await client.post(
            "/v1/observe",
            json={
                "source": "Test",
                "conversation": "I'm building UMS. I prefer Python for backend development and testing.",
                "metadata": {"project": "UMS"},
            },
            headers={"Authorization": "Bearer test-key"},
        )
        assert resp.status_code == 202
        data = resp.json()
        assert data["ok"] is True
        assert "job_id" in data["data"]
        assert data["data"]["status"] == "queued"

    async def test_recall_returns_context(self, client: AsyncClient):
        resp = await client.post(
            "/v1/recall",
            json={"task": "Help with UMS"},
            headers={"Authorization": "Bearer test-key"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert "context" in data["data"]
        assert "retrieval_metadata" in data["data"]

    async def test_health_endpoint(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["database"] == "connected"

    async def test_auth_error(self, client: AsyncClient):
        resp = await client.post(
            "/v1/observe",
            json={"source": "T", "conversation": "test conversation with enough words for processing"},
        )
        assert resp.status_code == 401
        data = resp.json()
        assert data["ok"] is False
        assert data["error"] == "unauthorized"

    async def test_empty_recall_graceful(self, client: AsyncClient):
        resp = await client.post(
            "/v1/recall",
            json={"task": "unknown project"},
            headers={"Authorization": "Bearer test-key"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert len(data["data"]["context"]["relevant_beliefs"]) == 0

    async def test_timeline_empty(self, client: AsyncClient):
        resp = await client.get(
            "/v1/timeline",
            headers={"Authorization": "Bearer test-key"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["data"]["events"] == []
        assert data["data"]["pagination"]["total"] == 0
