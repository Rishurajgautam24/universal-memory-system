# Architecture Design Document
## Universal Memory System (UMS)

> **Version:** 1.0 · **Date:** 2026-07-29  
> **Status:** APPROVED FOR IMPLEMENTATION  
> **Note:** This document describes the *logical* architecture. Technology choices (graph DB, vector store, message queue) are intentionally deferred to the implementation phase.

---

## 1. Design Philosophy

### First Principle: Memory is Infrastructure

Memory is not a feature of an application. It is infrastructure that applications consume.
The relationship is identical to how applications use databases — they don't own the storage, they query it.

### First Principle: LLMs Are Noisy

People say things casually. LLMs misinterpret context. Not everything said in a conversation is true, important, or lasting.

**Therefore:** LLMs never write directly to memory. Every observation enters as a hypothesis (a Candidate) and must earn its way to permanence through reinforcement.

### First Principle: Memory Must Explain Itself

A system that says "you believe X" but cannot say "because of conversations Y, Z on date D" is not trustworthy.
Every belief must be traceable to its source evidence.

### First Principle: Memory Evolves Like a Human Mind

Humans don't immediately believe everything they hear. They hear something, it lingers, it gets reinforced or forgotten, and only after repeated exposure does it become a belief.
UMS is designed to mirror this cycle.

---

## 2. System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI APPLICATIONS                          │
│          Claude · Cursor · VSCode · ChatGPT · Gemini            │
│                Any application with HTTP or MCP                 │
└─────────────────────────┬───────────────────────────────────────┘
                           │  Memory SDK / MCP Protocol
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                     MEMORY GATEWAY                              │
│   /observe  /recall  /reflect  /search  /timeline  /explain     │
│         Single entry point · Authentication · Rate limiting      │
└──────┬───────────────┬───────────────┬───────────────┬──────────┘
       │               │               │               │
┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐ ┌────▼──────────┐
│  OBSERVATION│ │   RECALL    │ │  REFLECTION │ │  DISTILLATION │
│   ENGINE    │ │   ENGINE    │ │   ENGINE    │ │   ENGINE      │
│             │ │             │ │             │ │               │
│ Extract     │ │ Intent      │ │ Nightly     │ │ Async queue   │
│ Entities    │ │ Parse       │ │ self-review │ │ Merge + Dedup │
│ Observe     │ │ Multi-stage │ │ Belief      │ │ Promote       │
│ Candidate   │ │ Retrieval   │ │ refresh     │ │ candidates    │
│ Queue       │ │ Rank        │ │             │ │               │
└──────┬──────┘ └──────▲──────┘ └──────┬──────┘ └──────┬────────┘
       │               │               │               │
┌──────▼───────────────┴───────────────▼───────────────▼────────┐
│                    KNOWLEDGE ENGINE                             │
│                                                                 │
│   Memory Compiler Pipeline                                      │
│   Raw → Observation → Candidate → Verified → Graph → Belief    │
│                         → Identity Model                        │
└──────┬─────────────────────────────────────────┬───────────────┘
       │                                         │
┌──────▼──────────────────────────────────────────▼─────────────┐
│                      STORAGE LAYER                             │
│                                                                │
│     Graph Store        Timeline Store        Vector Store      │
│   (entities +         (ordered events)    (embedding index)    │
│   relationships)                                               │
└────────────────────────────────────────────────────────────────┘
```

---

## 3. Layer Specifications

### Layer 1: Memory Gateway

**Purpose:** Single, stable public contract. Hides all internal complexity from clients.

**Responsibilities:**
- Route incoming requests to the correct internal engine
- Authenticate and authorize clients
- Rate limit to prevent abuse
- Return uniform response schema regardless of internal changes

**Stability Contract:** The Gateway API is a public contract. Once released, any breaking change requires a major version bump and a deprecation period.

**Endpoints:**

| Endpoint | Description |
|---|---|
| `POST /observe` | Submit raw conversation for memory processing |
| `POST /recall` | Retrieve relevant memory context for a task |
| `POST /search` | Free-form search across all memory objects |
| `GET /timeline` | Retrieve chronological event history |
| `POST /explain` | Get the evidence chain behind a belief |
| `POST /reflect` | Trigger manual reflection (normally automatic) |

---

### Layer 2: Observation Engine

**Purpose:** Transform raw, unstructured conversation into structured, labelled observations.

**Input:**
```json
{
  "source": "Claude",
  "conversation": "<raw text>",
  "metadata": {
    "project": "UMS",
    "session_id": "abc123"
  }
}
```

**Processing Steps:**
1. Segment conversation into meaningful units
2. Extract named entities (people, tools, projects, technologies, concepts)
3. Extract explicit and implied facts
4. Extract relationships between entities
5. Generate observation statements in natural language
6. Assign initial confidence score to each observation
7. Write to Candidate Queue (never to permanent memory)

**Output (to Candidate Queue):**
```
Observation: "User is building a memory layer for AI applications"
Confidence: 0.85
Entities: [UMS, Memory Layer, AI]
Source: Claude · Session abc123 · 2026-07-29

Observation: "User believes vector search alone is insufficient for memory"
Confidence: 0.78
Entities: [Vector Search, Memory]
Source: Claude · Session abc123 · 2026-07-29
```

**Key Constraint:** This engine NEVER writes to the knowledge graph or permanent belief store directly.

---

### Layer 3: Memory Engine (Candidate System)

**Purpose:** Act as the gatekeeper between raw observation and permanent memory.

**The Candidate Lifecycle:**

```
New Information Arrives
        │
        ▼
  Create Candidate
  (Statement + Evidence + Confidence = Low)
        │
        ▼
  Observe Again? ──NO──► Candidate Expires (never promoted)
        │ YES
        ▼
  Accumulate Evidence
  (Confidence rises)
        │
  Threshold Met? ──NO──► Continue accumulating
        │ YES
        ▼
  Promote to Verified Memory
        │
        ▼
  Feed into Knowledge Graph
```

**Decision Logic:**

| Scenario | Action |
|---|---|
| Observation matches nothing | Create new Candidate |
| Observation matches existing Candidate | Increase confidence, add evidence |
| Observation matches Verified Memory | Reinforce, update timestamp |
| Observation contradicts Verified Memory | Flag contradiction, create competing Candidate |
| Observation is noise / trivial | Low confidence assigned, high expiry threshold |

---

### Layer 4: Distillation Engine

**Purpose:** Asynchronous background process that synthesizes candidates and updates the knowledge graph. Analogous to human sleep and memory consolidation.

**Operating Model:**
- Runs on a configurable schedule (default: every 4 hours)
- Reads from Observation Queue
- Does not block the Gateway

**Distillation Pipeline:**
```
Observation Queue (FIFO)
        │
        ▼
Merge related observations
        │
        ▼
Deduplicate semantically equivalent observations
        │
        ▼
Recalculate confidence for all affected candidates
        │
        ▼
Promote candidates that meet threshold
        │
        ▼
Update belief statements
        │
        ▼
Generate human-readable summary of cycle
        │
        ▼
Write to Knowledge Graph
        │
        ▼
Update embedding index
        │
        ▼
Log distillation event to Timeline
```

---

### Layer 5: Recall Engine

**Purpose:** Retrieve the most relevant memory context for a given task. This is NOT a search engine. It is a context assembly engine.

**Why multi-stage retrieval?**

A question like "Help me review this Python code for the UMS project" requires:
- Understanding intent (code review, not a factual question)
- Knowing which project is relevant (UMS)
- Knowing user's coding preferences and patterns
- Knowing recent project state (what was last worked on)
- Knowing related entities (Python, code quality, etc.)
- Only THEN doing semantic search for specific relevant memories

**Retrieval Pipeline:**
```
Input Query
        │
        ▼
1. Parse Intent
   (What kind of memory is needed?)
        │
        ▼
2. Identify Relevant Projects
   (Which active projects match?)
        │
        ▼
3. Load Relevant Beliefs
   (What does the user believe about this domain?)
        │
        ▼
4. Load Timeline Events
   (What has happened recently in this context?)
        │
        ▼
5. Load Relevant Documents / Observations
   (Keyword + entity matching)
        │
        ▼
6. Graph Traversal
   (Expand to related entities and relationships)
        │
        ▼
7. Embedding Search
   (Semantic similarity on residual candidates)
        │
        ▼
8. Rank + Deduplicate
   (Score by relevance, recency, confidence)
        │
        ▼
9. Assemble Context Object
   (Structured, ready for LLM injection)
```

---

### Layer 6: Reflection Engine

**Purpose:** Memory that asks questions about itself. Runs nightly without user prompting.

**Reflection Questions Run Automatically:**

```
What changed in the user's beliefs today?
What topics grew in importance this week?
What topics became less relevant?
Which projects progressed? Which stalled?
Which beliefs have been contradicted but not resolved?
What patterns are emerging across projects?
What skills or interests are developing?
Are there open questions that should be answered?
```

**Output:**
- Updated confidence scores for affected beliefs
- New timeline events capturing what changed
- A human-readable daily memory digest
- Archived versions of superseded beliefs

---

### Layer 7: Memory Compiler (Staged Promotion)

**Purpose:** Enforce the multi-stage pipeline. No information can skip stages.

**Compilation Pipeline:**

```
Stage 0: Raw Conversation
         (Unstructured text, not in memory system)
              │
              ▼
Stage 1: Observation
         (Extracted, labelled, confidence-scored)
              │
              ▼
Stage 2: Memory Candidate
         (Hypothesis with evidence links, not yet trusted)
              │
              ▼
Stage 3: Verified Memory
         (Promoted after sufficient evidence, confidence ≥ threshold)
              │
              ▼
Stage 4: Knowledge Graph Node/Edge
         (Structured as entity or relationship)
              │
              ▼
Stage 5: Belief
         (Synthesized across multiple graph nodes, has history)
              │
              ▼
Stage 6: Identity Model
         (Persistent, high-confidence beliefs that define who the user is)
```

**Compiler Invariants:**
- Every stage transition is logged with timestamp and trigger
- Any stage object can be inspected via the `explain` endpoint
- Information can only move forward (or be archived), never backward
- Archived beliefs remain readable but are marked superseded

---

## 4. Storage Layer (Abstract)

The storage layer is deliberately implementation-agnostic at this stage.
The knowledge engine interacts with storage only through well-defined interfaces.

**Three Logical Stores:**

| Store | Responsibility | Swappable? |
|---|---|---|
| **Graph Store** | Entities + relationships + belief links | Yes |
| **Timeline Store** | Ordered sequence of events | Yes |
| **Vector Store** | Embedding index for semantic search | Yes |

**Phase 1 Storage Guidance (without specifying technology):**
- Start simple. A file-based store or SQLite is acceptable for Phase 1.
- Prioritize correct data model over performance.
- Abstract behind an interface from day one so it can be swapped.

---

## 5. Cross-Cutting Concerns

### 5.1 Authentication Model
- Every client has a user-scoped API key
- All memory is isolated per user identity
- Admin API (separate port/auth) for management operations

### 5.2 Audit Log
- Every write to memory is logged: timestamp, source, stage, action
- Audit log is append-only
- Audit log is part of the portable export

### 5.3 Export Format
- All memory must be exportable as:
  - JSON (machine-readable, full fidelity)
  - Markdown (human-readable summary)
- Export includes: observations, candidates, verified memory, beliefs, timeline, identity model, audit log

### 5.4 LLM Abstraction
- All LLM calls are routed through a single internal `LLMProvider` interface
- Supports: OpenAI, Anthropic, local models (Ollama)
- Observation extraction quality may vary by model — this is expected

---

## 6. What This Architecture Intentionally Does NOT Do

| What | Why Not |
|---|---|
| Real-time streaming of memory updates | Complexity without clear benefit in v1 |
| Multi-user shared memory | Different trust model; deferred to future |
| LLM hosting | Not our responsibility; we call LLMs |
| Full-text search as primary retrieval | Insufficient; multi-stage recall is required |
| Automatic PII scrubbing | Important but deferred; manual controls in v1 |
