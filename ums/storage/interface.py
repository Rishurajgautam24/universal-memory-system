from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from ums.models.audit import AuditLogEntry
from ums.models.belief import Belief
from ums.models.candidate import MemoryCandidate
from ums.models.entity import Entity
from ums.models.identity import Identity
from ums.models.project import Project
from ums.models.relationship import Relationship
from ums.models.timeline import TimelineEvent
from ums.models.verified_memory import VerifiedMemory


class StorageInterface(ABC):
    @abstractmethod
    async def initialize(self) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    async def health_check(self) -> bool: ...


class GraphStoreInterface(StorageInterface):
    # Entity CRUD
    @abstractmethod
    async def create_entity(self, entity: Entity) -> Entity: ...

    @abstractmethod
    async def get_entity(self, entity_id: UUID) -> Entity | None: ...

    @abstractmethod
    async def update_entity(self, entity: Entity) -> Entity: ...

    @abstractmethod
    async def delete_entity(self, entity_id: UUID) -> None: ...

    # Relationship CRUD
    @abstractmethod
    async def create_relationship(self, relationship: Relationship) -> Relationship: ...

    @abstractmethod
    async def get_relationship(self, relationship_id: UUID) -> Relationship | None: ...

    @abstractmethod
    async def update_relationship(self, relationship: Relationship) -> Relationship: ...

    @abstractmethod
    async def delete_relationship(self, relationship_id: UUID) -> None: ...

    # VerifiedMemory CRUD
    @abstractmethod
    async def create_verified_memory(self, memory: VerifiedMemory) -> VerifiedMemory: ...

    @abstractmethod
    async def get_verified_memory(self, memory_id: UUID) -> VerifiedMemory | None: ...

    @abstractmethod
    async def update_verified_memory(self, memory: VerifiedMemory) -> VerifiedMemory: ...

    @abstractmethod
    async def upsert_verified_memory(self, memory: VerifiedMemory) -> VerifiedMemory: ...

    @abstractmethod
    async def find_all_verified_memories(self, limit: int = 100) -> list[VerifiedMemory]: ...

    @abstractmethod
    async def delete_verified_memory(self, memory_id: UUID) -> None: ...

    # Belief CRUD
    @abstractmethod
    async def create_belief(self, belief: Belief) -> Belief: ...

    @abstractmethod
    async def get_belief(self, belief_id: UUID) -> Belief | None: ...

    @abstractmethod
    async def update_belief(self, belief: Belief) -> Belief: ...

    @abstractmethod
    async def delete_belief(self, belief_id: UUID) -> None: ...

    @abstractmethod
    async def find_all_beliefs(self, min_confidence: float | None = None) -> list[Belief]: ...

    # Candidate CRUD
    @abstractmethod
    async def create_candidate(self, candidate: MemoryCandidate) -> MemoryCandidate: ...

    @abstractmethod
    async def get_candidate(self, candidate_id: UUID) -> MemoryCandidate | None: ...

    @abstractmethod
    async def update_candidate(self, candidate: MemoryCandidate) -> MemoryCandidate: ...

    @abstractmethod
    async def upsert_candidate(self, candidate: MemoryCandidate) -> MemoryCandidate: ...

    @abstractmethod
    async def find_candidates(self, status: str | None = None) -> list[MemoryCandidate]: ...

    @abstractmethod
    async def delete_candidate(self, candidate_id: UUID) -> None: ...

    # Identity CRUD
    @abstractmethod
    async def create_identity(self, identity: Identity) -> Identity: ...

    @abstractmethod
    async def get_identity(self, identity_id: UUID) -> Identity | None: ...

    @abstractmethod
    async def update_identity(self, identity: Identity) -> Identity: ...

    @abstractmethod
    async def delete_identity(self, identity_id: UUID) -> None: ...

    # Project CRUD
    @abstractmethod
    async def create_project(self, project: Project) -> Project: ...

    @abstractmethod
    async def get_project(self, project_id: UUID) -> Project | None: ...

    @abstractmethod
    async def update_project(self, project: Project) -> Project: ...

    @abstractmethod
    async def delete_project(self, project_id: UUID) -> None: ...


class TimelineStoreInterface(StorageInterface):
    @abstractmethod
    async def append_event(self, event: TimelineEvent) -> TimelineEvent: ...

    @abstractmethod
    async def get_events(
        self, limit: int = 100, offset: int = 0
    ) -> list[TimelineEvent]: ...

    @abstractmethod
    async def count_events(self) -> int: ...


class VectorStoreInterface(StorageInterface):
    @abstractmethod
    async def upsert_embedding(
        self, object_id: UUID, vector: list[float], metadata: dict | None = None
    ) -> None: ...

    @abstractmethod
    async def search(
        self, vector: list[float], top_k: int = 10
    ) -> list[tuple[UUID, float]]: ...

    @abstractmethod
    async def delete_embedding(self, object_id: UUID) -> None: ...


class CandidateQueueInterface(StorageInterface):
    @abstractmethod
    async def enqueue(self, candidate: MemoryCandidate) -> None: ...

    @abstractmethod
    async def dequeue_batch(self, batch_size: int = 10) -> list[MemoryCandidate]: ...

    @abstractmethod
    async def requeue(self, candidate_id: UUID) -> None: ...

    @abstractmethod
    async def mark_processed(self, candidate_id: UUID) -> None: ...

    @abstractmethod
    async def get_pending_count(self) -> int: ...

    @abstractmethod
    async def get_by_stage(self, stage: str) -> list[MemoryCandidate]: ...


class AuditLogInterface(StorageInterface):
    @abstractmethod
    async def append(self, entry: AuditLogEntry) -> AuditLogEntry: ...

    @abstractmethod
    async def get_logs(
        self, limit: int = 100, offset: int = 0
    ) -> list[AuditLogEntry]: ...


class Storage(
    GraphStoreInterface,
    TimelineStoreInterface,
    VectorStoreInterface,
    CandidateQueueInterface,
    AuditLogInterface,
):
    pass
