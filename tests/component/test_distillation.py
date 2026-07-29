from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from ums.distillation.pipeline import DistillationPipeline
from ums.models.candidate import CandidateStatus, MemoryCandidate
from ums.models.distillation import CycleStatus
from ums.models.observation import Observation


@pytest.fixture
def storage():
    mock = AsyncMock()
    mock.dequeue_batch = AsyncMock(return_value=[])
    mock.mark_processed = AsyncMock()
    return mock


@pytest.fixture
def memory_engine():
    mock = AsyncMock()
    mock.process_observation = AsyncMock()
    return mock


@pytest.fixture
def pipeline(storage, memory_engine):
    return DistillationPipeline(storage, memory_engine, batch_size=5)


def _make_obs(statement: str = "test") -> Observation:
    return Observation(
        id=uuid4(),
        source="test",
        session_id="test-session",
        raw_text=statement,
        statement=statement,
        confidence=0.9,
    )


def _make_candidate(status: CandidateStatus = CandidateStatus.ACCUMULATING) -> MemoryCandidate:
    return MemoryCandidate(
        id=uuid4(),
        statement="test",
        confidence=0.9,
        status=status,
    )


class TestDistillationPipeline:
    async def test_empty_queue(self, pipeline, storage, memory_engine) -> None:
        cycle = await pipeline.run()
        assert cycle.status == CycleStatus.COMPLETED
        assert cycle.observations_read == 0
        assert cycle.candidates_promoted == 0
        assert cycle.candidates_created == 0
        assert cycle.summary == "Processed 0 obs: 0 created, 0 promoted"
        storage.dequeue_batch.assert_awaited_once_with(5)

    async def test_single_observation_promoted(self, pipeline, storage, memory_engine) -> None:
        obs = _make_obs()
        storage.dequeue_batch.return_value = [obs]
        candidate = _make_candidate(CandidateStatus.PROMOTED)
        memory_engine.process_observation.return_value = candidate

        cycle = await pipeline.run()

        assert cycle.observations_read == 1
        assert cycle.candidates_promoted == 1
        assert cycle.candidates_created == 0
        memory_engine.process_observation.assert_awaited_once_with(obs)
        storage.mark_processed.assert_awaited_once_with(obs.id)

    async def test_single_observation_accumulating(self, pipeline, storage, memory_engine) -> None:
        obs = _make_obs()
        storage.dequeue_batch.return_value = [obs]
        candidate = _make_candidate(CandidateStatus.ACCUMULATING)
        memory_engine.process_observation.return_value = candidate

        cycle = await pipeline.run()

        assert cycle.observations_read == 1
        assert cycle.candidates_promoted == 0
        assert cycle.candidates_created == 1

    async def test_multiple_observations(self, pipeline, storage, memory_engine) -> None:
        obs_a = _make_obs("a")
        obs_b = _make_obs("b")
        storage.dequeue_batch.return_value = [obs_a, obs_b]
        memory_engine.process_observation.side_effect = [
            _make_candidate(CandidateStatus.PROMOTED),
            _make_candidate(CandidateStatus.ACCUMULATING),
        ]

        cycle = await pipeline.run()

        assert cycle.observations_read == 2
        assert cycle.candidates_promoted == 1
        assert cycle.candidates_created == 1
        assert storage.mark_processed.await_count == 2

    async def test_skip_when_no_candidate_returned(self, pipeline, storage, memory_engine) -> None:
        obs = _make_obs()
        storage.dequeue_batch.return_value = [obs]
        memory_engine.process_observation.return_value = None

        cycle = await pipeline.run()

        assert cycle.observations_read == 1
        assert cycle.candidates_promoted == 0
        assert cycle.candidates_created == 0

    async def test_error_in_processing_continues(self, pipeline, storage, memory_engine) -> None:
        obs_a = _make_obs("a")
        obs_b = _make_obs("b")
        storage.dequeue_batch.return_value = [obs_a, obs_b]
        memory_engine.process_observation.side_effect = [
            Exception("processing error"),
            _make_candidate(CandidateStatus.ACCUMULATING),
        ]

        cycle = await pipeline.run()

        assert cycle.observations_read == 2
        assert cycle.candidates_created == 1
        assert len(cycle.errors) == 1
        assert "processing error" in cycle.errors[0]
        assert cycle.status == CycleStatus.COMPLETED

    async def test_batch_size_passed_to_storage(self, pipeline, storage, memory_engine) -> None:
        custom_pipeline = DistillationPipeline(storage, memory_engine, batch_size=20)
        await custom_pipeline.run()
        storage.dequeue_batch.assert_awaited_once_with(20)

    async def test_dequeue_failure_sets_failed(self, pipeline, storage, memory_engine) -> None:
        storage.dequeue_batch.side_effect = Exception("dequeue failed")
        cycle = await pipeline.run()
        assert cycle.status == CycleStatus.FAILED
        assert len(cycle.errors) == 1
        assert "dequeue failed" in cycle.errors[0]
