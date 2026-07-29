from __future__ import annotations

# (version, SQL) tuples — applied in order, each only once
MIGRATIONS: list[tuple[int, str]] = [
    (
        1,
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS observations (
            id TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            session_id TEXT NOT NULL,
            raw_text TEXT NOT NULL,
            statement TEXT NOT NULL,
            confidence REAL NOT NULL,
            category TEXT,
            stage TEXT NOT NULL DEFAULT 'PENDING',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_observations_stage ON observations(stage);

        CREATE TABLE IF NOT EXISTS candidates (
            id TEXT PRIMARY KEY,
            statement TEXT NOT NULL,
            confidence REAL NOT NULL,
            category TEXT,
            observation_ids TEXT NOT NULL DEFAULT '[]',
            supporting_obs TEXT NOT NULL DEFAULT '[]',
            contradicting_obs TEXT NOT NULL DEFAULT '[]',
            notes TEXT,
            promotion_threshold REAL NOT NULL DEFAULT 0.75,
            status TEXT NOT NULL DEFAULT 'ACCUMULATING',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_candidates_status ON candidates(status);

        CREATE TABLE IF NOT EXISTS verified_memories (
            id TEXT PRIMARY KEY,
            statement TEXT NOT NULL,
            confidence REAL NOT NULL,
            category TEXT,
            source_candidate_id TEXT,
            supporting_obs TEXT NOT NULL DEFAULT '[]',
            status TEXT NOT NULL DEFAULT 'ACTIVE',
            version INTEGER NOT NULL DEFAULT 1,
            superseded_by TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_verified_memories_status ON verified_memories(status);

        CREATE TABLE IF NOT EXISTS entities (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            aliases TEXT NOT NULL DEFAULT '[]',
            description TEXT,
            confidence REAL NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS relationships (
            id TEXT PRIMARY KEY,
            source_entity_id TEXT NOT NULL,
            target_entity_id TEXT NOT NULL,
            relation_type TEXT NOT NULL,
            confidence REAL NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            confidence REAL NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS beliefs (
            id TEXT PRIMARY KEY,
            statement TEXT NOT NULL,
            confidence REAL NOT NULL,
            supporting_memory_ids TEXT NOT NULL DEFAULT '[]',
            contradicting_memory_ids TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS timeline_events (
            id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            object_id TEXT NOT NULL,
            object_type TEXT NOT NULL,
            description TEXT NOT NULL,
            confidence REAL NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_timeline_events_created_at ON timeline_events(created_at);

        CREATE TABLE IF NOT EXISTS audit_log (
            id TEXT PRIMARY KEY,
            action TEXT NOT NULL,
            object_type TEXT NOT NULL,
            object_id TEXT NOT NULL,
            actor TEXT NOT NULL,
            details TEXT,
            confidence REAL NOT NULL DEFAULT 1.0,
            created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at);

        CREATE TABLE IF NOT EXISTS distillation_cycles (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            confidence REAL NOT NULL,
            source_reflection_ids TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS identity_models (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            confidence REAL NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS reflections (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            confidence REAL NOT NULL,
            source_memory_ids TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """,
    ),
]
