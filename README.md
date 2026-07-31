<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/your-org/ums/main/docs/assets/ums-logo-dark.svg">
  <img alt="UMS Logo" src="https://raw.githubusercontent.com/your-org/ums/main/docs/assets/ums-logo-light.svg" width="100%">
</picture>

# Universal Memory System (UMS)

> **Persistent memory layer for AI applications** — Give your AI assistants long-term memory, identity, and contextual awareness.

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-204%2F207%20passing-brightgreen)](https://github.com/your-org/ums/actions)
[![PyPI](https://img.shields.io/badge/pypi-v0.1.0-orange)](https://pypi.org/project/ums/)
[![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter-ff6b6b)](https://openrouter.ai/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688)](https://fastapi.tiangolo.com/)

---

## 🧠 What is UMS?

UMS is an **open-source memory infrastructure** that gives AI applications persistent, evolving memory. It's not another AI app — it's the **memory layer that every AI application plugs into**, like a database for identity, belief, and context.

### Why UMS?

| Problem | UMS Solution |
|---------|-------------|
| AI assistants forget everything between sessions | **Persistent memory** across conversations |
| LLMs hallucinate facts about users | **Evidence-based beliefs** with confidence scoring |
| No way to trace why an AI "knows" something | **Full audit trail** from observation to belief |
| Switching LLMs loses all context | **Model-agnostic** memory layer |
| Every app builds its own memory system | **One open standard** everyone can use |

---

## ✨ Features

- **🔍 Observation Engine** — Extract structured facts from raw conversations using any LLM
- **🧠 Memory Engine** — Evidence accumulation with candidate promotion/demotion
- **📚 Recall Engine** — Multi-stage context retrieval with intent parsing
- **⚡ Distillation Pipeline** — Async background processing for memory consolidation
- **🔗 Graph Store** — Entity-relationship knowledge graph
- **📊 Timeline** — Chronological event history with pagination
- **🔐 Audit Log** — Append-only, full-fidelity audit trail
- **🔌 REST API Gateway** — FastAPI-based with auth, rate limiting, CORS
- **🔎 Vector Search** — Embedding-based semantic similarity search
- **🔄 Model Agnostic** — Works with OpenAI, Anthropic, local models via OpenRouter

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI APPLICATIONS                          │
│          Claude · Cursor · VSCode · ChatGPT · Gemini            │
└─────────────────────────┬───────────────────────────────────────┘
                          │  HTTP REST API
                          │
┌─────────────────────────▼──────────────────────────────────────┐
│                     MEMORY GATEWAY                              │
│   /observe  /recall  /reflect  /search  /timeline  /explain     │
│         Single entry point · Auth · Rate limiting                │
└──────┬───────────────┬───────────────┬───────────────┬──────────┘
       │               │               │               │
┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐ ┌────▼──────────┐
│  OBSERVATION│ │   RECALL    │ │  REFLECTION │ │  DISTILLATION │
│   ENGINE    │ │   ENGINE    │ │   ENGINE    │ │   ENGINE      │
└──────┬──────┘ └──────▲──────┘ └──────┬──────┘ └──────┬────────┘
       │               │               │               │
┌──────▼───────────────┴───────────────▼───────────────▼────────┐
│                    KNOWLEDGE ENGINE                             │
│   Raw → Observation → Candidate → Verified → Graph → Belief    │
└──────┬─────────────────────────────────────────┬───────────────┘
       │                                         │
┌──────▼──────────────────────────────────────────▼─────────────┐
│                      STORAGE LAYER                             │
│     Graph Store        Timeline Store        Vector Store      │
└────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Conversation
    │
    ▼
┌─────────────┐     ┌──────────────┐     ┌────────────┐     ┌──────────┐
│  LLM        │────▶│  Observation │────▶│  Candidate  │────▶│ Verified │
│  Extraction │     │  (Stage 1)   │     │  (Stage 2)  │     │  Memory  │
└─────────────┘     └──────────────┘     └────────────┘     │ (Stage 3)│
                                                            └────┬─────┘
                                                                 │
                                                            ┌────▼─────┐
                                                            │  Belief   │
                                                            │ (Stage 5) │
                                                            └──────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- An OpenRouter API key (or any OpenAI-compatible API)

### Installation

```bash
# Install from PyPI
pip install ums

# Or install from source
git clone https://github.com/your-org/ums.git
cd ums
pip install -e ".[dev]"
```

### Configuration

Create a `.env` file:

```env
# Required
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Models (optional - defaults shown)
EXTRACTION_MODEL=openai/gpt-4o-mini
SYNTHESIS_MODEL=openai/gpt-4o
EMBEDDING_MODEL=openai/text-embedding-3-small

# Server (optional)
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite+aiosqlite://data/ums.db

# Security (highly recommended for production)
ADMIN_API_KEY=your-secret-api-key
```

### Start the Server

```bash
# Using the CLI
ums serve

# Or directly with uvicorn
uvicorn ums.gateway.app:create_app --host 0.0.0.0 --port 8000 --factory
```

### Quick Test

```bash
# Health check
curl http://localhost:8000/health

# Observe a conversation
curl -X POST http://localhost:8000/v1/observe \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "source": "Claude",
    "conversation": "I prefer Python for backend development and PostgreSQL for databases.",
    "metadata": {"session_id": "test-1"}
  }'

# Recall what was learned
curl -X POST http://localhost:8000/v1/recall \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "task": "What are my technology preferences?"
  }'
```

---

## 📖 API Reference

### `POST /v1/observe` — Submit conversation for memory processing

```json
{
  "source": "Claude",
  "conversation": "Raw conversation text...",
  "metadata": {
    "session_id": "abc-123",
    "project": "my-project"
  }
}
```

**Response:** `202 Accepted`
```json
{
  "ok": true,
  "data": {
    "job_id": "uuid",
    "status": "queued",
    "estimated_processing_ms": 3000
  }
}
```

### `POST /v1/recall` — Retrieve memory context

```json
{
  "task": "Help me review this Python code",
  "context": {
    "project": "UMS",
    "focus": ["beliefs", "projects"]
  },
  "options": {
    "max_tokens": 2000
  }
}
```

### `GET /v1/timeline` — Get event history

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 50 | Events per page (max 200) |
| `page` | int | 1 | Page number |
| `from` | string | - | Start date (ISO 8601) |
| `to` | string | - | End date (ISO 8601) |

### `POST /v1/search` — Semantic search

```json
{
  "query": "Python backend preferences",
  "filters": {"project": "UMS"}
}
```

### `POST /v1/explain` — Get evidence chain

```json
{
  "target_id": "uuid",
  "target_type": "belief"
}
```

### `POST /v1/reflect` — Trigger memory consolidation

```json
{}
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=ums --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/component/
pytest tests/integration/
```

---

## 📦 Project Structure

```
ums/
├── ums/                          # Main package
│   ├── gateway/                  # FastAPI REST API
│   │   ├── routes/               # API endpoints
│   │   ├── middleware/            # Auth, rate limiting
│   │   ├── app.py                # FastAPI application
│   │   ├── schemas.py            # Pydantic request/response models
│   │   └── exceptions.py         # Custom exceptions
│   ├── observation/              # Observation engine
│   │   ├── engine.py             # Main processing pipeline
│   │   ├── extractors.py         # LLM-based extraction
│   │   └── segmenter.py          # Text segmentation
│   ├── memory/                   # Memory engine
│   │   ├── candidate.py          # Candidate lifecycle
│   │   ├── deduplication.py      # Semantic dedup
│   │   ├── promotion.py          # Candidate promotion
│   │   └── contradiction.py      # Contradiction detection
│   ├── recall/                   # Recall engine
│   │   ├── engine.py             # Context retrieval
│   │   ├── assembler.py          # Context assembly
│   │   ├── intent_parser.py      # Query intent parsing
│   │   ├── loaders.py            # Data loaders
│   │   └── ranker.py             # Relevance ranking
│   ├── distillation/             # Distillation pipeline
│   │   └── pipeline.py           # Async processing
│   ├── llm/                      # LLM abstraction
│   │   ├── interface.py          # Abstract provider
│   │   ├── openrouter.py         # OpenRouter implementation
│   │   ├── prompts.py            # LLM prompts
│   │   └── router.py             # Model routing
│   ├── models/                   # Pydantic data models
│   │   ├── observation.py        # Observation model
│   │   ├── candidate.py          # MemoryCandidate model
│   │   ├── verified_memory.py    # VerifiedMemory model
│   │   ├── belief.py             # Belief model
│   │   ├── entity.py             # Entity model
│   │   ├── relationship.py       # Relationship model
│   │   ├── timeline.py           # TimelineEvent model
│   │   ├── audit.py              # AuditLogEntry model
│   │   ├── identity.py           # Identity model
│   │   ├── project.py            # Project model
│   │   ├── reflection.py         # Reflection model
│   │   └── distillation.py       # Distillation models
│   ├── storage/                  # Storage layer
│   │   ├── interface.py          # Abstract storage interface
│   │   └── sqlite/               # SQLite implementation
│   │       ├── connection.py     # Database connection
│   │       ├── migrations.py     # Schema migrations
│   │       ├── graph.py          # Graph store
│   │       ├── timeline.py       # Timeline store
│   │       ├── vector.py         # Vector store
│   │       └── audit.py          # Audit log
│   ├── utils/                    # Utilities
│   │   ├── datetime.py           # Date/time helpers
│   │   ├── embeddings.py         # Embedding service
│   │   └── similarity.py         # Similarity functions
│   ├── config.py                 # Settings management
│   └── main.py                   # CLI entry point
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   ├── component/                # Component tests
│   └── integration/              # Integration tests
├── scripts/                      # Utility scripts
├── docs/                         # Documentation
├── pyproject.toml                # Project configuration
├── Dockerfile                    # Docker support
└── docker-compose.yml            # Docker Compose
```

---

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t ums .
docker run -p 8000:8000 --env-file .env ums
```

---

## 📦 Publishing to PyPI

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Upload to PyPI
twine upload dist/*

# Or upload to Test PyPI first
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

### CI/CD with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI
on:
  release:
    types: [published]
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install build twine
      - run: python -m build
      - run: twine upload dist/* -u __token__ -p ${{ secrets.PYPI_TOKEN }}
```

---

## 🔧 Integration Guide

### With Python Applications

```python
import httpx

class UMSClient:
    def __init__(self, base_url: str, api_key: str):
        self.client = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"}
        )

    def observe(self, source: str, conversation: str, **metadata):
        return self.client.post("/v1/observe", json={
            "source": source,
            "conversation": conversation,
            "metadata": metadata
        })

    def recall(self, task: str, **context):
        return self.client.post("/v1/recall", json={
            "task": task,
            "context": context
        })

# Usage
ums = UMSClient("http://localhost:8000", "your-api-key")
ums.observe("Claude", "I love Python for backend development")
result = ums.recall("What are my tech preferences?")
```

### With JavaScript/TypeScript

```typescript
class UMSClient {
  private client: any;

  constructor(baseUrl: string, apiKey: string) {
    this.client = fetch.create({
      baseURL: baseUrl,
      headers: { Authorization: `Bearer ${apiKey}` }
    });
  }

  async observe(source: string, conversation: string, metadata?: any) {
    return this.client.post("/v1/observe", { source, conversation, metadata });
  }

  async recall(task: string, context?: any) {
    return this.client.post("/v1/recall", { task, context });
  }
}
```

### With Claude/Cursor/VSCode

Add to your AI tool's system prompt:

```
You have access to a memory system at http://localhost:8000.
Use POST /v1/observe to save information about the user.
Use POST /v1/recall to retrieve relevant context before answering.
```

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone and install
git clone https://github.com/your-org/ums.git
cd ums
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .

# Type check
mypy ums
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🌟 Support

- [Documentation](docs/00_README.md)
- [Issue Tracker](https://github.com/your-org/ums/issues)
- [Discussions](https://github.com/your-org/ums/discussions)

---

<p align="center">
  <b>Built with ❤️ for the AI community</b><br>
  <i>Memory should be infrastructure, not a feature.</i>
</p>