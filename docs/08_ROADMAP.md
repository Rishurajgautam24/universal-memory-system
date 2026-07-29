# Roadmap & Milestones
## Universal Memory System (UMS)

> **Version:** 1.0 · **Date:** 2026-07-29  
> **Status:** PLANNING

---

## Roadmap Philosophy

Each phase is independently deployable and delivers user value.
A user can stop at any phase and have something that works.
Each phase builds the foundation the next phase depends on.

**The sequence is non-negotiable.**  
Phase 2 cannot start until Phase 1 gates pass.  
Phase 3 cannot start until Phase 2 gates pass.  
(See `02_SUCCESS_CRITERIA.md` for gate definitions.)

---

## Overview

```
Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5
 Core         Graph      Distill    Reflect      SDKs &
 Memory       +           +          Engine     Connectors
 Server      Timeline   Confidence
```

---

## Phase 1: Core Memory Server

**Theme:** Make memory work end-to-end.

**What users get at the end of Phase 1:**
- A working local memory server
- The ability to `observe()` conversations from any client
- The ability to `recall()` relevant context for any task
- All observations treated as candidates (no noise in permanent memory)
- Memory that persists across restarts

**Deliverables:**

| # | Deliverable | Description |
|---|---|---|
| 1.1 | Memory Gateway | HTTP server with all six routes (stubs OK for non-Phase-1 features) |
| 1.2 | Observation Engine | LLM-based entity + observation extraction |
| 1.3 | Candidate Queue | Durable queue for observations |
| 1.4 | Memory Engine (basic) | Candidate creation and deduplication |
| 1.5 | Recall Engine (basic) | Simple retrieval: beliefs + projects + recent observations |
| 1.6 | Storage Layer v1 | File-based or SQLite storage behind abstract interface |
| 1.7 | LLM Provider abstraction | Support OpenAI and Anthropic; extendable |
| 1.8 | Authentication | API key per user, isolated storage |
| 1.9 | Audit Log | Append-only log for all writes |

**Phase 1 acceptance gates:** See `02_SUCCESS_CRITERIA.md` → Phase 1 Gate

**What is NOT in Phase 1:**
- Knowledge graph
- Timeline
- Distillation scheduler
- Reflection engine
- Embeddings / vector search
- SDKs

**Estimated Duration:** 4–6 weeks

---

## Phase 2: Knowledge Graph + Timeline + Hybrid Retrieval

**Theme:** Make memory structured and navigable.

**What users get at the end of Phase 2:**
- Named entities extracted and linked in a queryable graph
- A chronological timeline of memory events
- Significantly better recall quality (graph + embedding hybrid vs. keyword-only)
- The `timeline` endpoint is fully functional

**Deliverables:**

| # | Deliverable | Description |
|---|---|---|
| 2.1 | Entity Extraction | Named entity recognition in Observation Engine |
| 2.2 | Graph Store | Knowledge graph with entities and relationships |
| 2.3 | Entity Resolution | Deduplication and merging of aliases |
| 2.4 | Relationship Extraction | Extract typed links between entities |
| 2.5 | Embedding Index | Vector index for semantic similarity search |
| 2.6 | Hybrid Recall Engine | Multi-stage: intent → projects → beliefs → timeline → graph → embeddings |
| 2.7 | Timeline Store | Ordered event log with structured fields |
| 2.8 | `GET /v1/timeline` | Fully implemented with filters and pagination |
| 2.9 | Embedding refresh worker | Background job to keep vector index current |

**Phase 2 acceptance gates:** See `02_SUCCESS_CRITERIA.md` → Phase 2 Gate

**What is NOT in Phase 2:**
- Automatic distillation scheduler (manual trigger only)
- Confidence scoring over time (static after creation)
- Reflection engine
- SDKs

**Estimated Duration:** 4–6 weeks

---

## Phase 3: Distillation, Confidence Scoring, Candidate Promotion

**Theme:** Make memory trustworthy.

**What users get at the end of Phase 3:**
- Memory that automatically runs distillation every 4 hours
- Confidence scores that change over time as evidence accumulates
- Candidates that get promoted only after sufficient evidence
- Contradiction detection
- Memory decay for stale beliefs

**Deliverables:**

| # | Deliverable | Description |
|---|---|---|
| 3.1 | Distillation Scheduler | Cron job that runs every 4 hours |
| 3.2 | Confidence accumulation | Formula for confidence updates as evidence grows |
| 3.3 | Candidate promotion logic | Threshold-based promotion from Candidate → Verified Memory |
| 3.4 | Contradiction detection | Semantic comparison of new observations against existing memory |
| 3.5 | Memory decay | Confidence reduction for beliefs with no recent reinforcement |
| 3.6 | DistillationCycle logging | Metadata log for each cycle run |
| 3.7 | Deduplication | Merge semantically equivalent observations |
| 3.8 | `POST /v1/explain` | Full evidence chain for any belief or memory |

**Phase 3 acceptance gates:** See `02_SUCCESS_CRITERIA.md` → Phase 3 Gate

**What is NOT in Phase 3:**
- Reflection engine
- Identity Model generation
- SDKs

**Estimated Duration:** 4–6 weeks

---

## Phase 4: Reflection Engine + Proactive Memory

**Theme:** Make memory alive.

**What users get at the end of Phase 4:**
- Nightly self-reflection without any user prompting
- Daily memory digests
- Memory that notices when beliefs are weakening or obsolete
- An Identity Model — a synthesized description of who the user is
- Memory that detects patterns across projects

**Deliverables:**

| # | Deliverable | Description |
|---|---|---|
| 4.1 | Reflection Scheduler | Cron job running nightly at configurable time |
| 4.2 | Six reflection questions | Implemented and run automatically each night |
| 4.3 | Daily digest generation | Human-readable narrative summary |
| 4.4 | Belief lifecycle management | Weakening → Archived transitions |
| 4.5 | Pattern detection | Cross-project pattern identification |
| 4.6 | Identity Model | Synthesis of high-confidence long-standing beliefs |
| 4.7 | Identity Model update pipeline | Stage 5→6 from pipeline spec |
| 4.8 | `POST /v1/reflect` | Manual trigger with dry_run support |
| 4.9 | Reflection history | All Reflection objects stored and queryable |

**Phase 4 acceptance gates:** See `02_SUCCESS_CRITERIA.md` → Phase 4 Gate

**Estimated Duration:** 3–4 weeks

---

## Phase 5: SDKs + Connectors

**Theme:** Make memory accessible everywhere.

**What users get at the end of Phase 5:**
- Python SDK with `observe()` and `recall()` in <5 lines of code
- TypeScript/JavaScript SDK at feature parity
- MCP server for Claude Desktop integration
- Direct integrations with Cursor, VS Code, and OpenAI Responses API
- Documentation + quickstart guides

**Deliverables:**

| # | Deliverable | Description |
|---|---|---|
| 5.1 | Python SDK | `ums-python` package: observe, recall, search, timeline, explain, reflect |
| 5.2 | TypeScript SDK | `@ums/sdk` package: same methods |
| 5.3 | MCP Server | Exposes 6 tools: observe, recall, search, timeline, explain, reflect |
| 5.4 | Claude Desktop connector | Configuration + docs for Claude Desktop MCP integration |
| 5.5 | Cursor connector | VS Code extension or config integration |
| 5.6 | VS Code extension | Native VS Code integration |
| 5.7 | OpenAI Responses API connector | For apps using OpenAI tool calling |
| 5.8 | LangGraph integration | Node for use in LangGraph pipelines |
| 5.9 | Docker image | Single-command self-hosted deployment |
| 5.10 | Quickstart documentation | End-to-end setup guide (15 minutes to working) |
| 5.11 | Export / Import | Full memory export (JSON + Markdown) + import |

**Phase 5 acceptance gates:** See `02_SUCCESS_CRITERIA.md` → Phase 5 Gate

**Estimated Duration:** 6–8 weeks

---

## Total Estimated Timeline

| Phase | Duration | Cumulative |
|---|---|---|
| Phase 1 | 4–6 weeks | 4–6 weeks |
| Phase 2 | 4–6 weeks | 8–12 weeks |
| Phase 3 | 4–6 weeks | 12–18 weeks |
| Phase 4 | 3–4 weeks | 15–22 weeks |
| Phase 5 | 6–8 weeks | 21–30 weeks |

**~6–7 months to full v1.0.**

---

## What Comes After v1.0

These are NOT on the current roadmap. They are captured here to inform architecture decisions.

| Future Feature | Why Important | Why Not Now |
|---|---|---|
| Multi-user / team memory | Enterprises need shared context | Trust model is different; out of scope |
| Memory encryption at rest | Privacy requirement | Can be added without architecture change |
| Mobile SDK | iOS / Android apps need memory | Requires Phase 5 SDK first |
| Browser extension | Web apps need passive observation | Requires Phase 5 connector work |
| Voice input processing | Voice assistants | NLP preprocessing, out of scope v1 |
| PII auto-scrubbing | GDPR / privacy | Complex; manual controls in v1 are sufficient |
| Cloud-hosted UMS | SaaS offering | Self-hosted first; cloud is packaging, not architecture |
| Real-time collaboration | Pair programming with shared memory | Different concurrency model |

---

## Dependencies Between Phases

```
Phase 1: Candidate Queue ─────────────────────────────► Phase 3: Distillation
Phase 1: Storage Interface ───────────────────────────► All future phases
Phase 1: LLM Abstraction ─────────────────────────────► All future phases
Phase 1: Observation Engine ──────────────────────────► Phase 2: Entity Extraction
Phase 2: Embedding Index ─────────────────────────────► Phase 3: Deduplication
Phase 2: Knowledge Graph ─────────────────────────────► Phase 3: Belief Synthesis
Phase 3: Candidate Promotion ─────────────────────────► Phase 4: Reflection
Phase 3: Belief Lifecycle ────────────────────────────► Phase 4: Identity Model
Phase 4: Full Memory System ──────────────────────────► Phase 5: SDK + Connectors
```

---

## Milestone Review Process

At the end of each Phase:
1. Run all Phase gate acceptance tests (automated)
2. Manual review of memory quality on a real 30-day dataset
3. PM sign-off on gate criteria
4. Engineering review of technical debt incurred
5. Update roadmap if discoveries require scope adjustment

**No Phase begins until the previous Phase's gates pass.**
