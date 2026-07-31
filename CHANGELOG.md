# Changelog

## [0.1.0] - 2026-07-30

### 🎉 Initial Release

The Universal Memory System (UMS) is now available as an open-source package!

### ✨ Features

- **Observation Engine** — Extract structured facts from raw conversations using LLMs
- **Memory Engine** — Evidence accumulation with candidate promotion/demotion lifecycle
- **Recall Engine** — Multi-stage context retrieval with intent parsing
- **Distillation Pipeline** — Async background processing for memory consolidation
- **REST API Gateway** — FastAPI-based with auth, rate limiting, and CORS
- **SQLite Storage** — Full graph, timeline, vector, and audit log storage
- **Vector Search** — Embedding-based semantic similarity search
- **OpenRouter Integration** — Model-agnostic LLM access
- **Comprehensive Test Suite** — 204+ tests across unit, component, and integration levels

### 🐛 Bug Fixes

- Fixed type mismatch in observation pipeline (Observation vs MemoryCandidate)
- Fixed auth bypass when API key is empty string
- Fixed invalid CORS configuration (allow_credentials with wildcard origin)
- Fixed missing `factory=True` in uvicorn configuration
- Fixed falsy bugs in promotion eligibility checks
- Fixed falsy bug in recall loaders confidence filtering
- Fixed inconsistent datetime format in deduplication
- Fixed missing database directory creation
- Fixed missing embeddings table in migrations
- Fixed vector store stub (was no-op)
- Fixed ranker not actually ranking items
- Fixed missing imports in graph store builder functions
- Fixed string vs enum comparison in recall loaders
- Fixed broken pagination in timeline endpoint
- Fixed .env file parsing (removed header line)

### 📦 Package

- Published to PyPI as `ums`
- Docker support with Dockerfile and docker-compose
- Comprehensive documentation with architecture diagrams
- GitHub issue templates for bugs and features
- CI/CD ready with GitHub Actions workflow