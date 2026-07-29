from __future__ import annotations

import json
from uuid import UUID

from ums.models.belief import Belief
from ums.models.candidate import MemoryCandidate
from ums.models.entity import Entity
from ums.models.identity import Identity
from ums.models.observation import Observation
from ums.models.project import Project
from ums.models.relationship import Relationship
from ums.models.verified_memory import VerifiedMemory
from ums.storage.sqlite.connection import DatabaseManager

JSON_LIST_FIELDS: dict[type, list[str]] = {
    Entity: ["aliases"],
    Relationship: [],
    VerifiedMemory: [],
    Belief: ["supporting_memory_ids", "contradicting_memory_ids"],
    Identity: [],
    MemoryCandidate: ["observation_ids"],
    Project: [],
    Observation: [],
}


def _to_json(val):
    return json.dumps(val) if val is not None else "[]"


def _from_json(val):
    return json.loads(val) if val else []


def _uuid_row(row: dict, field: str = "id") -> dict:
    row[field] = UUID(row[field])
    return row


def _build_entity(row: dict) -> Entity:
    row = _uuid_row(row)
    row["aliases"] = _from_json(row.pop("aliases", "[]"))
    return Entity(**row)


def _build_observation(row: dict) -> Observation:
    row = _uuid_row(row)
    return Observation(**row)


def _build_relationship(row: dict) -> Relationship:
    row = _uuid_row(row)
    row["source_entity_id"] = UUID(row["source_entity_id"])
    row["target_entity_id"] = UUID(row["target_entity_id"])
    return Relationship(**row)


def _build_verified_memory(row: dict) -> VerifiedMemory:
    row = _uuid_row(row)
    if row.get("source_candidate_id"):
        row["source_candidate_id"] = UUID(row["source_candidate_id"])
    if row.get("superseded_by"):
        row["superseded_by"] = UUID(row["superseded_by"])
    row["supporting_obs"] = _from_json(row.pop("supporting_obs", "[]"))
    return VerifiedMemory(**row)


def _build_belief(row: dict) -> Belief:
    row = _uuid_row(row)
    row["supporting_memory_ids"] = [UUID(v) for v in _from_json(row.pop("supporting_memory_ids", "[]"))]
    row["contradicting_memory_ids"] = [UUID(v) for v in _from_json(row.pop("contradicting_memory_ids", "[]"))]
    return Belief(**row)


def _build_candidate(row: dict) -> MemoryCandidate:
    row = _uuid_row(row)
    row["observation_ids"] = [UUID(v) for v in _from_json(row.pop("observation_ids", "[]"))]
    row["supporting_obs"] = _from_json(row.pop("supporting_obs", "[]"))
    row["contradicting_obs"] = _from_json(row.pop("contradicting_obs", "[]"))
    return MemoryCandidate(**row)


def _build_identity(row: dict) -> Identity:
    row = _uuid_row(row)
    return Identity(**row)


def _build_project(row: dict) -> Project:
    row = _uuid_row(row)
    return Project(**row)


class SQLiteGraphStore:
    def __init__(self, db: DatabaseManager):
        self._db = db

    async def initialize(self) -> None:
        await self._db.initialize()

    async def close(self) -> None:
        await self._db.close()

    async def health_check(self) -> bool:
        try:
            await self._db.execute("SELECT 1")
            return True
        except BaseException:  # noqa: BLE001
            return False

    # --- Entity CRUD ---

    async def create_entity(self, entity: Entity) -> Entity:
        data = entity.model_dump()
        data["aliases"] = json.dumps(data.get("aliases", []))
        await self._db.execute(
            "INSERT INTO entities (id, name, entity_type, aliases, description, confidence, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                str(data["id"]),
                data["name"],
                data["entity_type"],
                data["aliases"],
                data.get("description"),
                data["confidence"],
                data["created_at"],
                data["updated_at"],
            ),
        )
        await self._db.commit()
        return entity

    async def get_entity(self, entity_id: UUID) -> Entity | None:
        row = await self._db.fetch_one("SELECT * FROM entities WHERE id = ?", (str(entity_id),))
        return _build_entity(row) if row else None

    async def update_entity(self, entity: Entity) -> Entity:
        data = entity.model_dump()
        data["aliases"] = json.dumps(data.get("aliases", []))
        await self._db.execute(
            "UPDATE entities SET name=?, entity_type=?, aliases=?, description=?, confidence=?, updated_at=? WHERE id=?",
            (
                data["name"],
                data["entity_type"],
                data["aliases"],
                data.get("description"),
                data["confidence"],
                data["updated_at"],
                str(data["id"]),
            ),
        )
        await self._db.commit()
        return entity

    async def delete_entity(self, entity_id: UUID) -> None:
        await self._db.execute("DELETE FROM entities WHERE id = ?", (str(entity_id),))
        await self._db.commit()

    # --- Relationship CRUD ---

    async def create_relationship(self, relationship: Relationship) -> Relationship:
        data = relationship.model_dump()
        await self._db.execute(
            "INSERT INTO relationships (id, source_entity_id, target_entity_id, relation_type, confidence, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                str(data["id"]),
                str(data["source_entity_id"]),
                str(data["target_entity_id"]),
                data["relation_type"],
                data["confidence"],
                data["created_at"],
                data["updated_at"],
            ),
        )
        await self._db.commit()
        return relationship

    async def get_relationship(self, relationship_id: UUID) -> Relationship | None:
        row = await self._db.fetch_one("SELECT * FROM relationships WHERE id = ?", (str(relationship_id),))
        return _build_relationship(row) if row else None

    async def update_relationship(self, relationship: Relationship) -> Relationship:
        data = relationship.model_dump()
        await self._db.execute(
            "UPDATE relationships SET source_entity_id=?, target_entity_id=?, relation_type=?, confidence=?, updated_at=? WHERE id=?",
            (
                str(data["source_entity_id"]),
                str(data["target_entity_id"]),
                data["relation_type"],
                data["confidence"],
                data["updated_at"],
                str(data["id"]),
            ),
        )
        await self._db.commit()
        return relationship

    async def delete_relationship(self, relationship_id: UUID) -> None:
        await self._db.execute("DELETE FROM relationships WHERE id = ?", (str(relationship_id),))
        await self._db.commit()

    # --- VerifiedMemory CRUD ---

    async def create_verified_memory(self, memory: VerifiedMemory) -> VerifiedMemory:
        data = memory.model_dump()
        data["supporting_obs"] = json.dumps(data.get("supporting_obs", []))
        await self._db.execute(
            "INSERT INTO verified_memories (id, statement, confidence, category, source_candidate_id, supporting_obs, status, version, superseded_by, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                str(data["id"]),
                data["statement"],
                data["confidence"],
                data.get("category"),
                str(data["source_candidate_id"]) if data.get("source_candidate_id") else None,
                data["supporting_obs"],
                data["status"],
                data["version"],
                str(data["superseded_by"]) if data.get("superseded_by") else None,
                data["created_at"],
                data["updated_at"],
            ),
        )
        await self._db.commit()
        return memory

    async def get_verified_memory(self, memory_id: UUID) -> VerifiedMemory | None:
        row = await self._db.fetch_one("SELECT * FROM verified_memories WHERE id = ?", (str(memory_id),))
        return _build_verified_memory(row) if row else None

    async def update_verified_memory(self, memory: VerifiedMemory) -> VerifiedMemory:
        data = memory.model_dump()
        data["supporting_obs"] = json.dumps(data.get("supporting_obs", []))
        await self._db.execute(
            "UPDATE verified_memories SET statement=?, confidence=?, category=?, source_candidate_id=?, supporting_obs=?, status=?, version=?, superseded_by=?, updated_at=? WHERE id=?",
            (
                data["statement"],
                data["confidence"],
                data.get("category"),
                str(data["source_candidate_id"]) if data.get("source_candidate_id") else None,
                data["supporting_obs"],
                data["status"],
                data["version"],
                str(data["superseded_by"]) if data.get("superseded_by") else None,
                data["updated_at"],
                str(data["id"]),
            ),
        )
        await self._db.commit()
        return memory

    async def upsert_verified_memory(self, memory: VerifiedMemory) -> VerifiedMemory:
        existing = await self.get_verified_memory(memory.id)
        if existing:
            return await self.update_verified_memory(memory)
        return await self.create_verified_memory(memory)

    async def find_all_verified_memories(self, limit: int = 100) -> list[VerifiedMemory]:
        rows = await self._db.fetch_all(
            "SELECT * FROM verified_memories WHERE status = 'ACTIVE' ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
        return [_build_verified_memory(r) for r in rows]

    async def delete_verified_memory(self, memory_id: UUID) -> None:
        await self._db.execute("DELETE FROM verified_memories WHERE id = ?", (str(memory_id),))
        await self._db.commit()

    # --- Belief CRUD ---

    async def create_belief(self, belief: Belief) -> Belief:
        data = belief.model_dump()
        data["supporting_memory_ids"] = json.dumps([str(u) for u in data.get("supporting_memory_ids", [])])
        data["contradicting_memory_ids"] = json.dumps([str(u) for u in data.get("contradicting_memory_ids", [])])
        await self._db.execute(
            "INSERT INTO beliefs (id, statement, confidence, supporting_memory_ids, contradicting_memory_ids, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                str(data["id"]),
                data["statement"],
                data["confidence"],
                data["supporting_memory_ids"],
                data["contradicting_memory_ids"],
                data["created_at"],
                data["updated_at"],
            ),
        )
        await self._db.commit()
        return belief

    async def get_belief(self, belief_id: UUID) -> Belief | None:
        row = await self._db.fetch_one("SELECT * FROM beliefs WHERE id = ?", (str(belief_id),))
        return _build_belief(row) if row else None

    async def update_belief(self, belief: Belief) -> Belief:
        data = belief.model_dump()
        data["supporting_memory_ids"] = json.dumps([str(u) for u in data.get("supporting_memory_ids", [])])
        data["contradicting_memory_ids"] = json.dumps([str(u) for u in data.get("contradicting_memory_ids", [])])
        await self._db.execute(
            "UPDATE beliefs SET statement=?, confidence=?, supporting_memory_ids=?, contradicting_memory_ids=?, updated_at=? WHERE id=?",
            (
                data["statement"],
                data["confidence"],
                data["supporting_memory_ids"],
                data["contradicting_memory_ids"],
                data["updated_at"],
                str(data["id"]),
            ),
        )
        await self._db.commit()
        return belief

    async def delete_belief(self, belief_id: UUID) -> None:
        await self._db.execute("DELETE FROM beliefs WHERE id = ?", (str(belief_id),))
        await self._db.commit()

    # --- Candidate CRUD ---

    async def create_candidate(self, candidate: MemoryCandidate) -> MemoryCandidate:
        data = candidate.model_dump()
        data["observation_ids"] = json.dumps([str(u) for u in data.get("observation_ids", [])])
        data["supporting_obs"] = json.dumps(data.get("supporting_obs", []))
        data["contradicting_obs"] = json.dumps(data.get("contradicting_obs", []))
        await self._db.execute(
            "INSERT INTO candidates (id, statement, confidence, category, observation_ids, supporting_obs, contradicting_obs, notes, promotion_threshold, status, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                str(data["id"]),
                data["statement"],
                data["confidence"],
                data.get("category"),
                data["observation_ids"],
                data["supporting_obs"],
                data["contradicting_obs"],
                data.get("notes"),
                data["promotion_threshold"],
                data["status"],
                data["created_at"],
                data["updated_at"],
            ),
        )
        await self._db.commit()
        return candidate

    async def get_candidate(self, candidate_id: UUID) -> MemoryCandidate | None:
        row = await self._db.fetch_one("SELECT * FROM candidates WHERE id = ?", (str(candidate_id),))
        return _build_candidate(row) if row else None

    async def update_candidate(self, candidate: MemoryCandidate) -> MemoryCandidate:
        data = candidate.model_dump()
        data["observation_ids"] = json.dumps([str(u) for u in data.get("observation_ids", [])])
        data["supporting_obs"] = json.dumps(data.get("supporting_obs", []))
        data["contradicting_obs"] = json.dumps(data.get("contradicting_obs", []))
        await self._db.execute(
            "UPDATE candidates SET statement=?, confidence=?, category=?, observation_ids=?, supporting_obs=?, contradicting_obs=?, notes=?, promotion_threshold=?, status=?, updated_at=? WHERE id=?",
            (
                data["statement"],
                data["confidence"],
                data.get("category"),
                data["observation_ids"],
                data["supporting_obs"],
                data["contradicting_obs"],
                data.get("notes"),
                data["promotion_threshold"],
                data["status"],
                data["updated_at"],
                str(data["id"]),
            ),
        )
        await self._db.commit()
        return candidate

    async def upsert_candidate(self, candidate: MemoryCandidate) -> MemoryCandidate:
        existing = await self.get_candidate(candidate.id)
        if existing:
            return await self.update_candidate(candidate)
        return await self.create_candidate(candidate)

    async def find_candidates(self, status: str | None = None) -> list[MemoryCandidate]:
        if status:
            rows = await self._db.fetch_all("SELECT * FROM candidates WHERE status = ?", (status,))
        else:
            rows = await self._db.fetch_all("SELECT * FROM candidates")
        return [_build_candidate(r) for r in rows]

    async def delete_candidate(self, candidate_id: UUID) -> None:
        await self._db.execute("DELETE FROM candidates WHERE id = ?", (str(candidate_id),))
        await self._db.commit()

    # --- Identity CRUD ---

    async def create_identity(self, identity: Identity) -> Identity:
        data = identity.model_dump()
        await self._db.execute(
            "INSERT INTO identity_models (id, name, confidence, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (str(data["id"]), data["name"], data["confidence"], data["created_at"], data["updated_at"]),
        )
        await self._db.commit()
        return identity

    async def get_identity(self, identity_id: UUID) -> Identity | None:
        row = await self._db.fetch_one("SELECT * FROM identity_models WHERE id = ?", (str(identity_id),))
        return _build_identity(row) if row else None

    async def update_identity(self, identity: Identity) -> Identity:
        data = identity.model_dump()
        await self._db.execute(
            "UPDATE identity_models SET name=?, confidence=?, updated_at=? WHERE id=?",
            (data["name"], data["confidence"], data["updated_at"], str(data["id"])),
        )
        await self._db.commit()
        return identity

    async def delete_identity(self, identity_id: UUID) -> None:
        await self._db.execute("DELETE FROM identity_models WHERE id = ?", (str(identity_id),))
        await self._db.commit()

    # --- Project CRUD ---

    async def create_project(self, project: Project) -> Project:
        data = project.model_dump()
        await self._db.execute(
            "INSERT INTO projects (id, name, description, confidence, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (
                str(data["id"]),
                data["name"],
                data.get("description"),
                data["confidence"],
                data["created_at"],
                data["updated_at"],
            ),
        )
        await self._db.commit()
        return project

    async def get_project(self, project_id: UUID) -> Project | None:
        row = await self._db.fetch_one("SELECT * FROM projects WHERE id = ?", (str(project_id),))
        return _build_project(row) if row else None

    async def update_project(self, project: Project) -> Project:
        data = project.model_dump()
        await self._db.execute(
            "UPDATE projects SET name=?, description=?, confidence=?, updated_at=? WHERE id=?",
            (
                data["name"],
                data.get("description"),
                data["confidence"],
                data["updated_at"],
                str(data["id"]),
            ),
        )
        await self._db.commit()
        return project

    async def delete_project(self, project_id: UUID) -> None:
        await self._db.execute("DELETE FROM projects WHERE id = ?", (str(project_id),))
        await self._db.commit()
