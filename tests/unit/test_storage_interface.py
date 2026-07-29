from uuid import UUID

import pytest

from ums.storage.interface import (
    AuditLogInterface,
    CandidateQueueInterface,
    GraphStoreInterface,
    Storage,
    StorageInterface,
    TimelineStoreInterface,
    VectorStoreInterface,
)


def test_storage_interface_cannot_be_instantiated():
    with pytest.raises(TypeError):
        StorageInterface()  # type: ignore[abstract]


def test_graph_store_interface_cannot_be_instantiated():
    with pytest.raises(TypeError):
        GraphStoreInterface()  # type: ignore[abstract]


def test_timeline_store_interface_cannot_be_instantiated():
    with pytest.raises(TypeError):
        TimelineStoreInterface()  # type: ignore[abstract]


def test_vector_store_interface_cannot_be_instantiated():
    with pytest.raises(TypeError):
        VectorStoreInterface()  # type: ignore[abstract]


def test_candidate_queue_interface_cannot_be_instantiated():
    with pytest.raises(TypeError):
        CandidateQueueInterface()  # type: ignore[abstract]


def test_audit_log_interface_cannot_be_instantiated():
    with pytest.raises(TypeError):
        AuditLogInterface()  # type: ignore[abstract]


def test_storage_cannot_be_instantiated():
    with pytest.raises(TypeError):
        Storage()  # type: ignore[abstract]


class TestStorageMethods:
    def test_inherits_from_all_interfaces(self):
        expected_bases = {
            GraphStoreInterface,
            TimelineStoreInterface,
            VectorStoreInterface,
            CandidateQueueInterface,
            AuditLogInterface,
        }
        actual_bases = set(Storage.__bases__)
        assert expected_bases.issubset(actual_bases)

    def test_has_initialize(self):
        assert hasattr(Storage, "initialize")

    def test_has_close(self):
        assert hasattr(Storage, "close")

    def test_has_health_check(self):
        assert hasattr(Storage, "health_check")

    def test_has_entity_crud(self):
        assert hasattr(Storage, "create_entity")
        assert hasattr(Storage, "get_entity")
        assert hasattr(Storage, "update_entity")
        assert hasattr(Storage, "delete_entity")

    def test_has_relationship_crud(self):
        assert hasattr(Storage, "create_relationship")
        assert hasattr(Storage, "get_relationship")
        assert hasattr(Storage, "update_relationship")
        assert hasattr(Storage, "delete_relationship")

    def test_has_verified_memory_crud(self):
        assert hasattr(Storage, "create_verified_memory")
        assert hasattr(Storage, "get_verified_memory")
        assert hasattr(Storage, "update_verified_memory")
        assert hasattr(Storage, "delete_verified_memory")

    def test_has_belief_crud(self):
        assert hasattr(Storage, "create_belief")
        assert hasattr(Storage, "get_belief")
        assert hasattr(Storage, "update_belief")
        assert hasattr(Storage, "delete_belief")

    def test_has_candidate_crud(self):
        assert hasattr(Storage, "create_candidate")
        assert hasattr(Storage, "get_candidate")
        assert hasattr(Storage, "update_candidate")
        assert hasattr(Storage, "delete_candidate")

    def test_has_identity_crud(self):
        assert hasattr(Storage, "create_identity")
        assert hasattr(Storage, "get_identity")
        assert hasattr(Storage, "update_identity")
        assert hasattr(Storage, "delete_identity")

    def test_has_project_crud(self):
        assert hasattr(Storage, "create_project")
        assert hasattr(Storage, "get_project")
        assert hasattr(Storage, "update_project")
        assert hasattr(Storage, "delete_project")

    def test_has_timeline_methods(self):
        assert hasattr(Storage, "append_event")
        assert hasattr(Storage, "get_events")
        assert hasattr(Storage, "count_events")

    def test_has_vector_methods(self):
        assert hasattr(Storage, "upsert_embedding")
        assert hasattr(Storage, "search")
        assert hasattr(Storage, "delete_embedding")

    def test_has_candidate_queue_methods(self):
        assert hasattr(Storage, "enqueue")
        assert hasattr(Storage, "dequeue_batch")
        assert hasattr(Storage, "requeue")
        assert hasattr(Storage, "mark_processed")
        assert hasattr(Storage, "get_pending_count")
        assert hasattr(Storage, "get_by_stage")

    def test_has_audit_log_methods(self):
        assert hasattr(Storage, "append")
        assert hasattr(Storage, "get_logs")

    def test_all_methods_are_abstract(self):
        for name in dir(Storage):
            if name.startswith("_"):
                continue
            attr = getattr(Storage, name)
            if callable(attr) and not name.startswith("__"):
                assert getattr(attr, "__isabstractmethod__", False), f"{name} should be abstract"
