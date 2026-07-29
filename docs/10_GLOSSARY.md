# Glossary
## Universal Memory System (UMS)

> **Version:** 1.0 · **Date:** 2026-07-29  
> **Purpose:** Shared language across Product, Engineering, and Design.
> If a word is used in any other document in this folder, its definition is here.

---

> **Rule:** When in doubt, use the term from this glossary.
> Synonyms are listed but should not be used in documentation or code.

---

## A

**Alias**  
An alternative name for an Entity. For example, "Python" may have aliases ["python3", "py", "Python 3"]. The system resolves aliases to a single canonical entity.

**Audit Log**  
An append-only, immutable record of every write operation performed on memory. Each entry captures what changed, when, why, and which internal component made the change. Audit logs are always included in memory exports.

---

## B

**Belief**  
A high-confidence, synthesized proposition about the user, derived from multiple Verified Memories. Beliefs represent stances, preferences, and worldviews — not raw facts. Example: "User believes that vector search alone is insufficient for reliable AI memory."  
*Distinguish from:* Verified Memory (a single fact) and Observation (an unverified extraction).

**Belief Lifecycle**  
The progression of a Belief through states: ACTIVE → WEAKENING → ARCHIVED (or CONTRADICTED). Beliefs are never deleted.

---

## C

**Candidate**  
See *Memory Candidate.*

**Candidate Queue**  
The durable, ordered queue where Observations are placed after extraction. The Distillation Engine reads from this queue. Nothing in the Candidate Queue has been verified yet.

**Candidate Promotion**  
The act of moving a Memory Candidate from the `ACCUMULATING` state to `PROMOTED`, after which a Verified Memory is created. Promotion requires minimum confidence AND minimum independent evidence count.

**Compiler**  
See *Memory Compiler.*

**Confidence Score**  
A float between 0.0 and 1.0 representing the system's certainty that a piece of information is true and persistent. Confidence is never static — it rises with reinforcing evidence and decays with time or contradiction. No object is hard-trusted at confidence 1.0.

**Context Object**  
The structured output of a `recall()` call. Contains identity summary, relevant beliefs, active project state, recent timeline events, and preferences. Designed to be directly injectable into an LLM system prompt.

**Contradiction**  
A state where a new Observation or Candidate semantically opposes an existing Verified Memory or Belief. UMS does not resolve contradictions automatically — it surfaces them for the Reflection Engine.

---

## D

**Decay**  
The gradual reduction of a Belief's or Candidate's confidence over time when there is no recent reinforcing evidence. Mirrors how human memory fades without reinforcement.

**Distillation**  
The asynchronous background process that transforms raw Observations in the Candidate Queue into structured memory: merging, deduplicating, promoting Candidates, updating Beliefs, and writing to the Knowledge Graph.  
*Analogy:* Comparable to the human brain's memory consolidation during sleep.

**Distillation Cycle**  
One complete run of the Distillation Engine. Cycles run on a configurable schedule (default: every 4 hours). Each cycle produces a DistillationCycle log object.

**Distillation Engine**  
The internal service responsible for running Distillation Cycles. Operates asynchronously. Does not block the Gateway.

---

## E

**Entity**  
A named, identifiable thing in the user's world. Types include: PERSON, TOOL, PROJECT, TECHNOLOGY, CONCEPT, ORGANIZATION, SKILL, PLACE. Entities are the nodes in the Knowledge Graph.

**Entity Resolution**  
The process of detecting when two entities refer to the same thing (e.g., "PostgreSQL" and "Postgres") and merging them into a canonical entity with aliases.

**Evidence**  
One or more Observations that support a Memory Candidate or Verified Memory. The evidence chain is the full path from raw conversation to belief.

**Evidence Chain**  
The complete traceable path from a Belief back to the original Observations that created it. Accessible via the `explain` endpoint.

---

## G

**Gateway**  
See *Memory Gateway.*

**Knowledge Graph**  
The structured representation of entities and relationships derived from Verified Memory. Contains nodes (Entities) and edges (Relationships). One of the three components of the Storage Layer.

---

## I

**Identity Model**  
The top-level synthesis of a user's persistent, high-confidence Beliefs. Describes who the user is at the highest level of abstraction. Updated nightly by the Reflection Engine. Contains: core interests, skills, preferences, values, active projects, and an identity summary paragraph.

---

## L

**LLM Provider**  
An abstract interface through which all LLM API calls are made. Supports OpenAI, Anthropic, and local models (Ollama). No engine calls an LLM API directly — all calls go through this abstraction.

---

## M

**MCP (Model Context Protocol)**  
An open protocol for AI tools to call external services. UMS exposes an MCP Server as one of its client interfaces. MCP is an interface, not an architecture requirement.

**Memory**  
The system as a whole, and informally, any piece of information that has been stored at any stage (Observation, Candidate, Verified Memory, Belief, Identity Model).

**Memory Candidate**  
A hypothesis in the memory system. Created when an Observation contains information that doesn't match existing Verified Memory. Must accumulate sufficient evidence before being promoted. Never directly visible to end users unless they use the `explain` endpoint.

**Memory Compiler**  
The conceptual model for how information progresses through stages: Raw → Observation → Candidate → Verified → Graph → Belief → Identity Model. Each stage is a transformation. No stage can be skipped.

**Memory Engine**  
The internal service responsible for the Candidate lifecycle: creation, evidence accumulation, contradiction detection, and promotion.

**Memory Gateway**  
The single HTTP API that all clients (applications, SDKs, MCP tools) use to interact with UMS. Exposes exactly six endpoints. Hides all internal complexity.

**Memory OS / UMS**  
The project name. Universal Memory System. A persistent, portable, user-owned memory layer for AI applications.

---

## O

**Observation**  
The smallest meaningful unit of extracted information from a conversation. Produced by the Observation Engine. Human-readable statement about the user (e.g., "User is building a memory layer for AI applications"). NOT yet memory — it is an extracted hypothesis waiting to be evaluated.

**Observation Engine**  
The internal service that accepts raw conversations from the Gateway and produces Observations. Uses LLM calls for entity extraction, observation generation, and relationship extraction. Never writes directly to Verified Memory.

---

## P

**Pipeline**  
See *Memory Compiler.*

**Permanent Memory**  
Informal term for Verified Memory — information that has been promoted from the Candidate stage.

**Portable**  
The property that all memory can be exported in open formats (JSON, Markdown) and re-imported into any UMS instance. LLM switching does not affect portability.

**Project**  
A first-class object representing an ongoing body of work. Contains: name, status, current goal, recent work, open questions, and related entities. Projects are the most natural unit of context for AI assistance.

**Promotion**  
See *Candidate Promotion.*

---

## R

**Recall**  
The act of retrieving relevant memory context for a given task. Not a search — a multi-stage context assembly process that produces a structured Context Object.

**Recall Engine**  
The internal service that handles `recall()` requests via multi-stage retrieval: intent parsing → project lookup → belief retrieval → timeline lookup → graph traversal → embedding search → ranking.

**Reflection**  
The process of the system asking questions about its own memory: what changed, what grew, what became obsolete. Runs nightly without user prompting. Produces a Reflection object and a daily digest.

**Reflection Engine**  
The internal service responsible for nightly reflection cycles.

**Relationship**  
A typed, directed link between two Entities in the Knowledge Graph. Example: `User --[interested_in]--> GraphRAG`.

---

## S

**SDK**  
Software Development Kit. The client library that wraps the Memory Gateway HTTP API. Available in Python (`ums`) and TypeScript (`@ums/sdk`). Applications use SDKs instead of calling the API directly.

**Source**  
The application that submitted a conversation for observation. Examples: "Claude", "Cursor", "ChatGPT", "MyApp". Sources are recorded on every Observation and Verified Memory for traceability.

**Stage**  
One level in the Memory Compiler pipeline. Stages are: 0 (Raw), 1 (Observation), 2 (Candidate), 3 (Verified Memory), 4 (Knowledge Graph), 5 (Belief), 6 (Identity Model).

**Storage Layer**  
The abstract interface through which the Knowledge Engine reads and writes data. Contains three logical stores: Graph Store, Timeline Store, Vector Store. Swappable without changing higher layers.

---

## T

**Timeline**  
The chronological ordered sequence of events in a user's memory history. Contains events like: observation made, belief formed, project started, reflection run.

**Timeline Event**  
A single immutable record in the Timeline. Has fields: who, what, when, where, event_type, references.

---

## U

**User**  
The human whose memory UMS manages. All memory is isolated per user identity. The user owns all their memory.

**User Identity**  
The combination of API key + user identifier that scopes all memory operations. No cross-user access is possible.

---

## V

**Vector Store**  
The embedding index component of the Storage Layer. Used in Stage 7 of multi-stage recall (embedding search). Swappable — the recall pipeline does not depend on any specific vector database.

**Verified Memory**  
A piece of information that has been promoted from Candidate status after accumulating sufficient evidence. Trusted, permanent (until superseded), and linked to its full evidence chain.

---

## Concepts That Are NOT Used in This System

These terms are deliberately avoided in UMS documentation because they carry assumptions we reject:

| Avoided Term | Why Avoided | What We Use Instead |
|---|---|---|
| "Memory slot" | Implies fixed capacity | Memory grows organically |
| "Fact" | Implies binary truth | We use "Observation" or "Belief" with confidence |
| "Delete" | We don't delete | ARCHIVE or SUPERSEDE |
| "Overwrite" | We don't overwrite | VERSION with history |
| "Ground truth" | Nothing is ground truth | Everything has a confidence score |
| "Store" (as verb) | Implies immediate permanence | OBSERVE (queue for processing) |
