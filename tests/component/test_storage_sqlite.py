from __future__ import annotations

import pytest

from ums.models.audit import AuditAction, AuditLogEntry
from ums.models.belief import Belief
from ums.models.candidate import CandidateStatus, MemoryCandidate
from ums.models.entity import Entity, EntityType
from ums.models.identity import Identity
from ums.models.project import Project
from ums.models.relationship import Relationship
from ums.models.timeline import EventType, TimelineEvent
from ums.models.verified_memory import MemoryStatus, VerifiedMemory
from ums.storage.sqlite.audit import SQLiteAuditLog
from ums.storage.sqlite.connection import DatabaseManager
from ums.storage.sqlite.graph import SQLiteGraphStore
from ums.storage.sqlite.timeline import SQLiteTimelineStore


@pytest.fixture
async def db():
    manager = DatabaseManager("sqlite+aiosqlite://")
    await manager.initialize()
    yield manager
    await manager.close()


@pytest.fixture
async def graph_store(db):
    store = SQLiteGraphStore(db)
    return store


@pytest.fixture
async def timeline_store(db):
    store = SQLiteTimelineStore(db)
    return store


@pytest.fixture
async def audit_store(db):
    store = SQLiteAuditLog(db)
    return store


# --- Entity ---


class TestEntityCRUD:
    async def test_create_and_get_entity(self, graph_store: SQLiteGraphStore):
        entity = Entity(name="Test", entity_type=EntityType.CONCEPT, confidence=0.95)
        created = await graph_store.create_entity(entity)
        assert created.id == entity.id

        fetched = await graph_store.get_entity(entity.id)
        assert fetched is not None
        assert fetched.name == "Test"
        assert fetched.entity_type == EntityType.CONCEPT
        assert fetched.confidence == 0.95

    async def test_get_entity_not_found(self, graph_store: SQLiteGraphStore):
        from uuid import uuid4

        result = await graph_store.get_entity(uuid4())
        assert result is None

    async def test_update_entity(self, graph_store: SQLiteGraphStore):
        entity = Entity(name="Original", entity_type=EntityType.PERSON, confidence=0.8)
        await graph_store.create_entity(entity)
        entity.name = "Updated"
        entity.confidence = 0.95
        updated = await graph_store.update_entity(entity)
        assert updated.name == "Updated"
        assert updated.confidence == 0.95

        fetched = await graph_store.get_entity(entity.id)
        assert fetched is not None
        assert fetched.name == "Updated"

    async def test_delete_entity(self, graph_store: SQLiteGraphStore):
        entity = Entity(name="DeleteMe", entity_type=EntityType.OTHER, confidence=0.5)
        await graph_store.create_entity(entity)
        await graph_store.delete_entity(entity.id)
        fetched = await graph_store.get_entity(entity.id)
        assert fetched is None

    async def test_entity_with_aliases(self, graph_store: SQLiteGraphStore):
        entity = Entity(
            name="Multi",
            entity_type=EntityType.PERSON,
            confidence=0.9,
            aliases=["Alias1", "Alias2"],
        )
        await graph_store.create_entity(entity)
        fetched = await graph_store.get_entity(entity.id)
        assert fetched is not None
        assert fetched.aliases == ["Alias1", "Alias2"]

    async def test_entity_with_description(self, graph_store: SQLiteGraphStore):
        entity = Entity(
            name="Described",
            entity_type=EntityType.CONCEPT,
            confidence=0.7,
            description="A test description",
        )
        await graph_store.create_entity(entity)
        fetched = await graph_store.get_entity(entity.id)
        assert fetched is not None
        assert fetched.description == "A test description"

    async def test_entity_without_description(self, graph_store: SQLiteGraphStore):
        entity = Entity(name="NoDesc", entity_type=EntityType.CONCEPT, confidence=0.7)
        await graph_store.create_entity(entity)
        fetched = await graph_store.get_entity(entity.id)
        assert fetched is not None
        assert fetched.description is None


# --- Relationship ---


class TestRelationshipCRUD:
    async def test_create_and_get_relationship(self, graph_store: SQLiteGraphStore):
        from uuid import uuid4

        rel = Relationship(
            source_entity_id=uuid4(),
            target_entity_id=uuid4(),
            relation_type="knows",
            confidence=0.9,
        )
        created = await graph_store.create_relationship(rel)
        assert created.id == rel.id

        fetched = await graph_store.get_relationship(rel.id)
        assert fetched is not None
        assert fetched.relation_type == "knows"
        assert fetched.confidence == 0.9

    async def test_update_relationship(self, graph_store: SQLiteGraphStore):
        from uuid import uuid4

        rel = Relationship(
            source_entity_id=uuid4(),
            target_entity_id=uuid4(),
            relation_type="knows",
            confidence=0.8,
        )
        await graph_store.create_relationship(rel)
        rel.relation_type = "works_with"
        rel.confidence = 0.95
        await graph_store.update_relationship(rel)

        fetched = await graph_store.get_relationship(rel.id)
        assert fetched is not None
        assert fetched.relation_type == "works_with"
        assert fetched.confidence == 0.95

    async def test_delete_relationship(self, graph_store: SQLiteGraphStore):
        from uuid import uuid4

        rel = Relationship(
            source_entity_id=uuid4(),
            target_entity_id=uuid4(),
            relation_type="knows",
            confidence=0.8,
        )
        await graph_store.create_relationship(rel)
        await graph_store.delete_relationship(rel.id)
        fetched = await graph_store.get_relationship(rel.id)
        assert fetched is None


# --- VerifiedMemory ---


class TestVerifiedMemoryCRUD:
    async def test_create_and_get(self, graph_store: SQLiteGraphStore):
        mem = VerifiedMemory(statement="Test memory", confidence=0.95)
        created = await graph_store.create_verified_memory(mem)
        assert created.id == mem.id

        fetched = await graph_store.get_verified_memory(mem.id)
        assert fetched is not None
        assert fetched.statement == "Test memory"
        assert fetched.status == MemoryStatus.ACTIVE

    async def test_update(self, graph_store: SQLiteGraphStore):
        mem = VerifiedMemory(statement="Original", confidence=0.8)
        await graph_store.create_verified_memory(mem)
        mem.statement = "Updated"
        mem.status = MemoryStatus.ARCHIVED
        await graph_store.update_verified_memory(mem)

        fetched = await graph_store.get_verified_memory(mem.id)
        assert fetched is not None
        assert fetched.statement == "Updated"
        assert fetched.status == MemoryStatus.ARCHIVED

    async def test_delete(self, graph_store: SQLiteGraphStore):
        mem = VerifiedMemory(statement="Delete me", confidence=0.9)
        await graph_store.create_verified_memory(mem)
        await graph_store.delete_verified_memory(mem.id)
        fetched = await graph_store.get_verified_memory(mem.id)
        assert fetched is None

    async def test_with_source_candidate(self, graph_store: SQLiteGraphStore):
        from uuid import uuid4

        cid = uuid4()
        mem = VerifiedMemory(
            statement="From candidate",
            confidence=0.85,
            source_candidate_id=cid,
        )
        await graph_store.create_verified_memory(mem)
        fetched = await graph_store.get_verified_memory(mem.id)
        assert fetched is not None
        assert fetched.source_candidate_id == cid

    async def test_superseded(self, graph_store: SQLiteGraphStore):
        from uuid import uuid4

        sid = uuid4()
        mem = VerifiedMemory(
            statement="Superseded",
            confidence=0.7,
            status=MemoryStatus.SUPERSEDED,
            superseded_by=sid,
        )
        await graph_store.create_verified_memory(mem)
        fetched = await graph_store.get_verified_memory(mem.id)
        assert fetched is not None
        assert fetched.superseded_by == sid
        assert fetched.status == MemoryStatus.SUPERSEDED


# --- Belief ---


class TestBeliefCRUD:
    async def test_create_and_get(self, graph_store: SQLiteGraphStore):
        belief = Belief(statement="Test belief", confidence=0.9)
        created = await graph_store.create_belief(belief)
        assert created.id == belief.id

        fetched = await graph_store.get_belief(belief.id)
        assert fetched is not None
        assert fetched.statement == "Test belief"

    async def test_with_lists(self, graph_store: SQLiteGraphStore):
        from uuid import uuid4

        supporting = [uuid4(), uuid4()]
        contradicting = [uuid4()]
        belief = Belief(
            statement="Complex belief",
            confidence=0.85,
            supporting_memory_ids=supporting,
            contradicting_memory_ids=contradicting,
        )
        await graph_store.create_belief(belief)
        fetched = await graph_store.get_belief(belief.id)
        assert fetched is not None
        assert len(fetched.supporting_memory_ids) == 2
        assert len(fetched.contradicting_memory_ids) == 1

    async def test_update(self, graph_store: SQLiteGraphStore):
        belief = Belief(statement="Original belief", confidence=0.8)
        await graph_store.create_belief(belief)
        belief.statement = "Updated belief"
        belief.confidence = 0.95
        await graph_store.update_belief(belief)

        fetched = await graph_store.get_belief(belief.id)
        assert fetched is not None
        assert fetched.statement == "Updated belief"
        assert fetched.confidence == 0.95

    async def test_delete(self, graph_store: SQLiteGraphStore):
        belief = Belief(statement="Temp belief", confidence=0.5)
        await graph_store.create_belief(belief)
        await graph_store.delete_belief(belief.id)
        fetched = await graph_store.get_belief(belief.id)
        assert fetched is None


# --- Candidate ---


class TestCandidateCRUD:
    async def test_create_and_get(self, graph_store: SQLiteGraphStore):
        cand = MemoryCandidate(statement="Test candidate", confidence=0.9)
        created = await graph_store.create_candidate(cand)
        assert created.id == cand.id

        fetched = await graph_store.get_candidate(cand.id)
        assert fetched is not None
        assert fetched.statement == "Test candidate"

    async def test_with_observation_ids(self, graph_store: SQLiteGraphStore):
        from uuid import uuid4

        obs_ids = [uuid4(), uuid4()]
        cand = MemoryCandidate(
            statement="With observations",
            confidence=0.8,
            observation_ids=obs_ids,
        )
        await graph_store.create_candidate(cand)
        fetched = await graph_store.get_candidate(cand.id)
        assert fetched is not None
        assert len(fetched.observation_ids) == 2

    async def test_update(self, graph_store: SQLiteGraphStore):
        cand = MemoryCandidate(statement="Original", confidence=0.7)
        await graph_store.create_candidate(cand)
        cand.statement = "Updated"
        cand.status = CandidateStatus.CORROBORATED
        await graph_store.update_candidate(cand)

        fetched = await graph_store.get_candidate(cand.id)
        assert fetched is not None
        assert fetched.statement == "Updated"
        assert fetched.status == CandidateStatus.CORROBORATED

    async def test_delete(self, graph_store: SQLiteGraphStore):
        cand = MemoryCandidate(statement="Temp", confidence=0.5)
        await graph_store.create_candidate(cand)
        await graph_store.delete_candidate(cand.id)
        fetched = await graph_store.get_candidate(cand.id)
        assert fetched is None


# --- Identity ---


class TestIdentityCRUD:
    async def test_create_and_get(self, graph_store: SQLiteGraphStore):
        identity = Identity(name="TestUser", confidence=0.9)
        created = await graph_store.create_identity(identity)
        assert created.id == identity.id

        fetched = await graph_store.get_identity(identity.id)
        assert fetched is not None
        assert fetched.name == "TestUser"

    async def test_update(self, graph_store: SQLiteGraphStore):
        identity = Identity(name="OldName", confidence=0.8)
        await graph_store.create_identity(identity)
        identity.name = "NewName"
        identity.confidence = 0.95
        await graph_store.update_identity(identity)

        fetched = await graph_store.get_identity(identity.id)
        assert fetched is not None
        assert fetched.name == "NewName"

    async def test_delete(self, graph_store: SQLiteGraphStore):
        identity = Identity(name="DelUser", confidence=0.5)
        await graph_store.create_identity(identity)
        await graph_store.delete_identity(identity.id)
        fetched = await graph_store.get_identity(identity.id)
        assert fetched is None


# --- Project ---


class TestProjectCRUD:
    async def test_create_and_get(self, graph_store: SQLiteGraphStore):
        project = Project(name="TestProj", confidence=0.9)
        created = await graph_store.create_project(project)
        assert created.id == project.id

        fetched = await graph_store.get_project(project.id)
        assert fetched is not None
        assert fetched.name == "TestProj"

    async def test_with_description(self, graph_store: SQLiteGraphStore):
        project = Project(name="DescProj", confidence=0.8, description="A project")
        await graph_store.create_project(project)
        fetched = await graph_store.get_project(project.id)
        assert fetched is not None
        assert fetched.description == "A project"

    async def test_update(self, graph_store: SQLiteGraphStore):
        project = Project(name="Old", confidence=0.7)
        await graph_store.create_project(project)
        project.name = "New"
        project.confidence = 0.95
        await graph_store.update_project(project)

        fetched = await graph_store.get_project(project.id)
        assert fetched is not None
        assert fetched.name == "New"

    async def test_delete(self, graph_store: SQLiteGraphStore):
        project = Project(name="DelProj", confidence=0.5)
        await graph_store.create_project(project)
        await graph_store.delete_project(project.id)
        fetched = await graph_store.get_project(project.id)
        assert fetched is None


# --- Timeline ---


class TestTimeline:
    async def test_append_and_count(self, timeline_store: SQLiteTimelineStore):
        from uuid import uuid4

        event = TimelineEvent(
            event_type=EventType.SYSTEM,
            object_id=uuid4(),
            object_type="test",
            description="Test event",
            confidence=1.0,
        )
        created = await timeline_store.append_event(event)
        assert created.id == event.id

        count = await timeline_store.count_events()
        assert count == 1

    async def test_multiple_events(self, timeline_store: SQLiteTimelineStore):
        from uuid import uuid4

        events = []
        for i in range(5):
            ev = TimelineEvent(
                event_type=EventType.SYSTEM,
                object_id=uuid4(),
                object_type="test",
                description=f"Event {i}",
                confidence=1.0,
            )
            await timeline_store.append_event(ev)
            events.append(ev)

        count = await timeline_store.count_events()
        assert count == 5

    async def test_get_events_pagination(self, timeline_store: SQLiteTimelineStore):
        from uuid import uuid4

        for i in range(10):
            ev = TimelineEvent(
                event_type=EventType.SYSTEM,
                object_id=uuid4(),
                object_type="test",
                description=f"Event {i}",
                confidence=1.0,
            )
            await timeline_store.append_event(ev)

        page1 = await timeline_store.get_events(limit=3, offset=0)
        assert len(page1) == 3

        page2 = await timeline_store.get_events(limit=3, offset=3)
        assert len(page2) == 3

        all_ids = {e.id for e in page1} | {e.id for e in page2}
        assert len(all_ids) == 6

    async def test_events_ordered_by_date(self, timeline_store: SQLiteTimelineStore):
        from uuid import uuid4

        ev1 = TimelineEvent(
            event_type=EventType.SYSTEM,
            object_id=uuid4(),
            object_type="test",
            description="First",
            confidence=1.0,
            created_at="2024-01-01T00:00:00Z",
        )
        ev2 = TimelineEvent(
            event_type=EventType.SYSTEM,
            object_id=uuid4(),
            object_type="test",
            description="Second",
            confidence=1.0,
            created_at="2024-01-02T00:00:00Z",
        )
        await timeline_store.append_event(ev1)
        await timeline_store.append_event(ev2)

        events = await timeline_store.get_events(limit=10)
        assert events[0].description == "Second"
        assert events[1].description == "First"


# --- Audit Log ---


class TestAuditLog:
    async def test_append_and_get_logs(self, audit_store: SQLiteAuditLog):
        from uuid import uuid4

        entry = AuditLogEntry(
            action=AuditAction.CREATE,
            object_type="entity",
            object_id=uuid4(),
            actor="test",
        )
        created = await audit_store.append(entry)
        assert created.id == entry.id

        logs = await audit_store.get_logs(limit=10)
        assert len(logs) == 1
        assert logs[0].action == AuditAction.CREATE

    async def test_multiple_logs(self, audit_store: SQLiteAuditLog):
        from uuid import uuid4

        for i in range(5):
            entry = AuditLogEntry(
                action=AuditAction.CREATE,
                object_type="test",
                object_id=uuid4(),
                actor=f"actor_{i}",
            )
            await audit_store.append(entry)

        logs = await audit_store.get_logs(limit=10)
        assert len(logs) == 5

    async def test_log_pagination(self, audit_store: SQLiteAuditLog):
        from uuid import uuid4

        for i in range(10):
            entry = AuditLogEntry(
                action=AuditAction.CREATE,
                object_type="test",
                object_id=uuid4(),
                actor=f"actor_{i}",
            )
            await audit_store.append(entry)

        page1 = await audit_store.get_logs(limit=3, offset=0)
        assert len(page1) == 3

        page2 = await audit_store.get_logs(limit=3, offset=3)
        assert len(page2) == 3

    async def test_log_with_details(self, audit_store: SQLiteAuditLog):
        from uuid import uuid4

        entry = AuditLogEntry(
            action=AuditAction.UPDATE,
            object_type="entity",
            object_id=uuid4(),
            actor="test",
            details={"field": "name", "old": "Old", "new": "New"},
        )
        await audit_store.append(entry)
        logs = await audit_store.get_logs(limit=10)
        assert len(logs) == 1
        assert logs[0].details == {"field": "name", "old": "Old", "new": "New"}

    async def test_log_without_details(self, audit_store: SQLiteAuditLog):
        from uuid import uuid4

        entry = AuditLogEntry(
            action=AuditAction.CREATE,
            object_type="entity",
            object_id=uuid4(),
            actor="test",
        )
        await audit_store.append(entry)
        logs = await audit_store.get_logs(limit=10)
        assert len(logs) == 1
        assert logs[0].details is None


# --- Error Handling ---


class TestErrorHandling:
    async def test_health_check_positive(self, graph_store: SQLiteGraphStore):
        healthy = await graph_store.health_check()
        assert healthy is True

    async def test_health_check_negative(self):
        from ums.storage.sqlite.connection import DatabaseManager

        db = DatabaseManager("sqlite+aiosqlite://")
        store = SQLiteGraphStore(db)
        healthy = await store.health_check()
        assert healthy is False


# --- DatabaseManager ---


class TestDatabaseManager:
    async def test_double_close(self, db: DatabaseManager):
        await db.close()
        await db.close()

    async def test_execute_fails_before_init(self):
        db = DatabaseManager("sqlite+aiosqlite://")
        with pytest.raises(RuntimeError, match="DB not initialized"):
            await db.execute("SELECT 1")

    async def test_fetch_one_no_result(self, db: DatabaseManager):
        result = await db.fetch_one("SELECT * FROM entities WHERE id = 'nonexistent'")
        assert result is None

    async def test_execute_many(self, db: DatabaseManager):
        await db.execute_many(
            "INSERT INTO users (id, name, created_at) VALUES (?, ?, ?)",
            [("1", "Alice", "2024-01-01"), ("2", "Bob", "2024-01-02")],
        )
        await db.commit()
        rows = await db.fetch_all("SELECT * FROM users ORDER BY id")
        assert len(rows) == 2
        assert rows[0]["name"] == "Alice"
        assert rows[1]["name"] == "Bob"
