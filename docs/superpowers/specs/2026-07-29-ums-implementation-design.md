# UMS Implementation Design
## Universal Memory System — Phase 1-5

> **Version:** 1.0  
> **Date:** 2026-07-29  
> **Status:** APPROVED FOR IMPLEMENTATION  

---

## 1. Approach

**Recommended: Phase-by-Phase Sequential** — follow the roadmap exactly, completing each phase's success gates before starting the next.

**Why:** Solo developer, well-defined gates, each phase ships working value, low rework risk. The storage abstraction in Phase 1 is the critical foundation — getting interfaces right makes later phases smooth.

**Stack:** Python 3.11+ / FastAPI / SQLite (aiosqlite) / OpenRouter (LLM)

---

## 2. Project Structure

```
ums/
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── ums/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Pydantic Settings (env-driven)
│   ├── gateway/                # Layer 1: Memory Gateway (public API)
│   │   ├── routes/
│   │   │   ├── observe.py      # POST /v1/observe
│   │   │   ├── recall.py       # POST /v1/recall
│   │   │   ├── search.py       # POST /v1/search
│   │   │   ├── timeline.py     # GET /v1/timeline
│   │   │   ├── explain.py      # POST /v1/explain
│   │   │   └── reflect.py      # POST /v1/reflect
│   │   ├── middleware/
│   │   │   ├── auth.py         # API key validation
│   │   │   ├── rate_limit.py   # Token bucket per user
│   │   │   └── request_id.py
│   │   ├── schemas.py          # Pydantic request/response models
│   │   └── exceptions.py
│   ├── observation/            # Layer 2: Observation Engine
│   │   ├── engine.py
│   │   ├── segmenter.py
│   │   ├── extractors/
│   │   │   ├── entities.py     # LLM call #1
│   │   │   ├── observations.py # LLM call #2
│   │   │   └── relationships.py # LLM call #3
│   │   ├── prompts/
│   │   └── queue.py            # Candidate queue (SQLite-backed)
│   ├── memory/                 # Layer 3: Memory Engine
│   │   ├── candidate.py        # Candidate lifecycle
│   │   ├── deduplication.py
│   │   ├── contradiction.py
│   │   ├── promotion.py
│   │   └── decay.py
│   ├── distillation/           # Layer 4: Distillation Engine
│   │   ├── scheduler.py
│   │   ├── pipeline.py
│   │   ├── merger.py
│   │   ├── belief_synthesis.py
│   │   └── models.py
│   ├── recall/                 # Layer 5: Recall Engine
│   │   ├── engine.py
│   │   ├── intent_parser.py
│   │   ├── project_loader.py
│   │   ├── belief_loader.py
│   │   ├── timeline_loader.py
│   │   ├── graph_traversal.py
│   │   ├── embedding_search.py
│   │   ├── ranker.py
│   │   └── assembler.py
│   ├── reflection/             # Layer 6: Reflection Engine
│   │   ├── scheduler.py
│   │   ├── engine.py
│   │   ├── questions/
│   │   ├── digest.py
│   │   └── models.py
│   ├── identity/               # Layer 7: Identity Model
│   │   ├── synthesizer.py
│   │   └── models.py
│   ├── storage/                # Abstract storage layer
│   │   ├── interface.py        # ABCs (Graph, Timeline, Vector, Queue, Audit)
│   │   ├── sqlite/
│   │   │   ├── graph.py
│   │   │   ├── timeline.py
│   │   │   ├── vector.py
│   │   │   ├── audit.py
│   │   │   └── migrations.py
│   │   ├── kuzu/               # Phase 2+ swap-in
│   │   └── chroma/             # Phase 2+ swap-in
│   ├── llm/
│   │   ├── interface.py        # LLMProvider protocol + ModelRouter
│   │   ├── openrouter.py       # OpenRouter implementation
│   │   └── prompts.py
│   ├── models/                 # Data models (from 04_DATA_MODEL.md)
│   ├── utils/
│   │   ├── embeddings.py
│   │   ├── similarity.py
│   │   ├── datetime.py
│   │   └── uuid.py
│   └── export/                 # Phase 5
│       ├── json_exporter.py
│       ├── markdown_exporter.py
│       └── importer.py
├── tests/
│   ├── conftest.py
│   ├── unit/
│   ├── component/
│   ├── integration/
│   └── fixtures/
├── scripts/
│   ├── dev.sh
│   ├── migrate.py
│   ├── seed_test_data.py
│   ├── run_distillation.py
│   ├── run_reflection.py
│   ├── create_user.py
│   ├── export_memory.py
│   └── import_memory.py
└── docs/
```

---

## 3. Core Interfaces

### 3.1 Storage Interface

```python
class GraphStoreInterface(StorageInterface):
    """Entities, relationships, verified memories, beliefs, identity model."""
    async def upsert_entity(self, entity) -> Entity
    async def get_entity(self, entity_id) -> Optional[Entity]
    async def find_entities_by_name(self, name, type_=None) -> List[Entity]
    async def find_entities_by_embedding(self, embedding, limit=10) -> List[Entity]
    async def merge_entities(self, from_id, into_id) -> None
    async def upsert_relationship(self, rel) -> Relationship
    async def get_relationships(self, subject_id, predicate=None) -> List[Relationship]
    async def get_inverse_relationships(self, object_id, predicate=None) -> List[Relationship]
    async def upsert_verified_memory(self, memory) -> VerifiedMemory
    async def get_verified_memory(self, memory_id) -> Optional[VerifiedMemory]
    async def find_verified_memories(self, entity_ids, limit=50) -> List[VerifiedMemory]
    async def upsert_belief(self, belief) -> Belief
    async def get_belief(self, belief_id) -> Optional[Belief]
    async def find_beliefs(self, entity_ids, min_confidence=0.0) -> List[Belief]
    async def upsert_identity_model(self, identity) -> IdentityModel
    async def get_identity_model(self, user_id) -> Optional[IdentityModel]

class TimelineStoreInterface(StorageInterface):
    async def append_event(self, event) -> TimelineEvent
    async def get_events(self, from_ts=None, to_ts=None, project=None, event_types=None, limit=50, offset=0) -> List[TimelineEvent]
    async def count_events(self, **filters) -> int

class VectorStoreInterface(StorageInterface):
    async def upsert_embedding(self, object_id, object_type, embedding, metadata) -> None
    async def search(self, query_embedding, object_types=None, limit=10, min_score=0.5) -> List[tuple]
    async def delete_embedding(self, object_id, object_type) -> None

class CandidateQueueInterface(StorageInterface):
    async def enqueue(self, observation) -> None
    async def dequeue_batch(self, batch_size) -> List[Observation]
    async def requeue(self, observation) -> None
    async def mark_processed(self, observation_id) -> None
    async def get_pending_count(self) -> int

class AuditLogInterface(StorageInterface):
    async def append(self, entry) -> AuditLogEntry
    async def get_logs(self, object_type=None, object_id=None, limit=100) -> List[AuditLogEntry]
```

### 3.2 LLM Provider Interface

```python
class LLMProvider(ABC):
    @property
    def name(self) -> str  # "openrouter"
    @property
    def default_model(self) -> str
    @property
    def supports_json_mode(self) -> bool
    async def complete(self, messages, model=None, temperature=0.0, max_tokens=None, json_mode=False) -> LLMResponse
    async def embed(self, texts, model=None) -> List[List[float]]

class ModelRouter:
    def get(self, task: str) -> LLMProvider
    # "extraction" -> fast/cheap (gpt-4o-mini)
    # "synthesis" -> smart (gpt-4o)
    # "identity" -> best (gpt-4o)
```

### 3.3 All Interfaces → Unified Composite

```python
class Storage(GraphStoreInterface, TimelineStoreInterface, VectorStoreInterface,
              CandidateQueueInterface, AuditLogInterface):
    pass  # Implementations compose backends
```

---

## 4. SQLite Schema (Phase 1)

```sql
CREATE TABLE users (id TEXT PRIMARY KEY, api_key_hash TEXT, created_at TEXT);

CREATE TABLE observations (id TEXT PRIMARY KEY, user_id TEXT, source TEXT, session_id TEXT,
    timestamp TEXT, raw_text TEXT, statement TEXT, confidence REAL, entities TEXT,
    category TEXT, metadata TEXT, stage TEXT, expires_at TEXT, created_at TEXT);

CREATE TABLE candidates (id TEXT PRIMARY KEY, user_id TEXT, statement TEXT, category TEXT,
    confidence REAL, supporting_obs TEXT, contradicting_obs TEXT, affected_entities TEXT,
    created_at TEXT, last_updated TEXT, promotion_threshold REAL, status TEXT,
    expiry_date TEXT, needs_review INTEGER, notes TEXT);

CREATE TABLE verified_memories (id TEXT PRIMARY KEY, user_id TEXT, statement TEXT, category TEXT,
    confidence REAL, source_candidate_id TEXT, supporting_obs TEXT, entity_links TEXT,
    created_at TEXT, last_reinforced TEXT, last_contradicted TEXT, status TEXT,
    superseded_by TEXT, version INTEGER, history TEXT);

CREATE TABLE entities (id TEXT PRIMARY KEY, user_id TEXT, type TEXT, name TEXT, aliases TEXT,
    description TEXT, embedding BLOB, confidence REAL, created_at TEXT, last_seen TEXT,
    source_obs TEXT, attributes TEXT, status TEXT, merged_into TEXT);

CREATE TABLE relationships (id TEXT PRIMARY KEY, user_id TEXT, subject_id TEXT, predicate TEXT,
    object_id TEXT, confidence REAL, source_obs TEXT, created_at TEXT, last_reinforced TEXT,
    valid_from TEXT, valid_until TEXT, status TEXT, context TEXT);

CREATE TABLE beliefs (id TEXT PRIMARY KEY, user_id TEXT, statement TEXT, confidence REAL,
    supporting_memories TEXT, contradicting_memories TEXT, entity_links TEXT,
    created_at TEXT, last_updated TEXT, history TEXT, status TEXT, generated_by TEXT);

CREATE TABLE timeline_events (id TEXT PRIMARY KEY, user_id TEXT, who TEXT, what TEXT,
    when_ts TEXT, where_app TEXT, event_type TEXT, references TEXT, summary TEXT, created_at TEXT);

CREATE TABLE audit_log (id TEXT PRIMARY KEY, timestamp TEXT, action TEXT, object_type TEXT,
    object_id TEXT, actor TEXT, before TEXT, after TEXT, reason TEXT);

CREATE TABLE distillation_cycles (id TEXT PRIMARY KEY, user_id TEXT, started_at TEXT,
    completed_at TEXT, observations_read INTEGER, candidates_created INTEGER,
    candidates_promoted INTEGER, candidates_expired INTEGER, beliefs_updated INTEGER,
    graph_nodes_updated INTEGER, embeddings_updated INTEGER, summary TEXT, status TEXT, errors TEXT);

CREATE TABLE reflections (id TEXT PRIMARY KEY, user_id TEXT, run_at TEXT, period_start TEXT,
    period_end TEXT, changed_beliefs TEXT, new_beliefs TEXT, archived_beliefs TEXT,
    project_updates TEXT, patterns_found TEXT, digest TEXT, trigger TEXT);

CREATE TABLE identity_models (id TEXT PRIMARY KEY, user_id TEXT, last_updated TEXT,
    core_interests TEXT, skills TEXT, preferences TEXT, values TEXT,
    active_projects TEXT, identity_summary TEXT, version INTEGER, generated_by TEXT);
```

---

## 5. Phase Implementation Plans

### Phase 1: Core Memory Server (4-6 weeks)

**Goal:** Working local server with `observe()` → queue → basic `recall()`, all observations as candidates, persistence across restarts.

**Gates:** P1-G1 through P1-G5 from `docs/02_SUCCESS_CRITERIA.md`

**Week 1 — Foundation & Storage:**
- Project setup: FastAPI app, `pyproject.toml`, config
- Define all data models (12 object types)
- Storage interfaces (5 ABCs)
- SQLite implementations: GraphStore, TimelineStore, CandidateQueue, AuditLog
- Migration system

**Week 2 — LLM Abstraction & Observation Engine:**
- OpenRouter LLM provider
- Prompt templates for entity/observation extraction
- Conversation segmenter
- Entity, observation, relationship extractors (3 LLM calls)
- Observation engine orchestrator
- Error handling + retry logic

**Week 3 — Memory Engine (Candidate System):**
- Candidate creation from observations
- Semantic deduplication (embedding-based similarity >0.85)
- Contradiction detection
- Entity resolution
- Manual distillation pipeline runner
- Candidate promotion logic (confidence ≥0.75 + ≥2 obs)
- Timeline + audit logging on promotion

**Week 4 — Recall Engine + Gateway:**
- Intent parser
- Project, belief, timeline loaders
- Ranker + context assembler
- All 6 gateway routes (stubs for non-Phase-1 features)
- Auth middleware (API key validation)
- Rate limiting
- Pydantic request/response schemas

**Week 5 — Integration, Testing & Gates:**
- E2E integration test (observe → distill → recall)
- Load tests for latency SLOs
- Restart persistence test
- Candidate-only verification
- Dockerfile + docker-compose.yml
- CLI scripts (migrate, seed, distill)
- Documentation

**Phase 1 simplifications:**
- Distillation runs manually (no scheduler)
- Vector search skipped (keyword/entity-based recall only)
- No belief synthesis (verified memories serve as beliefs)
- No reflection engine

---

### Phase 2: Knowledge Graph + Timeline + Hybrid Retrieval (4-6 weeks)

**Gates:** P2-G1 through P2-G5

- Named entity extraction (already built in Phase 1, now enhanced)
- Graph store: swap SQLite → Kuzu (graph database) or stay with SQLite extended
- Vector store: add sqlite-vec or ChromaDB
- Entity resolution + merging (deduplicate aliases)
- Relationship extraction + storage
- Hybrid recall pipeline: intent → projects → beliefs → timeline → graph → embeddings → rank
- `GET /v1/timeline` fully implemented with filters + pagination
- Embedding refresh worker (background)

---

### Phase 3: Distillation, Confidence, Candidate Promotion (4-6 weeks)

**Gates:** P3-G1 through P3-G5

- Distillation scheduler (APScheduler, every 4 hours)
- Confidence accumulation formula: `1 - (1 - current) * (1 - new_obs) * decay`
- Automated candidate promotion with threshold + min evidence
- Contradiction detection + competing Candidate pairs
- Memory decay for beliefs without reinforcement
- DistillationCycle metadata logging
- Semantic deduplication (merging equivalent observations)
- `POST /v1/explain` endpoint with full evidence chain

---

### Phase 4: Reflection + Proactive Memory (3-4 weeks)

**Gates:** P4-G1 through P4-G4

- Reflection scheduler (nightly at 02:00 UTC)
- 6 reflection questions:
  1. What changed in beliefs today?
  2. What topics grew in importance?
  3. What became less relevant?
  4. Which projects progressed / stalled?
  5. Which contradictions remain unresolved?
  6. What patterns are emerging?
- Daily digest generation (human-readable narrative)
- Belief lifecycle management (ACTIVE → WEAKENING → ARCHIVED)
- Pattern detection across projects
- Identity Model synthesis (confidence ≥ 0.85, age ≥ 30 days)
- `POST /v1/reflect` with dry_run support

---

### Phase 5: SDKs + Connectors (6-8 weeks)

**Gates:** P5-G1 through P5-G4

- Python SDK (`pip install ums-sdk`): observe, recall, search, timeline, explain, reflect
- TypeScript SDK (`npm install @ums/sdk`): feature parity
- MCP Server exposing 6 tools
- Claude Desktop connector (MCP config)
- Cursor integration (VS Code config)
- Docker image (single-command self-hosted)
- Full memory export (JSON + Markdown) + import
- Quickstart guide (15-minute setup)

---

## 6. Configuration

```python
# Key settings (all env-driven via Pydantic)
SERVER_HOST: str = "0.0.0.0"
SERVER_PORT: int = 8000
DATABASE_URL: str = "sqlite+aiosqlite:///./data/ums.db"
OPENROUTER_API_KEY: str  # Required
EXTRACTION_MODEL: str = "openai/gpt-4o-mini"
SYNTHESIS_MODEL: str = "openai/gpt-4o"
EMBEDDING_MODEL: str = "openai/text-embedding-3-small"
MIN_OBSERVATION_CONFIDENCE: float = 0.4
CANDIDATE_PROMOTION_THRESHOLD: float = 0.75
MIN_EVIDENCE_FOR_PROMOTION: int = 2
DISTILLATION_INTERVAL_HOURS: int = 4
DISTILLATION_BATCH_SIZE: int = 10
RECALL_MIN_CONFIDENCE: float = 0.5
RECALL_MAX_TOKENS: int = 2000
```

---

## 7. Testing

### Test Pyramid
- **Unit** (100+ tests): Pure functions, model validation, prompt rendering, ranking formula
- **Component** (20-30 per layer): Layer tests against real SQLite with mocked LLM
- **E2E** (5-10 scenarios): Full stack observe → distill → recall → explain

### Key E2E Scenarios
1. Observe → Distill → Recall (basic memory loop)
2. Multi-source observations → single candidate merge
3. Contradiction detection (both memories preserved)
4. Timeline query (chronological, filtered by project)
5. Explain evidence chain (belief → candidate → observation)
6. Export → Import round-trip (data integrity)
7. Restart persistence (no data loss)
8. Rate limiting enforcement
9. Auth isolation (user isolation)

### Phase Gate Tests
Each phase gate from `docs/02_SUCCESS_CRITERIA.md` has an automated test:
- P1-G1: observe 2000-token conversation → ≥3 observations
- P1-G2: recall returns relevant context
- P1-G3: persistence across restart
- P1-G4: no direct writes to permanent memory
- P1-G5: observe <200ms ack, recall <2s p95

### CI Pipeline
```yaml
jobs:
  test:
    steps:
      - run: pytest tests/unit
      - run: pytest tests/component
      - run: pytest tests/integration
      - run: ruff check .
      - run: mypy ums/
```

---

## 8. Deployment

### Docker (Multi-stage)
- Stage 1: Build with `uv`
- Stage 2: Slim runtime, non-root user, HEALTHCHECK, port 8000

### Docker Compose (Local Dev)
- Single service (UMS) with volume mounts for SQLite data
- Hot reload support for development

### Production Concerns
- **Secrets:** .env file or Docker secrets
- **Database:** SQLite for single-user; PostgreSQL for multi-user (future)
- **Backups:** Daily sqlite3 dump
- **Logs:** Structured JSON → stdout
- **Monitoring:** /health, /health/ready, /metrics

---

## 9. Design Invariants

1. Every Verified Memory links to ≥1 Observation via its source Candidate
2. Every Belief links to ≥1 Verified Memory
3. Every Identity Model links to ≥1 Belief
4. No object is ever hard-deleted — only ARCHIVED, MERGED, or SUPERSEDED
5. Every stage transition generates an Audit Log Entry
6. LLMs never write directly to permanent memory
7. Storage is always behind an interface — backends are swappable
8. No information can skip a pipeline stage
