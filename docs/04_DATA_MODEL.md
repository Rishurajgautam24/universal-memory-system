# Data Model Specification
## Universal Memory System (UMS)

> **Version:** 1.0 · **Date:** 2026-07-29  
> **Status:** DESIGN COMPLETE · Pending Engineering Review  
> **Note:** This specification describes logical objects and their fields. Physical storage schema (tables, documents, graph schemas) is an implementation concern derived from this spec.

---

## Guiding Principle

> Model the thing, not the storage.

Before deciding on databases, model what objects the system needs to think about.
Every field must earn its place by satisfying at least one functional requirement.

---

## Object Index

| Object | Layer | Description |
|---|---|---|
| [Observation](#1-observation) | Observation Engine | Single extracted insight from a conversation |
| [Memory Candidate](#2-memory-candidate) | Memory Engine | Unverified hypothesis waiting for evidence |
| [Verified Memory](#3-verified-memory) | Memory Engine | Promoted, trusted piece of information |
| [Entity](#4-entity) | Knowledge Engine | A named thing in the user's world |
| [Relationship](#5-relationship) | Knowledge Engine | A typed link between two entities |
| [Belief](#6-belief) | Knowledge Engine | A synthesized, high-confidence proposition |
| [Project](#7-project) | Knowledge Engine | An ongoing goal or body of work |
| [Timeline Event](#8-timeline-event) | Knowledge Engine | A moment in the user's history |
| [Identity Model](#9-identity-model) | Knowledge Engine | Persistent high-confidence self-description |
| [Reflection](#10-reflection) | Reflection Engine | Output of a nightly self-review cycle |
| [Distillation Cycle](#11-distillation-cycle) | Distillation Engine | Metadata about one processing run |
| [Audit Log Entry](#12-audit-log-entry) | Cross-cutting | Immutable record of a write to memory |

---

## 1. Observation

An Observation is the smallest meaningful unit produced by the Observation Engine.
It is NOT yet memory. It is a labelled insight waiting to be processed.

```
Observation {
  id               UUID             Unique identifier
  source           String           Which application sent the conversation (e.g., "Claude")
  session_id       String           Identifier of the originating conversation session
  timestamp        DateTime         When the observation was extracted (UTC)
  raw_text         String           The specific snippet from conversation that produced this
  statement        String           Human-readable observation (e.g., "User is building a memory layer")
  confidence       Float [0.0–1.0]  Extraction confidence assigned by the LLM
  entities         []EntityRef      References to entities mentioned (by ID or name)
  category         Enum             [PREFERENCE, PROJECT, BELIEF, FACT, ACTIVITY, RELATIONSHIP, SKILL]
  metadata         Map<String,Any>  Pass-through metadata from source (project name, tags, etc.)
  stage            Enum             [PENDING, QUEUED, PROCESSING, PROCESSED, EXPIRED]
  expires_at       DateTime?        Optional — when this observation auto-expires if not promoted
}
```

**Constraints:**
- `confidence` is set by the extraction LLM; it is never manually set by users
- `stage` transitions are one-way: PENDING → QUEUED → PROCESSING → PROCESSED (or EXPIRED)
- An Observation cannot be modified after creation — only its `stage` can change

---

## 2. Memory Candidate

A Memory Candidate is a hypothesis. It represents something that might be true about the user,
but has not yet accumulated enough evidence to be trusted.

```
MemoryCandidate {
  id                  UUID            Unique identifier
  statement           String          The proposed memory (e.g., "User prefers DuckDB for analytics")
  category            Enum            Same enum as Observation.category
  confidence          Float [0.0–1.0] Starts low; rises as evidence accumulates
  supporting_obs      []ObsRef        Observations that support this candidate
  contradicting_obs   []ObsRef        Observations that contradict this candidate
  affected_entities   []EntityRef     Entities involved in this candidate
  created_at          DateTime        When first created
  last_updated        DateTime        When confidence or evidence last changed
  promotion_threshold Float           Confidence level required for promotion (default: system config)
  status              Enum            [PENDING, ACCUMULATING, READY_FOR_PROMOTION, PROMOTED, EXPIRED, CONTRADICTED]
  expiry_date         DateTime?       Auto-expire if not reinforced by this date
  needs_review        Boolean         Flag for human review (optional, for future UI)
  notes               String?         Internal notes from the Distillation Engine
}
```

**Constraints:**
- A Candidate can only be in one status at a time
- `PROMOTED` is terminal — a promoted Candidate becomes a Verified Memory
- `EXPIRED` is terminal — expired Candidates are archived, not deleted
- `CONTRADICTED` means a competing Candidate exists with higher confidence

---

## 3. Verified Memory

A Verified Memory is a piece of information that has been promoted from Candidate status.
It is trusted, permanent (until superseded), and linked to its evidence chain.

```
VerifiedMemory {
  id                UUID            Unique identifier
  statement         String          The verified fact or belief
  category          Enum            Same enum as Observation.category
  confidence        Float [0.0–1.0] Current confidence (continues to update with reinforcement)
  source_candidate  CandidateRef    The promoted Candidate this came from
  supporting_obs    []ObsRef        All observations contributing to this memory
  entity_links      []EntityRef     Entities this memory relates to
  created_at        DateTime        When first promoted from Candidate
  last_reinforced   DateTime        When last supported by a new observation
  last_contradicted DateTime?       When last challenged by a contradicting observation
  status            Enum            [ACTIVE, SUPERSEDED, ARCHIVED]
  superseded_by     MemRef?         If SUPERSEDED, link to the newer memory that replaced it
  version           Integer         Incremented each time this memory is updated
  history           []MemoryVersion Full version history
}

MemoryVersion {
  version        Integer
  statement      String
  confidence     Float
  changed_at     DateTime
  change_reason  String
}
```

**Constraints:**
- Verified Memory is NEVER deleted — only SUPERSEDED or ARCHIVED
- The full version history is always preserved
- A SUPERSEDED memory is still queryable via the `explain` endpoint

---

## 4. Entity

An Entity is a named thing in the user's world. It is the building block of the knowledge graph.

```
Entity {
  id            UUID              Unique identifier
  type          Enum              [PERSON, TOOL, PROJECT, TECHNOLOGY, CONCEPT, ORGANIZATION, SKILL, PLACE]
  name          String            Primary canonical name (e.g., "Python")
  aliases       []String          Alternative names (e.g., ["python3", "py"])
  description   String            Auto-generated or user-provided description
  embedding     Vector            Semantic embedding for similarity search
  confidence    Float [0.0–1.0]   How confident we are this entity is real and relevant
  created_at    DateTime
  last_seen     DateTime          Last time this entity appeared in a conversation
  source_obs    []ObsRef          Observations that introduced or mentioned this entity
  attributes    Map<String,Any>   Flexible key-value attributes (e.g., {language: "Python", version: "3.12"})
  status        Enum              [ACTIVE, MERGED, DEPRECATED]
  merged_into   EntityRef?        If MERGED, the canonical entity
}
```

**Constraints:**
- Duplicate entities (same thing, different names) must be detected and merged
- Embedding is updated whenever the description or significant attributes change
- An entity is never deleted — only deprecated or merged

---

## 5. Relationship

A Relationship is a typed, directed link between two entities.

```
Relationship {
  id              UUID
  subject         EntityRef       The "from" entity
  predicate       String          The relationship type (e.g., "uses", "created", "interested_in", "prefers_over")
  object          EntityRef       The "to" entity
  confidence      Float [0.0–1.0]
  source_obs      []ObsRef        Observations that established or reinforced this relationship
  created_at      DateTime
  last_reinforced DateTime
  valid_from      DateTime?       Optional temporal scoping
  valid_until     DateTime?       Optional temporal scoping
  status          Enum            [ACTIVE, SUPERSEDED, ARCHIVED]
  context         String?         Optional natural language description of this relationship
}
```

**Example relationships:**
```
User --[interested_in]--> GraphRAG (confidence: 0.91)
User --[prefers_over]--> DuckDB, PostgreSQL (confidence: 0.62)
User --[is_building]--> UMS (confidence: 0.98)
UMS --[uses_concept]--> Memory Graph (confidence: 0.87)
```

---

## 6. Belief

A Belief is a synthesized, higher-order proposition. While a Verified Memory captures a single fact,
a Belief captures a stance, a preference, or a worldview — potentially spanning many memories.

```
Belief {
  id                    UUID
  statement             String          The belief (e.g., "User believes vector search is insufficient for reliable AI memory")
  confidence            Float [0.0–1.0]
  supporting_memories   []MemRef        Verified memories that support this belief
  contradicting_memories []MemRef       Verified memories that challenge this belief
  entity_links          []EntityRef
  created_at            DateTime
  last_updated          DateTime
  history               []BeliefVersion Full version history
  status                Enum            [ACTIVE, WEAKENING, CONTRADICTED, ARCHIVED]
  generated_by          Enum            [DISTILLATION, REFLECTION, MANUAL]
}

BeliefVersion {
  version         Integer
  statement       String
  confidence      Float
  changed_at      DateTime
  change_reason   String
  delta           Float       Confidence change from previous version (positive = stronger)
}
```

---

## 7. Project

A Project represents an ongoing body of work. It is a first-class object because
projects are the most natural unit of context for AI assistance.

```
Project {
  id                UUID
  name              String
  status            Enum          [ACTIVE, PAUSED, COMPLETED, ABANDONED]
  description       String        Auto-generated and updated description
  current_goal      String        The most recently understood goal
  recent_work       String        Summary of what was recently worked on
  open_questions    []String      Unresolved questions about this project
  related_entities  []EntityRef   Technologies, people, tools linked to this project
  timeline_events   []EventRef    Relevant timeline events
  related_beliefs   []BeliefRef   Beliefs that apply to this project
  created_at        DateTime
  last_active       DateTime
  inferred_from     []ObsRef      Observations that established or updated this project
  tags              []String
  metadata          Map<String,Any>
}
```

---

## 8. Timeline Event

A Timeline Event is an immutable record of something that happened.
It is the raw material for the timeline view.

```
TimelineEvent {
  id          UUID
  who         String          The actor (usually "User" but can be named if relevant)
  what        String          Human-readable description of what happened
  when        DateTime        Timestamp of the event (may differ from creation time)
  where       String?         Application context (e.g., "Claude", "Cursor")
  event_type  Enum            [OBSERVATION_MADE, BELIEF_FORMED, BELIEF_CHANGED, BELIEF_ARCHIVED,
                               PROJECT_STARTED, PROJECT_UPDATED, PROJECT_COMPLETED,
                               REFLECTION_RUN, DISTILLATION_RUN, CANDIDATE_PROMOTED,
                               MEMORY_EXPORTED]
  references  []Ref           Links to any relevant objects (observations, beliefs, projects)
  summary     String?         Auto-generated summary sentence
  created_at  DateTime        When the system recorded this event
}
```

---

## 9. Identity Model

The Identity Model is the top-level synthesis. It represents who the user is at the highest level of abstraction.
It is composed entirely of high-confidence, long-standing beliefs.

```
IdentityModel {
  id              UUID
  user_id         String          The user this identity belongs to
  last_updated    DateTime
  core_interests  []BeliefRef     High-confidence long-term interests
  skills          []BeliefRef     Established capabilities
  preferences     []BeliefRef     Consistent preferences (tools, methods, styles)
  values          []BeliefRef     Inferred values and worldview
  active_projects []ProjectRef    Currently active projects
  identity_summary String         A paragraph describing who this person is
  version         Integer
  generated_by    Enum            [DISTILLATION, REFLECTION]
}
```

---

## 10. Reflection

A Reflection is the output of one nightly reflection cycle.

```
Reflection {
  id              UUID
  run_at          DateTime
  period_start    DateTime        Start of the period examined
  period_end      DateTime        End of the period examined
  changed_beliefs []BeliefRef     Beliefs that changed during this period
  new_beliefs     []BeliefRef     Beliefs that were created
  archived_beliefs []BeliefRef    Beliefs that became obsolete
  project_updates []ProjectRef    Projects that progressed
  patterns_found  []String        Natural language patterns identified
  digest          String          Human-readable narrative summary
  trigger         Enum            [SCHEDULED, MANUAL]
}
```

---

## 11. Distillation Cycle

Metadata record for one distillation run.

```
DistillationCycle {
  id                  UUID
  started_at          DateTime
  completed_at        DateTime
  observations_read   Integer     Count of observations processed
  candidates_created  Integer
  candidates_promoted Integer
  candidates_expired  Integer
  beliefs_updated     Integer
  graph_nodes_updated Integer
  embeddings_updated  Integer
  summary             String      Human-readable summary of the cycle
  status              Enum        [RUNNING, COMPLETED, FAILED]
  errors              []String?   Any non-fatal errors encountered
}
```

---

## 12. Audit Log Entry

Every write to any memory object generates an immutable audit log entry.

```
AuditLogEntry {
  id          UUID
  timestamp   DateTime
  action      Enum        [CREATE, UPDATE, PROMOTE, ARCHIVE, SUPERSEDE, DELETE, EXPORT]
  object_type String      Which object type was affected
  object_id   UUID        ID of the affected object
  actor       String      What triggered this (e.g., "DistillationEngine", "ReflectionEngine", "API:observe")
  before      JSON?       Snapshot of object before the action (for UPDATE/SUPERSEDE)
  after       JSON        Snapshot of object after the action
  reason      String?     Human-readable reason for the action
}
```

**Constraints:**
- Audit log entries are NEVER modified or deleted
- The full audit log is included in memory exports
- Audit log is append-only at the storage level

---

## 13. Field Type Reference

| Type | Description |
|---|---|
| UUID | Universally Unique Identifier (v4) |
| DateTime | ISO 8601 UTC datetime string |
| Float [0.0–1.0] | Confidence score, inclusive of bounds |
| Enum | Defined set of string values — see individual objects |
| Vector | Floating-point array for embedding (dimension depends on model) |
| Map<String,Any> | Arbitrary key-value store for extensibility |
| Ref | A typed reference: `{ type: "ObsRef", id: UUID }` |

---

## 14. Cross-Object Invariants

1. Every Verified Memory MUST link to at least one Observation via its source Candidate.
2. Every Belief MUST link to at least one Verified Memory.
3. Every Identity Model MUST link to at least one Belief.
4. No object is ever hard-deleted — only ARCHIVED, MERGED, or SUPERSEDED.
5. Every object has a `created_at` timestamp.
6. Every stage transition generates an Audit Log Entry.
