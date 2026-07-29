# API Specification
## Universal Memory System — Memory Gateway

> **Version:** v1  
> **Base URL:** `http://localhost:8000/v1` (self-hosted default)  
> **Date:** 2026-07-29  
> **Auth:** Bearer token in `Authorization` header  
> **Content-Type:** `application/json`

---

## Design Contract

This API is the **only** surface that clients ever touch.  
It is intentionally minimal: six endpoints, each with a single clear purpose.  
Internal architecture may change entirely. This contract will not.

---

## Authentication

Every request must include:
```http
Authorization: Bearer <user-api-key>
```

API keys are scoped to a single user identity.  
All data returned is isolated to that user.

Error response when authentication fails:
```json
{
  "error": "unauthorized",
  "message": "Invalid or missing API key"
}
```

---

## Standard Response Envelope

All successful responses follow this structure:
```json
{
  "ok": true,
  "data": { ... },
  "meta": {
    "request_id": "uuid",
    "processing_time_ms": 142,
    "version": "1.0"
  }
}
```

All error responses follow this structure:
```json
{
  "ok": false,
  "error": "error_code",
  "message": "Human-readable description",
  "meta": {
    "request_id": "uuid"
  }
}
```

---

## Endpoints

---

### POST /v1/observe

**Purpose:** Submit a conversation for memory processing.

Processing is **asynchronous**. The endpoint acknowledges immediately.
The actual observation extraction and candidate creation happen in the background.

**Request Body:**
```json
{
  "source": "Claude",
  "conversation": "Full conversation text or structured messages array",
  "metadata": {
    "project": "UMS",
    "session_id": "abc123",
    "tags": ["coding", "architecture"]
  },
  "options": {
    "priority": "normal",
    "extract_entities": true,
    "min_confidence": 0.4
  }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `source` | String | Yes | Name of the calling application |
| `conversation` | String | Yes | Raw conversation text (or JSON message array) |
| `metadata` | Object | No | Arbitrary metadata passed through to observations |
| `options.priority` | Enum | No | `low`, `normal`, `high`. Default: `normal` |
| `options.extract_entities` | Boolean | No | Whether to run entity extraction. Default: `true` |
| `options.min_confidence` | Float | No | Minimum confidence for observations to enter queue. Default: `0.4` |

**Success Response (202 Accepted):**
```json
{
  "ok": true,
  "data": {
    "job_id": "3f8a2c1d-...",
    "status": "queued",
    "estimated_processing_ms": 3000,
    "message": "Conversation queued for memory processing"
  },
  "meta": { ... }
}
```

**Error Codes:**
| Code | HTTP Status | Meaning |
|---|---|---|
| `invalid_conversation` | 400 | Conversation is empty or too short |
| `source_required` | 400 | `source` field is missing |
| `queue_full` | 429 | Processing queue is at capacity |

---

### POST /v1/recall

**Purpose:** Retrieve memory context relevant to a task or question.

This is the primary read operation. It runs multi-stage retrieval internally
and returns a structured context object ready for injection into an LLM prompt.

**Request Body:**
```json
{
  "task": "Review my Python code for the UMS observation engine",
  "context": {
    "project": "UMS",
    "recent_messages": ["last 2 user messages for additional context"],
    "focus": ["preferences", "projects", "beliefs"]
  },
  "options": {
    "max_tokens": 2000,
    "include_timeline": true,
    "include_beliefs": true,
    "include_projects": true,
    "time_range": {
      "from": "2026-06-01T00:00:00Z",
      "to": "2026-07-29T23:59:59Z"
    },
    "min_confidence": 0.5
  }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `task` | String | Yes | The task or question context for which memory is needed |
| `context.project` | String | No | Narrow recall to a specific project |
| `context.focus` | []String | No | Which memory types to emphasize |
| `options.max_tokens` | Integer | No | Approximate token budget for returned context. Default: 2000 |
| `options.include_*` | Boolean | No | Fine-grained inclusion controls. Default: all `true` |
| `options.time_range` | Object | No | Restrict to a specific time window |
| `options.min_confidence` | Float | No | Minimum confidence threshold for included memories |

**Success Response (200 OK):**
```json
{
  "ok": true,
  "data": {
    "context": {
      "identity_summary": "A software engineer building an AI memory infrastructure project called UMS.",
      "relevant_beliefs": [
        {
          "statement": "User believes vector search alone is insufficient for memory retrieval",
          "confidence": 0.88,
          "last_updated": "2026-07-28T10:00:00Z"
        }
      ],
      "active_projects": [
        {
          "name": "UMS",
          "status": "active",
          "current_goal": "Design the memory model before writing any code",
          "recent_work": "Drafting architecture and data model documents",
          "open_questions": ["Which graph DB to use?", "Confidence threshold for promotion?"]
        }
      ],
      "relevant_preferences": [
        {
          "statement": "User prefers to design data models before choosing databases",
          "confidence": 0.91
        }
      ],
      "recent_timeline": [
        {
          "when": "2026-07-29",
          "what": "Wrote full architecture specification for UMS"
        }
      ],
      "skills": ["Python", "System Design", "Graph Databases"],
      "prompt_ready_summary": "## About You\n..."
    },
    "retrieval_metadata": {
      "stages_used": ["intent", "projects", "beliefs", "timeline", "embeddings"],
      "total_candidates_considered": 142,
      "returned": 18,
      "approximate_tokens": 1840
    }
  },
  "meta": { ... }
}
```

---

### POST /v1/search

**Purpose:** Free-form search across all memory objects.
For when you want to find something specific, not assemble context.

**Request Body:**
```json
{
  "query": "GraphRAG vs vector search",
  "filters": {
    "types": ["belief", "observation", "verified_memory"],
    "entity": "GraphRAG",
    "time_range": {
      "from": "2026-01-01T00:00:00Z"
    },
    "min_confidence": 0.5
  },
  "options": {
    "limit": 10,
    "include_archived": false
  }
}
```

**Success Response (200 OK):**
```json
{
  "ok": true,
  "data": {
    "results": [
      {
        "type": "belief",
        "id": "uuid",
        "statement": "User believes GraphRAG produces higher quality retrieval than pure vector search",
        "confidence": 0.83,
        "last_updated": "2026-07-15T14:00:00Z",
        "source_count": 7
      }
    ],
    "total": 3,
    "query_interpretation": "Searching for memories related to GraphRAG and vector search comparison"
  },
  "meta": { ... }
}
```

---

### GET /v1/timeline

**Purpose:** Retrieve chronologically ordered events from the user's memory history.

**Query Parameters:**
| Parameter | Type | Required | Description |
|---|---|---|---|
| `from` | DateTime | No | Start of time range (ISO 8601 UTC) |
| `to` | DateTime | No | End of time range (ISO 8601 UTC) |
| `project` | String | No | Filter events by project name |
| `event_type` | String | No | Filter by event type |
| `limit` | Integer | No | Max events to return. Default: 50 |
| `page` | Integer | No | Pagination page. Default: 1 |

**Example Request:**
```http
GET /v1/timeline?from=2026-07-01T00:00:00Z&project=UMS&limit=20
```

**Success Response (200 OK):**
```json
{
  "ok": true,
  "data": {
    "events": [
      {
        "id": "uuid",
        "when": "2026-07-29T05:00:00Z",
        "what": "Wrote architecture design document for UMS",
        "where": "Claude",
        "event_type": "OBSERVATION_MADE",
        "summary": "Major design work on UMS memory architecture"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 47,
      "has_more": true
    }
  },
  "meta": { ... }
}
```

---

### POST /v1/explain

**Purpose:** Return the full evidence chain behind a belief or memory.
This is what makes UMS trustworthy — you can always ask "why do you think that?"

**Request Body:**
```json
{
  "target_id": "uuid-of-belief-or-memory",
  "target_type": "belief",
  "options": {
    "include_archived_evidence": false,
    "max_depth": 3
  }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `target_id` | UUID | Yes | ID of the belief or memory to explain |
| `target_type` | Enum | Yes | `belief`, `verified_memory`, `candidate` |
| `options.include_archived_evidence` | Boolean | No | Include superseded evidence. Default: `false` |
| `options.max_depth` | Integer | No | How deep to trace the evidence chain. Default: 3 |

**Success Response (200 OK):**
```json
{
  "ok": true,
  "data": {
    "target": {
      "type": "belief",
      "id": "uuid",
      "statement": "User likes Neo4j",
      "confidence": 0.96,
      "status": "active"
    },
    "evidence_chain": [
      {
        "level": 1,
        "type": "verified_memory",
        "statement": "User mentioned Neo4j positively in a GraphRAG discussion",
        "confidence": 0.82
      },
      {
        "level": 2,
        "type": "observation",
        "statement": "User compared Neo4j and Kuzu and preferred Neo4j's maturity",
        "source": "Claude",
        "session_id": "session-328",
        "timestamp": "2026-05-01T14:22:00Z",
        "raw_excerpt": "...I think Neo4j is more mature for production use..."
      }
    ],
    "summary": "This belief formed across 3 conversations between May and July 2026. The user consistently referenced Neo4j positively when discussing graph databases.",
    "confidence_history": [
      { "date": "2026-05-01", "confidence": 0.42, "trigger": "first_observation" },
      { "date": "2026-06-15", "confidence": 0.71, "trigger": "second_observation" },
      { "date": "2026-07-10", "confidence": 0.96, "trigger": "third_observation" }
    ]
  },
  "meta": { ... }
}
```

---

### POST /v1/reflect

**Purpose:** Trigger a reflection cycle manually.
Normally this runs automatically every night. This endpoint allows manual triggering.

**Request Body:**
```json
{
  "period": {
    "from": "2026-07-01T00:00:00Z",
    "to": "2026-07-29T23:59:59Z"
  },
  "focus": ["belief_changes", "project_updates", "patterns"],
  "options": {
    "dry_run": false
  }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `period.from` | DateTime | No | Start of period to reflect on. Default: last 24 hours |
| `period.to` | DateTime | No | End of period to reflect on. Default: now |
| `focus` | []String | No | Which reflection questions to run |
| `options.dry_run` | Boolean | No | If true, returns what would change but doesn't write. Default: `false` |

**Success Response (200 OK):**
```json
{
  "ok": true,
  "data": {
    "reflection_id": "uuid",
    "status": "completed",
    "period": { "from": "...", "to": "..." },
    "digest": "Between July 1-29, your focus on system design grew significantly. You started and made major progress on UMS. Your belief in the limitations of vector search became stronger. Three stale beliefs about old tooling preferences were archived.",
    "summary": {
      "beliefs_changed": 4,
      "beliefs_archived": 3,
      "projects_updated": 1,
      "patterns_identified": 2
    }
  },
  "meta": { ... }
}
```

---

## Rate Limits

| Endpoint | Limit |
|---|---|
| `POST /v1/observe` | 100 requests/hour |
| `POST /v1/recall` | 500 requests/hour |
| `POST /v1/search` | 200 requests/hour |
| `GET /v1/timeline` | 200 requests/hour |
| `POST /v1/explain` | 100 requests/hour |
| `POST /v1/reflect` | 10 requests/hour |

Rate limit headers included in all responses:
```http
X-RateLimit-Limit: 500
X-RateLimit-Remaining: 497
X-RateLimit-Reset: 1722254400
```

---

## Error Code Reference

| Error Code | HTTP Status | Description |
|---|---|---|
| `unauthorized` | 401 | Invalid or missing API key |
| `forbidden` | 403 | Valid key but insufficient permissions |
| `not_found` | 404 | Requested object does not exist |
| `invalid_request` | 400 | Malformed request body |
| `validation_error` | 422 | Request body valid JSON but fails field validation |
| `queue_full` | 429 | Observation queue at capacity |
| `rate_limited` | 429 | Rate limit exceeded |
| `internal_error` | 500 | Unexpected server error |
| `llm_unavailable` | 503 | LLM backend unavailable for extraction |

---

## SDK Contract

The SDK wraps this API. The public SDK interface must remain stable even if the underlying HTTP calls change.

**Python:**
```python
from ums import MemoryClient

memory = MemoryClient(api_key="...", base_url="http://localhost:8000")

# Observe
memory.observe(conversation=chat_text, source="Claude", metadata={"project": "UMS"})

# Recall
context = memory.recall(task="Review my Python code", project="UMS")
print(context.prompt_ready_summary)

# Search
results = memory.search("GraphRAG", types=["belief"])

# Timeline
events = memory.timeline(project="UMS", limit=20)

# Explain
explanation = memory.explain(belief_id="uuid")

# Reflect
digest = memory.reflect(dry_run=True)
```

**TypeScript:**
```typescript
import { MemoryClient } from '@ums/sdk';

const memory = new MemoryClient({ apiKey: '...', baseUrl: 'http://localhost:8000' });

await memory.observe({ conversation: messages, source: 'Cursor', metadata: { project: 'UMS' }});

const context = await memory.recall({ task: 'Code review', project: 'UMS' });
console.log(context.promptReadySummary);
```
