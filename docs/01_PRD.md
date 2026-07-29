# Product Requirements Document (PRD)
## Universal Memory System (UMS)

> **Document Status:** APPROVED FOR DESIGN PHASE  
> **Version:** 1.0  
> **Date:** 2026-07-29  
> **Author:** Product Management  
> **Reviewers:** Engineering Lead, Architecture Lead

---

## 1. Executive Summary

Every AI application today has amnesia.

Claude doesn't know what you told ChatGPT. Cursor doesn't know what you told Claude. You re-explain yourself hundreds of times a year. Every new conversation starts from zero. Your context — your preferences, your projects, your beliefs, your growth — lives nowhere.

**Universal Memory System (UMS)** is a persistent, portable, user-owned memory layer that sits between you and every AI application you use. It is infrastructure — not an application. Like a database, every app can plug into it. Unlike a database, it thinks.

---

## 2. Problem Statement

### 2.1 The Core Problem

AI systems are stateless by default. Every session begins empty. Users are forced to:
- Re-introduce themselves and their context in every new session
- Maintain their own "system prompt" documents and manually paste them
- Accept that AI tools forget what they learned about the user
- Lose accumulated context when switching providers

### 2.2 Why Existing Solutions Fail

| Existing Approach | Why It Fails |
|---|---|
| App-level memory (ChatGPT Memory) | Siloed per app, not portable, opaque |
| System prompts | Manual, static, does not evolve, no evidence chain |
| RAG pipelines | Retrieval-only, no belief modeling, no synthesis |
| LLM context windows | Ephemeral, expensive, no persistence |
| Personal CRMs / Notion | Not AI-native, requires human curation |

### 2.3 The Root Cause

Memory has been treated as an **application feature** instead of **infrastructure**.

Nobody thinks of a relational database as belonging to a single app. Memory should be the same.

---

## 3. Vision

> **UMS becomes the memory layer that every AI application plugs into.**

One year from now, a new user installs UMS, connects Claude, Cursor, and ChatGPT, and from day one those applications know who they are — not because the apps stored anything, but because UMS did.

Two years from now, UMS is a standard interface. New AI tools advertise "UMS-compatible" the way apps advertise GDPR compliance.

---

## 4. Goals and Non-Goals

### 4.1 Goals

- **G1:** Provide a single, unified memory API that any AI application can call.
- **G2:** Accumulate, synthesize, and evolve memory without user intervention.
- **G3:** Ensure every memory is traceable to its source observations.
- **G4:** Make memory portable across LLM providers.
- **G5:** Keep memory ownership with the user at all times.
- **G6:** Surface memory that explains itself (beliefs with evidence chains).

### 4.2 Non-Goals (v1.0)

- **NG1:** We are NOT building another AI chat application.
- **NG2:** We are NOT providing LLM inference — we call LLMs, we don't host them.
- **NG3:** We are NOT a general-purpose vector database.
- **NG4:** We are NOT building team or multi-user shared memory (future phase).
- **NG5:** We are NOT replacing application-level context windows.

---

## 5. Target Users

### 5.1 Primary User: The Power AI User
- Uses 3+ AI tools weekly (Claude, ChatGPT, Cursor, Gemini, etc.)
- Builds projects across multiple sessions and tools
- Frustrated by context loss and repetitive re-introduction
- Technically comfortable enough to run a local service or connect via API

### 5.2 Secondary User: The Developer
- Building AI-powered applications
- Wants to avoid building memory themselves
- Wants to offer their users persistent, cross-app context
- Values open standards and composability

### 5.3 Future User: The Enterprise
- Wants team-level knowledge persistence (not in scope v1)
- Compliance requirements around data ownership
- Multi-user memory with access controls (not in scope v1)

---

## 6. Core Use Cases

### UC-1: Ambient Observation
A user has a conversation with Claude about a new project. UMS passively receives the conversation via the Claude integration, extracts observations, and adds them to the candidate queue. No user action required.

### UC-2: Contextual Recall
A user opens Cursor to work on a Python project. Cursor calls `recall()` with the current task context. UMS returns the most relevant beliefs, project state, preferences, and timeline events. Cursor uses this as system context.

### UC-3: Belief Evolution
User said "I prefer PostgreSQL" three months ago. Over time, conversations show increasing interest in DuckDB for analytics. UMS detects the shift, promotes a new belief, and archives the old one with a timestamp — without deleting history.

### UC-4: Explain Why
User asks "Why does UMS think I'm interested in Rust?" UMS returns the belief statement, confidence score, and the list of source observations with timestamps that led to it.

### UC-5: Timeline Reconstruction
User asks "What was I working on in March?" UMS returns a chronological summary of projects, key decisions, and belief changes from that period.

### UC-6: Proactive Reflection
Every night, UMS runs an internal reflection pass. It identifies what changed, what became more important, which projects stalled, and which beliefs are weakening. This information is distilled into the memory graph automatically.

---

## 7. Functional Requirements

### 7.1 Memory Gateway (Public API)

| Requirement ID | Requirement |
|---|---|
| FR-GW-01 | System SHALL expose a single HTTP API endpoint for all client interaction |
| FR-GW-02 | System SHALL support `observe`, `recall`, `reflect`, `search`, `timeline`, and `explain` operations |
| FR-GW-03 | System SHALL authenticate clients via API key scoped to a user identity |
| FR-GW-04 | System SHALL return deterministic, structured JSON responses |
| FR-GW-05 | System SHALL be provider-agnostic — no assumption about which LLM the client uses |

### 7.2 Observation Engine

| Requirement ID | Requirement |
|---|---|
| FR-OB-01 | System SHALL accept raw conversation text from any source |
| FR-OB-02 | System SHALL extract named entities (people, tools, projects, concepts) |
| FR-OB-03 | System SHALL generate human-readable observation statements |
| FR-OB-04 | System SHALL assign a confidence score to each observation |
| FR-OB-05 | System SHALL never write directly to permanent memory — all output is candidates |

### 7.3 Memory Engine (Candidate System)

| Requirement ID | Requirement |
|---|---|
| FR-ME-01 | System SHALL treat every new piece of information as a Memory Candidate |
| FR-ME-02 | System SHALL promote a Candidate to Verified Memory only after sufficient evidence |
| FR-ME-03 | System SHALL detect when a new observation contradicts an existing belief |
| FR-ME-04 | System SHALL accumulate evidence across multiple conversations before promoting |
| FR-ME-05 | System SHALL support belief revision (update confidence, archive history) |
| FR-ME-06 | System SHALL detect and deduplicate semantically equivalent observations |
| FR-ME-07 | System SHALL support memory decay for beliefs with no recent reinforcement |

### 7.4 Distillation Engine

| Requirement ID | Requirement |
|---|---|
| FR-DI-01 | System SHALL operate asynchronously via an observation queue |
| FR-DI-02 | System SHALL run distillation cycles on a configurable schedule (default: every 4 hours) |
| FR-DI-03 | System SHALL merge related observations into coherent belief updates |
| FR-DI-04 | System SHALL generate a human-readable summary of each distillation cycle |
| FR-DI-05 | System SHALL update the knowledge graph after each distillation cycle |

### 7.5 Recall Engine

| Requirement ID | Requirement |
|---|---|
| FR-RE-01 | System SHALL parse the intent of a recall query before searching |
| FR-RE-02 | System SHALL perform multi-stage retrieval: intent → projects → beliefs → timeline → documents → graph → embeddings |
| FR-RE-03 | System SHALL rank and merge results across retrieval stages |
| FR-RE-04 | System SHALL return a structured context object, not a raw document dump |
| FR-RE-05 | System SHALL support filtering recall by project, time range, or entity |

### 7.6 Reflection Engine

| Requirement ID | Requirement |
|---|---|
| FR-RF-01 | System SHALL run automatic nightly reflection without user prompting |
| FR-RF-02 | System SHALL detect: what changed, what grew in importance, what became obsolete, which projects progressed |
| FR-RF-03 | System SHALL update belief confidence scores based on reflection |
| FR-RF-04 | System SHALL generate a human-readable daily memory digest |
| FR-RF-05 | System SHALL store reflection results as timeline events |

### 7.7 Memory Compiler (Staged Promotion)

| Requirement ID | Requirement |
|---|---|
| FR-MC-01 | System SHALL enforce a multi-stage pipeline: Raw → Observation → Candidate → Verified → Graph → Belief → Identity |
| FR-MC-02 | System SHALL never skip stages |
| FR-MC-03 | System SHALL be able to explain which stage any piece of information is in |

---

## 8. Non-Functional Requirements

| Category | Requirement |
|---|---|
| **Latency** | `recall()` MUST return in under 2 seconds for the p95 case |
| **Latency** | `observe()` MUST acknowledge in under 200ms (processing is async) |
| **Portability** | All memory MUST be exportable as JSON or Markdown |
| **Privacy** | No memory data SHALL be sent to third parties without explicit user consent |
| **Explainability** | Every belief MUST link to its source observations |
| **Resilience** | Observation queue MUST survive service restarts without data loss |
| **Extensibility** | Storage layer MUST be swappable without changing higher layers |
| **Auditability** | Every write to memory MUST be logged with timestamp and source |

---

## 9. Constraints

- **No LLM lock-in:** The system must function with any LLM API. Initial implementation targets OpenAI and Anthropic but must be provider-abstracted.
- **No cloud dependency for core function:** Users must be able to run UMS locally. Cloud hosting is an option, not a requirement.
- **Open data format:** Memory must be stored in a format that a user can read without special tooling.

---

## 10. Dependencies

| Dependency | Type | Risk |
|---|---|---|
| LLM API (for extraction) | External | Medium — provider outages affect extraction |
| Embedding model | External or Local | Low — can fallback to keyword search |
| Storage backend | Internal | Low — abstracted behind storage layer |
| MCP protocol spec | External standard | Low — stable spec |

---

## 11. Out of Scope for v1.0

- Multi-user / shared memory
- Real-time collaboration
- Mobile applications
- Browser extension
- Voice input processing
- Memory encryption at rest (planned for v1.1)

---

## 12. Open Questions for Engineering

| ID | Question | Priority | Owner |
|---|---|---|---|
| OQ-01 | Which graph database do we start with — file-based, SQLite, or a real graph DB? | High | Arch |
| OQ-02 | What is the minimum confidence threshold for candidate promotion? | High | PM + Eng |
| OQ-03 | How do we handle PII in observations? (names, locations, etc.) | High | PM + Legal |
| OQ-04 | What is the distillation cycle interval in v1? | Medium | Eng |
| OQ-05 | Should the Reflection Engine be triggered by schedule or by observation count? | Medium | PM |
| OQ-06 | How do we version the memory schema for backward compatibility? | Medium | Arch |
