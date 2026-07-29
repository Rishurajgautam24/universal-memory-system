# Internal Pipeline Specification
## Universal Memory System (UMS)

> **Version:** 1.0 · **Date:** 2026-07-29  
> **Audience:** Engineering  
> **Status:** DESIGN COMPLETE

---

## Overview

The internal pipeline is the path that information travels from raw conversation to permanent memory.
It is a compiler — information passes through multiple transformation stages.
No stage can be skipped. No information can write to a later stage without passing through all earlier ones.

---

## Stage 0 → 1: Raw Conversation → Observation

**Trigger:** Client calls `POST /v1/observe`

**Owner:** Observation Engine

**Inputs:**
- `source` (string): Which application sent this
- `conversation` (string): Raw text
- `metadata` (object): Pass-through context

**Processing:**

```
Step 1: Pre-processing
  - Strip PII markers (v1: flag only, don't remove)
  - Chunk conversation into semantic segments
  - Detect language (default: English)
  - Estimate token count for LLM call budgeting

Step 2: Entity Extraction (LLM call #1)
  Prompt the LLM to identify:
    - People mentioned
    - Tools / technologies referenced
    - Projects mentioned
    - Concepts discussed
    - Organizations named
  Output: []EntityExtraction { name, type, aliases, confidence }

Step 3: Fact & Observation Extraction (LLM call #2)
  Prompt the LLM to generate observation statements:
    - Observations must be in the form: "User [verb] [subject]"
    - Each observation gets a confidence score
    - Category is assigned (PREFERENCE / BELIEF / ACTIVITY / etc.)
  Output: []ObservationStatement { statement, confidence, category, entity_refs, raw_excerpt }

Step 4: Relationship Extraction (LLM call #3, optional)
  Prompt the LLM to identify:
    - Explicit relationships between extracted entities
    - Implied relationships
  Output: []RelationshipExtraction { subject, predicate, object, confidence }

Step 5: Write Observations to Queue
  For each extracted observation:
    - Create Observation object (see Data Model)
    - Set stage = QUEUED
    - Write to Candidate Queue
    - Do NOT touch any other memory store
```

**Output:** N Observation objects in the Candidate Queue

**Constraints:**
- If LLM is unavailable: queue the raw conversation with stage = PENDING (retry when available)
- Minimum confidence threshold: configurable (default 0.4) — observations below threshold are discarded
- Maximum observations per conversation: 50 (prevent noise floods)
- LLM calls MUST be idempotent — same input must produce equivalent (not identical) output

---

## Stage 1 → 2: Observation → Memory Candidate

**Trigger:** Distillation Engine pickup from Candidate Queue

**Owner:** Memory Engine (runs inside Distillation Engine)

**For each Observation in the queue:**

```
Step 1: Semantic Deduplication
  - Embed the observation statement
  - Search existing Candidates for semantic similarity > 0.85
  - If match found: this is a duplicate observation → go to Step 2a
  - If no match: this is a new candidate → go to Step 2b

Step 2a: DUPLICATE — Reinforce existing Candidate
  - Add this Observation to the Candidate's supporting_obs list
  - Recalculate confidence:
      new_confidence = 1 - (1 - current_confidence) * (1 - new_obs_confidence) * decay_factor
  - Update last_updated timestamp
  - Check if promotion threshold is now met (go to Stage 2 → 3 if yes)

Step 2b: NEW — Check for Contradictions
  - Search Verified Memory for semantically opposing statements
  - If contradiction found:
      - Create Candidate with status = CONTRADICTED
      - Link to the contradicting Verified Memory
      - Flag for reflection review
  - If no contradiction:
      - Create new Candidate with initial confidence = observation.confidence
      - Set status = ACCUMULATING
      - Set expiry_date = now + 30 days (default)

Step 3: Entity Resolution
  - For each entity reference in the Observation:
    - Check if entity already exists (by name + aliases)
    - If yes: link Candidate to existing entity, update last_seen
    - If no: create new Entity with status = ACTIVE

Step 4: Relationship Processing
  - Create or reinforce relationships between entities
  - Apply same confidence accumulation formula as candidates
```

**Output:** Candidates created or updated, Entities created or updated

---

## Stage 2 → 3: Memory Candidate → Verified Memory

**Trigger:** Candidate.confidence ≥ Candidate.promotion_threshold

**Owner:** Distillation Engine

**Promotion conditions:**
- `confidence >= promotion_threshold` (default: 0.75) AND
- `len(supporting_obs) >= 2` (at least 2 independent source observations) AND
- `status == ACCUMULATING`

```
Step 1: Final Contradiction Check
  - Re-run contradiction search across all Verified Memory
  - If contradiction found:
      - Hold promotion
      - Create a competing Candidate pair
      - Flag for reflection resolution

Step 2: Create Verified Memory
  - Create VerifiedMemory object with:
      - statement = Candidate.statement
      - confidence = Candidate.confidence
      - source_candidate = Candidate.id
      - supporting_obs = Candidate.supporting_obs
      - status = ACTIVE
  - Set Candidate.status = PROMOTED

Step 3: Update Entity Links
  - Link VerifiedMemory to all related entities
  - Update entity attributes if memory implies a change

Step 4: Update Graph
  - Add VerifiedMemory node to knowledge graph
  - Create edges to related Entity nodes

Step 5: Update Embeddings
  - Embed the VerifiedMemory.statement
  - Add to vector index

Step 6: Log to Timeline
  - Create TimelineEvent:
      event_type = CANDIDATE_PROMOTED
      what = "New verified memory: {statement}"
      when = now

Step 7: Write Audit Log Entry
  - action = PROMOTE
  - object_type = verified_memory
  - actor = DistillationEngine
```

---

## Stage 3 → 4: Verified Memory → Knowledge Graph

**Trigger:** Runs as part of Stage 2→3 (Step 4) or during Distillation cycle

**Owner:** Knowledge Engine

```
Step 1: Merge with existing graph nodes
  - Check if any existing Entity nodes should be consolidated
  - Apply entity resolution (same entity, different names)

Step 2: Create or update graph edges
  - For each Relationship linked to this memory:
    - If edge exists: increase confidence
    - If edge doesn't exist: create new edge
    - Apply temporal scoping if applicable

Step 3: Propagate confidence
  - Edges connecting to newly promoted memories gain a small confidence boost
  - Edges with no recent reinforcement decay slightly
```

---

## Stage 4 → 5: Knowledge Graph → Beliefs

**Trigger:** Distillation Engine, once per cycle

**Owner:** Distillation Engine + LLM synthesis

```
Step 1: Identify belief candidates
  - Find clusters of Verified Memory that share entities or themes
  - Clusters with ≥3 memories and average confidence > 0.65 are belief candidates

Step 2: Synthesize belief statement (LLM call)
  - Prompt: "Given these verified memories, state a single belief about this user"
  - Generate: statement, confidence, category

Step 3: Check for existing belief
  - If belief exists (semantic similarity > 0.85):
      - Update confidence
      - Add version history entry
      - Update supporting_memories list
  - If belief is new:
      - Create Belief object
      - Link to supporting Verified Memories

Step 4: Detect obsolete beliefs
  - Beliefs with no reinforcement in 60 days AND declining confidence
  - Mark as status = WEAKENING
  - If confidence drops below 0.30: archive

Step 5: Update Identity Model
  - High-confidence (>0.85), long-standing (>30 days) beliefs become Identity Model components
  - Regenerate identity_summary paragraph
```

---

## Stage 5 → 6: Beliefs → Identity Model

**Trigger:** Reflection Engine, nightly

**Owner:** Reflection Engine + LLM synthesis

```
Step 1: Collect qualifying beliefs
  - confidence >= 0.85
  - age >= 30 days
  - status = ACTIVE
  - Category in [PREFERENCE, SKILL, VALUE, INTEREST]

Step 2: Synthesize identity summary (LLM call)
  - Prompt: "Given these long-standing beliefs about a person, write a 2-paragraph
    identity summary that captures who they are."
  - This is not a CV. It is a rich, nuanced description.

Step 3: Update Identity Model
  - Replace previous identity_summary
  - Update version
  - Log to Timeline

Step 4: Archive superseded beliefs
  - Beliefs replaced by stronger, updated beliefs
  - Never deleted — archived with superseded_by link
```

---

## Background Jobs

### Candidate Queue Worker

- **Type:** Background worker (runs continuously)
- **Behavior:** Reads from Candidate Queue, processes Stage 1→2
- **Batch size:** 10 observations per batch
- **Retry policy:** 3 retries with exponential backoff on failure

### Distillation Scheduler

- **Type:** Scheduled cron job
- **Default schedule:** Every 4 hours
- **What it does:**
  1. Process all pending candidates (Stage 1→2)
  2. Evaluate all candidates for promotion (Stage 2→3)
  3. Update knowledge graph (Stage 3→4)
  4. Synthesize new or updated beliefs (Stage 4→5)
  5. Write DistillationCycle log

### Reflection Scheduler

- **Type:** Scheduled cron job
- **Default schedule:** Daily at 02:00 UTC (user-configurable)
- **What it does:**
  1. Run all six reflection questions
  2. Update confidence scores
  3. Identify and archive obsolete beliefs
  4. Update Identity Model (Stage 5→6)
  5. Generate and store daily digest
  6. Write Reflection object

### Embedding Refresh Worker

- **Type:** Background worker (low priority)
- **Trigger:** After any entity description or belief statement changes
- **Batch size:** 50 items per run

---

## LLM Call Budget

| Pipeline Stage | LLM Calls | Model Requirement |
|---|---|---|
| Entity Extraction | 1 | Standard (GPT-3.5 class or better) |
| Observation Extraction | 1 | Standard |
| Relationship Extraction | 1 | Standard (optional in v1) |
| Belief Synthesis | 1 per belief cluster | Standard |
| Identity Summary | 1 | Advanced (GPT-4 class or better) |
| Reflection Questions | 6 | Standard |

**Total per observe() call:** ~2-3 LLM calls  
**Total per distillation cycle:** Variable (proportional to new candidates)  
**Total per nightly reflection:** ~7 LLM calls

---

## Error Handling

| Failure Scenario | Recovery Strategy |
|---|---|
| LLM unavailable during observe | Store raw conversation in PENDING state; retry when LLM available |
| LLM unavailable during distillation | Skip cycle; retry on next scheduled run |
| Entity resolution ambiguity | Flag entity as `needs_review`; use lower confidence |
| Candidate promotion conflict | Hold in ACCUMULATING state; surface in next reflection |
| Distillation cycle fails midway | Log error in DistillationCycle; next cycle picks up where left off |
| Embedding service unavailable | Defer embedding; memory still usable via graph + keyword search |
