# Phase 1: Core Memory Server - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A working local memory server with `observe()` → queue → basic `recall()`, all observations as candidates, persistence across restarts.

**Architecture:** 7-layer architecture with interface-first design. Storage abstracted behind ABCs (SQLite in Phase 1). LLM calls routed through a single provider abstraction (OpenRouter). Observation pipeline never writes directly to permanent memory.

**Tech Stack:** Python 3.11+, FastAPI, SQLite (aiosqlite), OpenRouter (OpenAI-compatible API), uv (package management), pytest, APScheduler

## Global Constraints

- Python 3.11+ required
- All storage behind abstract interfaces (swappable backends)
- LLM calls only through `LLMProvider` abstraction
- No direct writes to VerifiedMemory from Observation Engine
- Never hard-delete data — only ARCHIVE, MERGE, or SUPERSEDE
- Every stage transition must generate an Audit Log Entry
- All models use ISO 8601 UTC datetimes
- Confidence scores are floats in [0.0, 1.0]

---

## File Structure

```
ums/
├── pyproject.toml
├── .env.example
├── Makefile
├── Dockerfile
├── docker-compose.yml
├── ums/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── gateway/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── schemas.py
│   │   ├── exceptions.py
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── rate_limit.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── observe.py
│   │       ├── recall.py
│   │       ├── search.py
│   │       ├── timeline.py
│   │       ├── explain.py
│   │       └── reflect.py
│   ├── observation/
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   ├── segmenter.py
│   │   ├── extractors.py
│   │   └── prompts.py
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── candidate.py
│   │   ├── deduplication.py
│   │   ├── contradiction.py
│   │   └── promotion.py
│   ├── distillation/
│   │   ├── __init__.py
│   │   └── pipeline.py
│   ├── recall/
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   ├── intent_parser.py
│   │   ├── loaders.py
│   │   ├── ranker.py
│   │   └── assembler.py
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── interface.py
│   │   └── sqlite/
│   │       ├── __init__.py
│   │       ├── connection.py
│   │       ├── graph.py
│   │       ├── timeline.py
│   │       ├── vector.py
│   │       ├── audit.py
│   │       └── migrations.py
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── interface.py
│   │   ├── openrouter.py
│   │   ├── router.py
│   │   └── prompts.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── observation.py
│   │   ├── candidate.py
│   │   ├── verified_memory.py
│   │   ├── entity.py
│   │   ├── relationship.py
│   │   ├── belief.py
│   │   ├── project.py
│   │   ├── timeline.py
│   │   ├── identity.py
│   │   ├── reflection.py
│   │   ├── distillation.py
│   │   └── audit.py
│   └── utils/
│       ├── __init__.py
│       ├── embeddings.py
│       ├── similarity.py
│       └── datetime.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_storage_interface.py
│   │   ├── test_deduplication.py
│   │   ├── test_promotion.py
│   │   ├── test_ranker.py
│   │   └── test_intent_parser.py
│   ├── component/
│   │   ├── test_storage_sqlite.py
│   │   ├── test_observation_engine.py
│   │   ├── test_candidate_system.py
│   │   ├── test_distillation.py
│   │   ├── test_recall_engine.py
│   │   └── test_gateway.py
│   └── integration/
│       └── test_pipeline_e2e.py
├── scripts/
│   ├── dev.sh
│   ├── migrate.py
│   ├── seed_test_data.py
│   ├── run_distillation.py
│   └── create_user.py
└── data/
```

---

## Implementation Tasks

---

### Task 1: Project Scaffold & Configuration

**Files:**
- Create: `ums/pyproject.toml`
- Create: `ums/.env.example`
- Create: `ums/Makefile`
- Create: `ums/ums/__init__.py`
- Create: `ums/ums/config.py`
- Create: `ums/ums/main.py`
- Create: `ums/ums/utils/__init__.py`
- Create: `ums/ums/utils/datetime.py`
- Create: `ums/ums/utils/embeddings.py`
- Create: `ums/ums/utils/similarity.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

**Interfaces:**
- Consumes: nothing
- Produces: `config.Settings` (used by all tasks), datetime utilities, FastAPI app CLI entrypoint

**Step 1: Create pyproject.toml**
```toml
[project]
name = "ums"
version = "0.1.0"
description = "Universal Memory System - Persistent memory layer for AI applications"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic>=2.9.0",
    "pydantic-settings>=2.5.0",
    "aiosqlite>=0.20.0",
    "openai>=1.50.0",
    "httpx>=0.28.0",
    "jinja2>=3.1.0",
    "apscheduler>=3.10.0",
    "structlog>=24.4.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=5.0.0",
    "ruff>=0.6.0",
    "mypy>=1.11.0",
    "asgi-lifespan>=2.1.0",
]

[tool.setuptools.packages.find]
include = ["ums*"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

**Step 2: Create config.py**
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8",
        case_sensitive=False, extra="ignore",
    )
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = False
    log_level: str = "INFO"
    database_url: str = "sqlite+aiosqlite:///./data/ums.db"
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    extraction_model: str = "openai/gpt-4o-mini"
    synthesis_model: str = "openai/gpt-4o"
    embedding_model: str = "openai/text-embedding-3-small"
    min_observation_confidence: float = 0.4
    max_observations_per_conversation: int = 50
    candidate_promotion_threshold: float = 0.75
    min_evidence_for_promotion: int = 2
    candidate_expiry_days: int = 30
    semantic_dedup_threshold: float = 0.85
    recall_max_tokens: int = 2000
    recall_min_confidence: float = 0.5
    distillation_batch_size: int = 10
    distillation_interval_hours: int = 4
    admin_api_key: Optional[str] = None

settings = Settings()
```

**Step 3: Create utils and main.py**

File `ums/utils/datetime.py`:
```python
from datetime import datetime, timezone

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def format_iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")
```

File `ums/utils/similarity.py`:
```python
import math

def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)
```

File `ums/utils/embeddings.py`:
```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ums.llm.interface import LLMProvider

class EmbeddingService:
    def __init__(self, provider: "LLMProvider", model: str):
        self._provider = provider
        self._model = model
    async def embed(self, texts: list[str]) -> list[list[float]]:
        return await self._provider.embed(texts, model=self._model)
    async def embed_one(self, text: str) -> list[float]:
        results = await self._provider.embed([text], model=self._model)
        return results[0] if results else []
```

File `ums/main.py`:
```python
import structlog
import uvicorn
from ums.config import settings

logger = structlog.get_logger()

def main():
    uvicorn.run(
        "ums.gateway.app:create_app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )

if __name__ == "__main__":
    main()
```

**Step 4: Run test to verify setup**
```
uv sync --all-extras && uv run python -c "from ums.config import settings; print('ok')"
```
Expected: prints `ok`

**Step 5: Create Makefile**
```makefile
.PHONY: install dev test lint

install:; uv sync --all-extras
dev:; uv run python -m ums.main
test:; uv run pytest tests/ -v --tb=short
test-unit:; uv run pytest tests/unit -v
test-component:; uv run pytest tests/component -v
test-e2e:; uv run pytest tests/integration -v
lint:; uv run ruff check . --fix && uv run mypy ums/
migrate:; uv run python scripts/migrate.py
distill:; uv run python scripts/run_distillation.py
```

**Step 6: Commit**
```bash
git init && git add -A && git commit -m "chore: scaffold UMS project with config, utils, and makefile"
```

---

### Task 2: Data Models

**Files:**
- Create: `ums/ums/models/__init__.py`
- Create: `ums/ums/models/observation.py`
- Create: `ums/ums/models/candidate.py`
- Create: `ums/ums/models/verified_memory.py`
- Create: `ums/ums/models/entity.py`
- Create: `ums/ums/models/relationship.py`
- Create: `ums/ums/models/belief.py`
- Create: `ums/ums/models/project.py`
- Create: `ums/ums/models/timeline.py`
- Create: `ums/ums/models/identity.py`
- Create: `ums/ums/models/reflection.py`
- Create: `ums/ums/models/distillation.py`
- Create: `ums/ums/models/audit.py`
- Create: `tests/unit/test_models.py`

**Interfaces:**
- Consumes: `ums.utils.datetime` (for `now_utc()`)
- Produces: All 12 Pydantic model classes used by every other task

**Model structure — each model is a Pydantic BaseModel with:**
- UUID `id` (default `uuid4()`)
- Confidence validated to [0.0, 1.0]
- Timestamps as ISO 8601 strings
- Forward-only stage transitions (via `set_stage`)
- No hard-delete (ARCHIVE/SUPERSEDE only)

**Step 1: Write the failing test**

File `tests/unit/test_models.py`:
```python
import pytest
from uuid import UUID
from ums.models.observation import Observation, ObservationStage, ObservationCategory
from ums.models.candidate import MemoryCandidate, CandidateStatus
from ums.models.verified_memory import VerifiedMemory, MemoryStatus
from ums.models.entity import Entity, EntityType
from ums.models.belief import Belief
from ums.models.timeline import TimelineEvent, EventType
from ums.models.audit import AuditLogEntry, AuditAction

class TestObservation:
    def test_create_minimal(self):
        obs = Observation(source="Claude", session_id="s-1",
                          raw_text="text", statement="User builds UMS", confidence=0.85)
        assert isinstance(obs.id, UUID)
        assert obs.stage == ObservationStage.PENDING

    def test_confidence_bounds(self):
        with pytest.raises(ValueError):
            Observation(source="T", session_id="s", raw_text="x",
                        statement="x", confidence=1.5)

class TestMemoryCandidate:
    def test_accumulating_by_default(self):
        c = MemoryCandidate(statement="x", confidence=0.5)
        assert c.status == CandidateStatus.ACCUMULATING

class TestVerifiedMemory:
    def test_links_to_candidate(self):
        from uuid import uuid4
        m = VerifiedMemory(statement="x", confidence=0.85, source_candidate_id=uuid4())
        assert m.status == MemoryStatus.ACTIVE
        assert m.version == 1

class TestAuditLogEntry:
    def test_create(self):
        from uuid import uuid4
        e = AuditLogEntry(action=AuditAction.CREATE, object_type="test", object_id=uuid4(), actor="test")
        assert e.id is not None
```

**Step 2: Create each model file following the data model spec**

Each model defined in `ums/models/` with:
- `from pydantic import BaseModel, Field, field_validator`
- `from ums.utils.datetime import now_utc`
- Enums for status/category fields
- `@field_validator("confidence")` ensuring 0.0-1.0
- Stage transitions as methods that prevent backward moves

**Step 3: Verify tests pass**
```
uv run pytest tests/unit/test_models.py -v
```
Expected: All tests PASS

**Step 4: Commit**
```bash
git add -A && git commit -m "feat: add all data models with validation"
```

---

### Task 3: Storage Interface ABCs

**Files:**
- Create: `ums/ums/storage/__init__.py`
- Create: `ums/ums/storage/interface.py`
- Create: `tests/unit/test_storage_interface.py`

**Interfaces:**
- Consumes: all model types
- Produces: `Storage` composite ABC (all interfaces combined into one class)

**Step 1: Create interface.py**

Define these ABCs in `ums/storage/interface.py`:
- `StorageInterface` — `initialize()`, `close()`, `health_check()`
- `GraphStoreInterface(StorageInterface)` — entity CRUD, relationship CRUD, verified memory CRUD, belief CRUD, candidate CRUD, identity model CRUD, project CRUD
- `TimelineStoreInterface(StorageInterface)` — `append_event()`, `get_events()`, `count_events()`
- `VectorStoreInterface(StorageInterface)` — `upsert_embedding()`, `search()`, `delete_embedding()`
- `CandidateQueueInterface(StorageInterface)` — `enqueue()`, `dequeue_batch()`, `requeue()`, `mark_processed()`, `get_pending_count()`, `get_by_stage()`
- `AuditLogInterface(StorageInterface)` — `append()`, `get_logs()`
- `Storage(*interfaces)` — composite with `pass`

All methods use `@abstractmethod`. Parameters use model types from `ums.models.*`.

**Step 2: Write and run tests**

Test that `Storage` has all expected methods and that no interface can be instantiated directly.

**Step 3: Commit**
```bash
git add -A && git commit -m "feat: add storage interface ABCs"
```

---

### Task 4: SQLite Storage Implementation

**Files:**
- Create: `ums/ums/storage/sqlite/__init__.py`
- Create: `ums/ums/storage/sqlite/connection.py`
- Create: `ums/ums/storage/sqlite/graph.py`
- Create: `ums/ums/storage/sqlite/timeline.py`
- Create: `ums/ums/storage/sqlite/vector.py`
- Create: `ums/ums/storage/sqlite/audit.py`
- Create: `ums/ums/storage/sqlite/migrations.py`
- Create: `tests/component/test_storage_sqlite.py`

**Interfaces:**
- Consumes: `Storage` interface ABCs, all model types, `config.settings`
- Produces: `SQLiteStorage` class implementing `Storage`

**Step 1: Create `connection.py` — `DatabaseManager` class**
- Wraps `aiosqlite` connection
- `initialize()` — opens connection, sets WAL mode + foreign keys, runs migrations
- `execute()`, `execute_many()`, `fetch_all()`, `fetch_one()`, `commit()`
- `_run_migrations()` — versioned migration table (`_migrations`)

**Step 2: Create `migrations.py` — list of (version, SQL) tuples**
All tables from schema design including indexes.

**Step 3: Create `graph.py` — `SQLiteGraphStore` implementing `GraphStoreInterface`**
- Serializes dict/list fields as JSON strings in SQLite
- Deserializes back when reading
- Uses `INSERT OR REPLACE` for upserts

**Step 4: Create `timeline.py` — `SQLiteTimelineStore`**
- Events stored with `when_ts` column for chronological ordering
- Filter support (user_id, date range, event type)

**Step 5: Create `audit.py` — `SQLiteAuditLog`**
- Append-only inserts

**Step 6: Create `vector.py` — `SQLiteVectorStore`** (Phase 1 stub)
- Methods are no-ops (vector search comes in Phase 2)

**Step 7: Create `__init__.py` — `SQLiteStorage` composite class**
```python
class SQLiteStorage(SQLiteGraphStore, SQLiteTimelineStore, SQLiteVectorStore, SQLiteAuditLog, Storage):
    def __init__(self, database_url: str):
        self._db = DatabaseManager(database_url)
        SQLiteGraphStore.__init__(self, self._db)
        SQLiteTimelineStore.__init__(self, self._db)
        SQLiteVectorStore.__init__(self, self._db)
        SQLiteAuditLog.__init__(self, self._db)
```

Also implement `enqueue`, `dequeue_batch`, `requeue`, `mark_processed`, `get_pending_count`, `get_by_stage` directly in `SQLiteStorage` (from `CandidateQueueInterface`), and `append`, `get_logs` (from `AuditLogInterface`).

**Step 8: Write component tests**
- Test each store against in-memory SQLite
- Verify CRUD operations, filtering, edge cases

**Step 9: Verify tests pass**
```
uv run pytest tests/component/test_storage_sqlite.py -v
```
Expected: All tests PASS

**Step 10: Commit**
```bash
git add -A && git commit -m "feat: implement SQLite storage backend with all interfaces"
```

---

### Task 5: LLM Provider & OpenRouter

**Files:**
- Create: `ums/ums/llm/__init__.py`
- Create: `ums/ums/llm/interface.py`
- Create: `ums/ums/llm/openrouter.py`
- Create: `ums/ums/llm/router.py`
- Create: `ums/ums/llm/prompts.py`

**Interfaces:**
- Consumes: `config.settings` (API key, model names)
- Produces: `LLMProvider` ABC, `OpenRouterProvider`, `ModelRouter`

**Step 1: Create `interface.py`**

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel

class LLMMessage(BaseModel):
    role: str
    content: str

class LLMResponse(BaseModel):
    content: str
    usage: Optional[dict] = None
    model: str
    provider: str

class LLMProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...
    @property
    @abstractmethod
    def default_model(self) -> str: ...
    @abstractmethod
    async def complete(self, messages: List[LLMMessage], model: Optional[str] = None,
                       temperature: float = 0.0, max_tokens: Optional[int] = None,
                       json_mode: bool = False) -> LLMResponse: ...
    @abstractmethod
    async def embed(self, texts: List[str], model: Optional[str] = None) -> List[List[float]]: ...
```

**Step 2: Create `openrouter.py`**

```python
from openai import AsyncOpenAI
from ums.config import settings
from ums.llm.interface import LLMProvider, LLMMessage, LLMResponse

class OpenRouterProvider(LLMProvider):
    def __init__(self):
        self._client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
        )
    @property
    def name(self) -> str: return "openrouter"
    @property
    def default_model(self) -> str: return settings.extraction_model

    async def complete(self, messages, model=None, temperature=0.0,
                       max_tokens=None, json_mode=False) -> LLMResponse:
        kwargs = dict(model=model or self.default_model,
                      messages=[m.model_dump() for m in messages],
                      temperature=temperature)
        if max_tokens: kwargs["max_tokens"] = max_tokens
        if json_mode: kwargs["response_format"] = {"type": "json_object"}
        response = await self._client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        return LLMResponse(content=choice.message.content or "",
                           usage=response.usage.model_dump() if response.usage else None,
                           model=response.model, provider=self.name)

    async def embed(self, texts, model=None) -> List[List[float]]:
        model = model or settings.embedding_model
        response = await self._client.embeddings.create(model=model, input=texts)
        return [d.embedding for d in response.data]
```

**Step 3: Create `router.py`**

```python
from ums.llm.interface import LLMProvider

class ModelRouter:
    def __init__(self, provider: LLMProvider):
        self._provider = provider
    @property
    def provider(self) -> LLMProvider:
        return self._provider
    def get(self, task: str) -> LLMProvider:
        return self._provider
```

**Step 4: Create `prompts.py`**

Functions returning lists of dict messages for entity extraction, observation extraction, and relationship extraction. Each uses system + user message format with JSON output instructions.

**Step 5: Create `llm/__init__.py`**
```python
from ums.llm.openrouter import OpenRouterProvider
from ums.llm.router import ModelRouter

def create_llm_router() -> ModelRouter:
    return ModelRouter(OpenRouterProvider())
```

**Step 6: Commit**
```bash
git add -A && git commit -m "feat: add LLM provider abstraction and OpenRouter implementation"
```
# Phase 1 Implementation Plan (Part 2: Tasks 6-10)

---

### Task 6: Observation Engine

**Files:**
- Create: `ums/ums/observation/__init__.py`
- Create: `ums/ums/observation/engine.py`
- Create: `ums/ums/observation/segmenter.py`
- Create: `ums/ums/observation/extractors.py`
- Create: `tests/component/test_observation_engine.py`

**Interfaces:**
- Consumes: `LLMProvider`, `Storage`, `config.settings`
- Produces: `ObservationEngine.process(source, conversation, session_id, metadata) -> UUID`

**Step 1: Create segmenter.py**

```python
import re
from typing import List

def segment_conversation(text: str, max_chunk_tokens: int = 4000) -> List[str]:
    if not text.strip():
        return []
    max_chars = max_chunk_tokens * 4
    if len(text) <= max_chars:
        return [text]
    segments = []
    current = ""
    for paragraph in re.split(r'\n\n+', text):
        candidate = current + ("\n\n" if current else "") + paragraph
        if len(candidate) > max_chars and current:
            segments.append(current)
            current = paragraph
        else:
            current = candidate
    if current:
        segments.append(current)
    return segments

def estimate_tokens(text: str) -> int:
    return len(text) // 4
```

**Step 2: Create extractors.py**

```python
import json, re
from typing import List, Optional
from ums.llm.interface import LLMProvider, LLMMessage
from ums.llm.prompts import entity_extraction_prompt, observation_extraction_prompt
from ums.models.observation import Observation, ObservationCategory, ObservationStage

def _parse_json_response(content: str) -> Optional[list]:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r'^```(?:json)?\s*', '', content)
        content = re.sub(r'\s*```$', '', content)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None

async def extract_entities(llm: LLMProvider, conversation: str, model: Optional[str] = None) -> List[dict]:
    messages = entity_extraction_prompt(conversation)
    response = await llm.complete(messages=[LLMMessage(**m) for m in messages], model=model, json_mode=True)
    result = _parse_json_response(response.content)
    return result if isinstance(result, list) else []

async def extract_observations(llm: LLMProvider, conversation: str, model: Optional[str] = None,
                                min_confidence: float = 0.4) -> List[Observation]:
    messages = observation_extraction_prompt(conversation)
    response = await llm.complete(messages=[LLMMessage(**m) for m in messages], model=model, json_mode=True)
    result = _parse_json_response(response.content)
    if not isinstance(result, list):
        return []
    observations = []
    for item in result:
        confidence = item.get("confidence", 0.0)
        if confidence < min_confidence:
            continue
        try:
            category = ObservationCategory(item.get("category", "FACT").upper())
        except ValueError:
            category = ObservationCategory.FACT
        obs = Observation(
            source="", session_id="", raw_text=conversation[:500],
            statement=item.get("statement", ""), confidence=confidence,
            category=category,
        )
        observations.append(obs)
    return observations
```

**Step 3: Create engine.py**

```python
import logging
from uuid import UUID, uuid4
from typing import Optional
from ums.llm.interface import LLMProvider
from ums.observation.segmenter import segment_conversation
from ums.observation.extractors import extract_observations
from ums.models.observation import ObservationStage
from ums.storage.interface import Storage

logger = logging.getLogger(__name__)

class ObservationEngine:
    def __init__(self, llm: LLMProvider, storage: Storage,
                 min_confidence: float = 0.4, max_observations: int = 50):
        self._llm = llm
        self._storage = storage
        self._min_confidence = min_confidence
        self._max_observations = max_observations

    async def process(self, source: str, conversation: str, session_id: str,
                      metadata: Optional[dict] = None) -> UUID:
        if not conversation.strip():
            raise ValueError("conversation is empty")
        if len(conversation.split()) < 10:
            raise ValueError("conversation too short (min 10 words)")
        metadata = metadata or {}
        job_id = uuid4()
        segments = segment_conversation(conversation)
        all_observations = []
        for segment in segments:
            observations = await extract_observations(
                self._llm, segment, min_confidence=self._min_confidence)
            for obs in observations:
                obs.source = source
                obs.session_id = session_id
                obs.metadata = metadata
                obs.set_stage(ObservationStage.QUEUED)
            all_observations.extend(observations)
            if len(all_observations) >= self._max_observations:
                break
        for obs in all_observations[:self._max_observations]:
            await self._storage.enqueue(obs)
        logger.info("observation_processed", job_id=str(job_id),
                    count=len(all_observations))
        return job_id
```

**Step 4: Write component tests**

Test with a mock LLM provider. Verify: observations are queued, low-confidence observations filtered, empty conversation raises error.

**Step 5: Commit**
```bash
git add -A && git commit -m "feat: implement observation engine with LLM extraction"
```

---

### Task 7: Memory Engine (Candidate Lifecycle)

**Files:**
- Create: `ums/ums/memory/__init__.py`
- Create: `ums/ums/memory/candidate.py`
- Create: `ums/ums/memory/deduplication.py`
- Create: `ums/ums/memory/contradiction.py`
- Create: `ums/ums/memory/promotion.py`
- Create: `tests/unit/test_deduplication.py`
- Create: `tests/unit/test_promotion.py`

**Interfaces:**
- Consumes: `Storage`, `config.settings`
- Produces: `MemoryEngine.process_observation(observation) -> MemoryCandidate`

**Step 1: Create deduplication.py**

```python
from ums.models.candidate import MemoryCandidate
from ums.models.observation import Observation

def semantic_similarity(text_a: str, text_b: str) -> float:
    if text_a == text_b:
        return 1.0
    if not text_a or not text_b:
        return 0.99 if not text_a and not text_b else 0.0
    a_grams = set(text_a.lower().split())
    b_grams = set(text_b.lower().split())
    if not a_grams or not b_grams:
        return 0.0
    return len(a_grams & b_grams) / len(a_grams | b_grams)

def is_duplicate(statement_a: str, statement_b: str, threshold: float = 0.85) -> bool:
    return semantic_similarity(statement_a, statement_b) >= threshold

def merge_observation_into_candidate(candidate: MemoryCandidate, observation: Observation,
                                     decay: float = 1.0) -> MemoryCandidate:
    from ums.memory.promotion import calculate_new_confidence
    from ums.utils.datetime import now_utc
    obs_ref = {"obs_id": str(observation.id), "source": observation.source,
               "statement": observation.statement, "confidence": observation.confidence}
    candidate.supporting_obs.append(obs_ref)
    candidate.confidence = calculate_new_confidence(candidate.confidence, observation.confidence, decay)
    candidate.last_updated = now_utc().isoformat()
    return candidate
```

**Step 2: Create contradiction.py**

```python
from typing import List, Tuple
from ums.models.candidate import MemoryCandidate, CandidateStatus
from ums.models.verified_memory import VerifiedMemory
from ums.memory.deduplication import semantic_similarity

CONTRADICTION_PAIRS = [
    ("likes", "dislikes"), ("prefers", "avoids"),
    ("is", "is not"), ("loves", "hates"),
    ("uses", "stopped using"), ("interested in", "not interested in"),
    ("good", "bad"), ("recommends", "advises against"),
]

def detect_contradiction(candidate: MemoryCandidate, existing_memories: List[VerifiedMemory],
                         threshold: float = 0.85) -> Tuple[bool, List[VerifiedMemory]]:
    conflicting = []
    for mem in existing_memories:
        sim = semantic_similarity(candidate.statement, mem.statement)
        a, b = candidate.statement.lower(), mem.statement.lower()
        has_pair = any((pos in a and neg in b) or (neg in a and pos in b) for pos, neg in CONTRADICTION_PAIRS)
        if sim >= threshold and has_pair:
            conflicting.append(mem)
    return len(conflicting) > 0, conflicting

def create_contradicted_candidate(candidate: MemoryCandidate,
                                   contradicting_memories: List[VerifiedMemory]) -> MemoryCandidate:
    candidate.status = CandidateStatus.CONTRADICTED
    candidate.notes = f"Contradicts {len(contradicting_memories)} memory(ies)"
    for mem in contradicting_memories:
        candidate.contradicting_obs.append({"memory_id": str(mem.id), "statement": mem.statement})
    return candidate
```

**Step 3: Create promotion.py**

```python
from typing import Tuple
from ums.models.candidate import MemoryCandidate, CandidateStatus
from ums.config import settings

def calculate_new_confidence(current: float, new_obs: float, decay: float = 1.0) -> float:
    if current <= 0.0:
        return min(new_obs, 1.0)
    result = 1 - (1 - current) * (1 - new_obs) * decay
    return min(max(result, 0.0), 1.0)

def check_promotion_eligibility(candidate: MemoryCandidate, min_confidence: float | None = None,
                                 min_evidence: int | None = None) -> Tuple[bool, str]:
    if candidate.status == CandidateStatus.PROMOTED:
        return False, "Already PROMOTED"
    threshold = min_confidence or candidate.promotion_threshold
    evidence_count = min_evidence or settings.min_evidence_for_promotion
    if candidate.confidence < threshold:
        return False, f"Confidence {candidate.confidence:.2f} < {threshold}"
    if len(candidate.supporting_obs) < evidence_count:
        return False, f"Evidence {len(candidate.supporting_obs)} < {evidence_count}"
    if candidate.status != CandidateStatus.ACCUMULATING:
        return False, f"Status {candidate.status} != ACCUMULATING"
    return True, ""
```

**Step 4: Create candidate.py (MemoryEngine)**

```python
import logging
from typing import Optional
from ums.storage.interface import Storage
from ums.models.observation import Observation
from ums.models.candidate import MemoryCandidate, CandidateStatus
from ums.models.verified_memory import VerifiedMemory, MemoryStatus
from ums.models.audit import AuditLogEntry, AuditAction
from ums.models.timeline import TimelineEvent, EventType
from ums.memory.deduplication import is_duplicate, merge_observation_into_candidate
from ums.memory.contradiction import detect_contradiction, create_contradicted_candidate
from ums.memory.promotion import check_promotion_eligibility
from ums.utils.datetime import now_utc

logger = logging.getLogger(__name__)

class MemoryEngine:
    def __init__(self, storage: Storage):
        self._storage = storage

    async def process_observation(self, observation: Observation) -> Optional[MemoryCandidate]:
        existing = await self._find_similar_candidate(observation)
        if existing:
            return await self._reinforce_candidate(existing, observation)
        return await self._create_candidate(observation)

    async def _find_similar_candidate(self, observation: Observation) -> Optional[MemoryCandidate]:
        candidates = await self._storage.find_candidates("default", status=CandidateStatus.ACCUMULATING.value)
        for cand in candidates:
            if is_duplicate(observation.statement, cand.statement, threshold=0.85):
                return cand
        return None

    async def _create_candidate(self, observation: Observation) -> MemoryCandidate:
        obs_ref = {"obs_id": str(observation.id), "source": observation.source,
                   "statement": observation.statement, "confidence": observation.confidence}
        candidate = MemoryCandidate(statement=observation.statement, category=observation.category,
                                     confidence=observation.confidence, supporting_obs=[obs_ref],
                                     status=CandidateStatus.ACCUMULATING)
        existing = await self._storage.find_all_verified_memories("default", limit=100)
        has_conflict, conflicting = detect_contradiction(candidate, existing)
        if has_conflict:
            candidate = create_contradicted_candidate(candidate, conflicting)
        await self._storage.upsert_candidate(candidate)
        return candidate

    async def _reinforce_candidate(self, candidate: MemoryCandidate, observation: Observation) -> MemoryCandidate:
        candidate = merge_observation_into_candidate(candidate, observation)
        eligible, reason = check_promotion_eligibility(candidate)
        if eligible:
            candidate = await self._promote_candidate(candidate)
        await self._storage.upsert_candidate(candidate)
        return candidate

    async def _promote_candidate(self, candidate: MemoryCandidate) -> MemoryCandidate:
        candidate.status = CandidateStatus.PROMOTED
        memory = VerifiedMemory(statement=candidate.statement, category=candidate.category,
                                 confidence=candidate.confidence, source_candidate_id=candidate.id,
                                 supporting_obs=candidate.supporting_obs, status=MemoryStatus.ACTIVE)
        await self._storage.upsert_verified_memory(memory)
        event = TimelineEvent(who="User", what=f"New memory: {candidate.statement[:100]}",
                               when=now_utc().isoformat(), event_type=EventType.CANDIDATE_PROMOTED,
                               references=[{"type": "verified_memory", "id": str(memory.id)}])
        await self._storage.append_event(event)
        audit = AuditLogEntry(action=AuditAction.PROMOTE, object_type="verified_memory",
                               object_id=memory.id, actor="MemoryEngine",
                               after={"statement": memory.statement, "confidence": memory.confidence})
        await self._storage.append(audit)
        logger.info("candidate_promoted", id=str(candidate.id))
        return candidate
```

**Step 5: Write and run unit tests**

Test deduplication (identical/similar/different texts), promotion eligibility (thresholds, evidence count, terminal status), and confidence calculation.

```
uv run pytest tests/unit/test_deduplication.py tests/unit/test_promotion.py -v
```
Expected: All PASS

**Step 6: Commit**
```bash
git add -A && git commit -m "feat: implement memory engine with candidate lifecycle"
```

---

### Task 8: Distillation Pipeline (Manual Trigger)

**Files:**
- Create: `ums/ums/distillation/__init__.py`
- Create: `ums/ums/distillation/pipeline.py`
- Create: `scripts/run_distillation.py`
- Create: `tests/component/test_distillation.py`

**Interfaces:**
- Consumes: `Storage`, `MemoryEngine`, `config.settings`
- Produces: `DistillationPipeline.run() -> DistillationCycle`

**Create pipeline.py:**

```python
import logging
from ums.storage.interface import Storage
from ums.memory.candidate import MemoryEngine
from ums.models.distillation import DistillationCycle, CycleStatus
from ums.utils.datetime import now_utc

logger = logging.getLogger(__name__)

class DistillationPipeline:
    def __init__(self, storage: Storage, memory_engine: MemoryEngine, batch_size: int = 10):
        self._storage = storage
        self._memory_engine = memory_engine
        self._batch_size = batch_size

    async def run(self) -> DistillationCycle:
        cycle = DistillationCycle(started_at=now_utc().isoformat(), status=CycleStatus.RUNNING)
        try:
            observations = await self._storage.dequeue_batch(self._batch_size)
            cycle.observations_read = len(observations)
            for obs in observations:
                try:
                    candidate = await self._memory_engine.process_observation(obs)
                    if candidate:
                        if candidate.status.value == "PROMOTED":
                            cycle.candidates_promoted += 1
                        elif candidate.status.value == "ACCUMULATING":
                            cycle.candidates_created += 1
                    await self._storage.mark_processed(obs.id)
                except Exception as e:
                    logger.error("obs_failed", error=str(e))
                    cycle.errors.append(str(e))
            cycle.status = CycleStatus.COMPLETED
            cycle.completed_at = now_utc().isoformat()
            cycle.summary = f"Processed {cycle.observations_read} obs: {cycle.candidates_created} created, {cycle.candidates_promoted} promoted"
        except Exception as e:
            cycle.status = CycleStatus.FAILED
            cycle.errors.append(str(e))
        return cycle
```

**Create `scripts/run_distillation.py`:**
```python
#!/usr/bin/env python3
import asyncio, structlog
from ums.config import settings
from ums.storage.sqlite import SQLiteStorage
from ums.memory.candidate import MemoryEngine
from ums.distillation.pipeline import DistillationPipeline

logger = structlog.get_logger()

async def main():
    storage = SQLiteStorage(settings.database_url)
    await storage.initialize()
    engine = MemoryEngine(storage)
    pipeline = DistillationPipeline(storage, engine)
    cycle = await pipeline.run()
    logger.info("result", status=cycle.status.value, obs=cycle.observations_read, promoted=cycle.candidates_promoted)

if __name__ == "__main__":
    asyncio.run(main())
```

**Commit:**
```bash
git add -A && git commit -m "feat: add distillation pipeline with manual CLI trigger"
```

---

### Task 9: Basic Recall Engine

**Files:**
- Create: `ums/ums/recall/__init__.py`
- Create: `ums/ums/recall/engine.py`
- Create: `ums/ums/recall/intent_parser.py`
- Create: `ums/ums/recall/loaders.py`
- Create: `ums/ums/recall/ranker.py`
- Create: `ums/ums/recall/assembler.py`
- Create: `tests/unit/test_ranker.py`
- Create: `tests/unit/test_intent_parser.py`

**Interfaces:**
- Consumes: `Storage`, `config.settings`
- Produces: `RecallEngine.recall(task, context) -> dict` (context object)

**Step 1: Create intent_parser.py**
```python
from dataclasses import dataclass, field
from typing import List, Optional
import re

@dataclass
class RecallIntent:
    type: str = "general"
    project: Optional[str] = None
    focus: List[str] = field(default_factory=lambda: ["preferences", "projects", "beliefs"])

def parse_intent(task: str) -> RecallIntent:
    if not task.strip():
        return RecallIntent()
    task_lower = task.lower()
    intent = RecallIntent()
    project_match = re.search(r'(?:project|repo|app)\s+["\']?([a-zA-Z0-9_-]+)', task_lower)
    if project_match:
        intent.project = project_match.group(1)
    if any(w in task_lower for w in ["review", "code", "debug", "fix", "implement"]):
        intent.type = "code_review"
    elif any(w in task_lower for w in ["what", "how", "explain", "tell me about"]):
        intent.type = "information"
    return intent
```

**Step 2: Create loaders.py**
```python
from typing import List
from ums.storage.interface import Storage
from ums.models.timeline import TimelineEvent

class RecallLoaders:
    def __init__(self, storage: Storage):
        self._storage = storage

    async def load_projects(self, user_id: str) -> List[dict]:
        memories = await self._storage.find_all_verified_memories(user_id, limit=50)
        projects = {}
        for m in memories:
            if m.category.value == "PROJECT":
                projects[m.statement] = {"name": m.statement, "confidence": m.confidence,
                                         "last_active": m.last_reinforced}
        return list(projects.values())

    async def load_beliefs(self, user_id: str, min_confidence: float = 0.5) -> List[dict]:
        beliefs = await self._storage.find_all_beliefs(user_id, min_confidence=min_confidence)
        return [{"statement": b.statement, "confidence": b.confidence,
                 "last_updated": b.last_updated, "status": b.status.value} for b in beliefs]

    async def load_timeline(self, user_id: str, limit: int = 10) -> List[dict]:
        events = await self._storage.get_events(user_id, limit=limit)
        return [{"what": e.what, "when": e.when, "where": e.where_app,
                 "type": e.event_type.value, "summary": e.summary} for e in events]
```

**Step 3: Create ranker.py**
```python
def score_relevance(confidence: float, recency_days: int = 0, keyword_score: float = 0.0) -> float:
    recency_factor = max(0.0, 1.0 - recency_days * 0.01)
    return min(1.0, confidence * 0.6 + recency_factor * 0.2 + keyword_score * 0.2)

def rank_and_deduplicate(items: list, dedup_key=None, limit: int = 20):
    seen = set()
    result = []
    for item in items:
        key = dedup_key(item) if dedup_key else item.get("id", item.get("statement", ""))
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result[:limit]
```

**Step 4: Create assembler.py**
```python
from typing import List
from ums.config import settings
from ums.recall.loaders import RecallLoaders

class ContextAssembler:
    def __init__(self, loaders: RecallLoaders):
        self._loaders = loaders

    async def assemble(self, user_id: str, project_filter: str | None = None,
                       focus: List[str] | None = None, max_tokens: int | None = None) -> dict:
        focus = focus or []
        max_tokens = max_tokens or settings.recall_max_tokens
        context = {"identity_summary": "", "relevant_beliefs": [],
                   "active_projects": [], "relevant_preferences": [],
                   "recent_timeline": [], "skills": [], "prompt_ready_summary": ""}

        if not focus or "projects" in focus:
            context["active_projects"] = await self._loaders.load_projects(user_id)

        if not focus or "beliefs" in focus:
            context["relevant_beliefs"] = await self._loaders.load_beliefs(user_id)

        timeline = await self._loaders.load_timeline(user_id, limit=10)
        context["recent_timeline"] = timeline

        lines = []
        if context["active_projects"]:
            lines.append("## Active Projects")
            for p in context["active_projects"][:3]:
                lines.append(f"- {p['name']} (confidence: {p['confidence']:.2f})")
        if context["relevant_beliefs"]:
            lines.append("## Relevant Beliefs")
            for b in context["relevant_beliefs"][:5]:
                lines.append(f"- {b['statement']} (confidence: {b['confidence']:.2f})")
        context["prompt_ready_summary"] = "\n".join(lines[:int(max_tokens / 20)])

        return context
```

**Step 5: Create engine.py**
```python
from typing import Optional, List
from ums.storage.interface import Storage
from ums.recall.intent_parser import parse_intent
from ums.recall.loaders import RecallLoaders
from ums.recall.ranker import score_relevance, rank_and_deduplicate
from ums.recall.assembler import ContextAssembler
from ums.config import settings

class RecallEngine:
    def __init__(self, storage: Storage):
        self._storage = storage
        self._loaders = RecallLoaders(storage)
        self._assembler = ContextAssembler(self._loaders)

    async def recall(self, task: str, context: Optional[dict] = None,
                     options: Optional[dict] = None) -> dict:
        context = context or {}
        options = options or {}
        intent = parse_intent(task)
        project = context.get("project") or intent.project
        focus = context.get("focus") or intent.focus
        user_id = "default"

        ctx = await self._assembler.assemble(
            user_id=user_id,
            project_filter=project,
            focus=focus,
            max_tokens=options.get("max_tokens", settings.recall_max_tokens),
        )

        return {
            "context": ctx,
            "retrieval_metadata": {
                "stages_used": ["intent", "projects", "beliefs", "timeline"],
                "returned": len(ctx.get("relevant_beliefs", [])),
            }
        }
```

**Step 6: Write and run unit tests**

Test intent parser (coding tasks, project detection, empty input), ranker (scoring, deduplication, limits).

```
uv run pytest tests/unit/test_ranker.py tests/unit/test_intent_parser.py -v
```
Expected: All PASS

**Step 7: Commit**
```bash
git add -A && git commit -m "feat: implement basic recall engine with multi-stage retrieval"
```

---

### Task 10: Gateway (FastAPI Routes + Auth)

**Files:**
- Create: `ums/ums/gateway/__init__.py`
- Create: `ums/ums/gateway/app.py`
- Create: `ums/ums/gateway/schemas.py`
- Create: `ums/ums/gateway/exceptions.py`
- Create: `ums/ums/gateway/middleware/__init__.py`
- Create: `ums/ums/gateway/middleware/auth.py`
- Create: `ums/ums/gateway/middleware/rate_limit.py`
- Create: `ums/ums/gateway/routes/__init__.py`
- Create: `ums/ums/gateway/routes/observe.py`
- Create: `ums/ums/gateway/routes/recall.py`
- Create: `ums/ums/gateway/routes/search.py` (stub)
- Create: `ums/ums/gateway/routes/timeline.py` (stub)
- Create: `ums/ums/gateway/routes/explain.py` (stub)
- Create: `ums/ums/gateway/routes/reflect.py` (stub)

**Interfaces:**
- Consumes: `ObservationEngine`, `RecallEngine`, `DistillationPipeline`, `Storage`, `config.settings`
- Produces: FastAPI application with all 6 routes + middleware

**Step 1: Create app.py**
```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from ums.config import settings
from ums.storage.sqlite import SQLiteStorage
from ums.llm.openrouter import OpenRouterProvider
from ums.observation.engine import ObservationEngine
from ums.memory.candidate import MemoryEngine
from ums.recall.engine import RecallEngine
from ums.distillation.pipeline import DistillationPipeline

class AppContext:
    def __init__(self):
        self.storage = SQLiteStorage(settings.database_url)
        self.llm = OpenRouterProvider()
        self.observation_engine = ObservationEngine(llm=self.llm, storage=self.storage,
                                                     min_confidence=settings.min_observation_confidence)
        self.memory_engine = MemoryEngine(storage=self.storage)
        self.recall_engine = RecallEngine(storage=self.storage)
        self.distillation = DistillationPipeline(storage=self.storage, memory_engine=self.memory_engine)

app_ctx = AppContext()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await app_ctx.storage.initialize()
    yield
    await app_ctx.storage.close()

def create_app() -> FastAPI:
    app = FastAPI(title="UMS Memory Gateway", version="0.1.0", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    from ums.gateway.routes import observe, recall, search, timeline, explain, reflect
    app.include_router(observe.router, prefix="/v1")
    app.include_router(recall.router, prefix="/v1")
    app.include_router(search.router, prefix="/v1")
    app.include_router(timeline.router, prefix="/v1")
    app.include_router(explain.router, prefix="/v1")
    app.include_router(reflect.router, prefix="/v1")

    @app.get("/health")
    async def health(): return {"status": "healthy"}

    return app
```

**Step 2: Create auth middleware.py**
```python
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import hashlib
import os

async def verify_api_key(request: Request, call_next):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"ok": False, "error": "unauthorized",
                                                       "message": "Missing or invalid API key"})
    # Phase 1: accept any non-empty key (full validation in Phase 5)
    token = auth[7:]
    if not token:
        return JSONResponse(status_code=401, content={"ok": False, "error": "unauthorized",
                                                       "message": "Invalid API key"})
    request.state.user_id = "default"
    response = await call_next(request)
    return response
```

**Step 3: Create route files**

Each route follows this pattern:
```python
from fastapi import APIRouter, Depends
from ums.gateway.app import app_ctx

router = APIRouter()

@router.post("/observe")
async def observe(body: dict):
    job_id = await app_ctx.observation_engine.process(
        source=body["source"], conversation=body["conversation"],
        session_id=body.get("metadata", {}).get("session_id", ""),
        metadata=body.get("metadata"),
    )
    return {"ok": True, "data": {"job_id": str(job_id), "status": "queued"}}

@router.post("/recall")
async def recall(body: dict):
    result = await app_ctx.recall_engine.recall(
        task=body["task"], context=body.get("context"), options=body.get("options"))
    return {"ok": True, "data": result}

@router.post("/search")
async def search(body: dict):
    return {"ok": True, "data": {"results": [], "total": 0}}  # Phase 2

@router.get("/timeline")
async def timeline(from_: str = None, to: str = None, project: str = None, limit: int = 50):
    events = await app_ctx.storage.get_events("default", from_ts=from_, to_ts=to,
                                                project=project, limit=limit)
    return {"ok": True, "data": {"events": [e.model_dump() for e in events]}}

@router.post("/explain")
async def explain(body: dict):
    return {"ok": True, "data": {}}  # Phase 3

@router.post("/reflect")
async def reflect(body: dict):
    return {"ok": True, "data": {"status": "not_implemented"}}  # Phase 4
```

**Step 4: Create schemas.py** — Pydantic request/response models matching 05_API_SPEC.md

**Step 5: Create exceptions.py** — Standard error response format

**Step 6: Write and run component tests**
Test that POST /v1/observe returns 202, POST /v1/recall returns context, auth rejects invalid keys, rate limiting works.

```
uv run pytest tests/component/test_gateway.py -v
```
Expected: All PASS

**Step 7: Commit**
```bash
git add -A && git commit -m "feat: add HTTP gateway with all 6 routes and auth middleware"
```

---

### Task 11: Integration Tests

**Files:**
- Create: `tests/integration/test_pipeline_e2e.py`
- Create: `tests/fixtures/conversations/coding_discussion.txt`
- Create: `tests/fixtures/expected_outputs/entities.json`
- Create: `tests/fixtures/expected_outputs/observations.json`
- Create: `scripts/migrate.py`
- Create: `scripts/create_user.py`
- Create: `scripts/seed_test_data.py`
- Create: `Dockerfile`
- Create: `docker-compose.yml`

**Step 1: Write E2E test**

Test covers: observe → distill → recall (basic memory loop), auth isolation, restart persistence, rate limiting.

```python
# tests/integration/test_pipeline_e2e.py
class TestPipelineE2E:
    async def test_observe_distill_recall_cycle(self, client):
        # 1. Submit conversation
        resp = await client.post("/v1/observe", json={
            "source": "Test", "conversation": "I'm building UMS. I prefer Python.",
            "metadata": {"project": "UMS"}
        })
        assert resp.status_code == 202
        # 2. Run distillation
        resp = await client.post("/v1/admin/distill")
        assert resp.status_code == 200
        # 3. Recall
        resp = await client.post("/v1/recall", json={"task": "Help with UMS"})
        assert resp.status_code == 200
        assert len(resp.json()["data"]["context"]["relevant_beliefs"]) > 0

    async def test_auth_isolation(self, client):
        # Without API key
        client.headers = {}
        resp = await client.post("/v1/observe", json={"source": "T", "conversation": "text"})
        assert resp.status_code == 401

    async def test_restart_persistence(self, client, tmp_path):
        # Use temp database, restart, verify data persists
        pass

    async def test_rate_limiting(self, client):
        for _ in range(101):
            resp = await client.post("/v1/observe", json={"source": "T", "conversation": "x" * 100})
        assert resp.status_code == 429

    async def test_empty_recall_returns_gracefully(self, client):
        resp = await client.post("/v1/recall", json={"task": "unknown project"})
        assert resp.status_code == 200
        assert len(resp.json()["data"]["context"]["relevant_beliefs"]) == 0
```

**Step 2: Create Dockerfile** (multi-stage: builder + slim runtime)

**Step 3: Create docker-compose.yml** (single service + volume mounts for data)

**Step 4: Create scripts** (migrate.py, create_user.py, seed_test_data.py)

**Step 5: Run phase gate verification**

| Gate | Test | How |
|------|------|-----|
| P1-G1 | observe 2000-token conversation → ≥3 observations | E2E test |
| P1-G2 | recall returns relevant project context | E2E test |
| P1-G3 | Memory persists across service restart | E2E test with temp DB |
| P1-G4 | No direct writes to verified_memory from observe | Unit test assertion |
| P1-G5 | Observe ack <200ms, recall <2s p95 | Load test (locust/k6) |

**Step 6: Commit**
```bash
git add -A && git commit -m "test: add integration tests and deployment scripts"
git add -A && git commit -m "chore: add Docker configuration for self-hosted deployment"
```
