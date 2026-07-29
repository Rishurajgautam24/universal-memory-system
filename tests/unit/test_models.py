from uuid import UUID, uuid4

import pytest

from ums.models.audit import AuditAction, AuditLogEntry
from ums.models.candidate import CandidateStatus, MemoryCandidate
from ums.models.observation import Observation, ObservationCategory, ObservationStage
from ums.models.verified_memory import MemoryStatus, VerifiedMemory


class TestObservation:
    def test_create_minimal(self):
        obs = Observation(
            source="Claude", session_id="s-1", raw_text="text", statement="User builds UMS", confidence=0.85
        )
        assert isinstance(obs.id, UUID)
        assert obs.stage == ObservationStage.PENDING

    def test_confidence_bounds(self):
        with pytest.raises(ValueError):
            Observation(source="T", session_id="s", raw_text="x", statement="x", confidence=1.5)


class TestMemoryCandidate:
    def test_accumulating_by_default(self):
        c = MemoryCandidate(statement="x", confidence=0.5)
        assert c.status == CandidateStatus.ACCUMULATING


class TestVerifiedMemory:
    def test_links_to_candidate(self):
        m = VerifiedMemory(statement="x", confidence=0.85, source_candidate_id=uuid4())
        assert m.status == MemoryStatus.ACTIVE
        assert m.version == 1


class TestAuditLogEntry:
    def test_create(self):
        e = AuditLogEntry(action=AuditAction.CREATE, object_type="test", object_id=uuid4(), actor="test")
        assert e.id is not None
