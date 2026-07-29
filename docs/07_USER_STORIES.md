# User Stories & Acceptance Criteria
## Universal Memory System (UMS)

> **Version:** 1.0 · **Date:** 2026-07-29  
> **Format:** As a [persona], I want [goal], so that [benefit].  
> **Acceptance Criteria format:** GIVEN [context] WHEN [action] THEN [outcome]

---

## Personas

- **Alex** — Power AI user. Uses Claude, Cursor, ChatGPT, and Gemini daily. Builds side projects and is frustrated by amnesia across tools.
- **Dev** — A developer building an AI application who wants to add memory to their product.
- **The System** — The UMS itself, acting as an autonomous agent for reflection and distillation.

---

## Epic 1: Core Observation

---

### US-01: Submit a conversation for memory processing

**As** Alex,  
**I want** to send a conversation I had with Claude to UMS,  
**So that** the important things said in that conversation are eventually remembered.

**Acceptance Criteria:**

**AC-01a:** GIVEN a valid API key and a non-empty conversation string  
WHEN `POST /v1/observe` is called  
THEN the system returns HTTP 202 with a `job_id` within 200ms

**AC-01b:** GIVEN the conversation contains at least 50 words  
WHEN the observation job completes  
THEN at least 1 Observation object exists in the candidate queue

**AC-01c:** GIVEN the conversation is processed  
WHEN observation extraction is complete  
THEN no observation is written directly to Verified Memory or Beliefs — only to Candidate Queue

**AC-01d:** GIVEN the LLM is unavailable during extraction  
WHEN the observe job runs  
THEN the raw conversation is stored with `stage = PENDING` and no data is lost

---

### US-02: Observe from multiple applications

**As** Dev,  
**I want** to call `observe()` from my application with a `source` tag,  
**So that** the source of each memory is always traceable.

**Acceptance Criteria:**

**AC-02a:** GIVEN a request with `source: "MyApp"` and a conversation  
WHEN the observation is created  
THEN `Observation.source == "MyApp"` is stored

**AC-02b:** GIVEN observations from two different sources about the same topic  
WHEN both are processed  
THEN they are treated as independent evidence for the same Candidate (not duplicates of each other)

---

## Epic 2: Memory Candidate Lifecycle

---

### US-03: New information starts as a candidate

**As** The System,  
**I want** every new observation to become a Candidate, not immediate Verified Memory,  
**So that** noise and casual statements do not pollute permanent memory.

**Acceptance Criteria:**

**AC-03a:** GIVEN a new observation with no matching existing Candidate  
WHEN the Distillation Engine processes it  
THEN a new MemoryCandidate is created with `status = ACCUMULATING` and `confidence = observation.confidence`

**AC-03b:** GIVEN a new observation that is semantically similar to an existing Candidate  
WHEN the Distillation Engine processes it  
THEN the existing Candidate gains an additional `supporting_obs` entry and its confidence increases

**AC-03c:** GIVEN a Candidate with only one supporting observation  
WHEN 30 days pass with no reinforcement  
THEN the Candidate expires and is archived, never promoted to Verified Memory

---

### US-04: Candidate promotion after sufficient evidence

**As** The System,  
**I want** to promote a Candidate to Verified Memory only after it has accumulated sufficient evidence,  
**So that** Verified Memory is reliable.

**Acceptance Criteria:**

**AC-04a:** GIVEN a Candidate with `confidence >= 0.75` AND `len(supporting_obs) >= 2`  
WHEN the Distillation Engine evaluates it  
THEN the Candidate is promoted to Verified Memory and its `status` changes to `PROMOTED`

**AC-04b:** GIVEN a Candidate is promoted  
WHEN the promotion completes  
THEN a `TimelineEvent` of type `CANDIDATE_PROMOTED` is created  
AND an `AuditLogEntry` with `action = PROMOTE` is created

**AC-04c:** GIVEN a Candidate is promoted  
WHEN checking the source  
THEN the resulting VerifiedMemory contains a link back to the originating Candidate and all its supporting Observations

---

### US-05: Contradiction detection

**As** The System,  
**I want** to detect when a new observation contradicts existing Verified Memory,  
**So that** beliefs are updated when the user's views change, not silently overwritten.

**Acceptance Criteria:**

**AC-05a:** GIVEN an existing Verified Memory: "User prefers PostgreSQL"  
WHEN a new Observation states: "User is migrating away from PostgreSQL to DuckDB"  
THEN a new Candidate is created with `status = CONTRADICTED` linking to the existing memory

**AC-05b:** GIVEN a contradiction is detected  
WHEN the Distillation Engine processes it  
THEN neither memory is deleted — both exist, with the contradiction flagged for reflection

**AC-05c:** GIVEN a contradiction exists  
WHEN the user calls `POST /v1/explain` for the affected belief  
THEN the response includes both the supporting and contradicting evidence

---

## Epic 3: Recall & Context

---

### US-06: Retrieve relevant context for a task

**As** Alex (via Cursor),  
**I want** Cursor to retrieve relevant context from UMS before helping me with a coding task,  
**So that** Cursor doesn't ask me to re-explain my project, preferences, or past decisions.

**Acceptance Criteria:**

**AC-06a:** GIVEN a task description and an active user session  
WHEN `POST /v1/recall` is called  
THEN the response is returned in under 2 seconds (p95)

**AC-06b:** GIVEN the user has an active project "UMS" in memory  
WHEN recall is called with context `{ "project": "UMS" }`  
THEN the response includes the project's current_goal, recent_work, and open_questions

**AC-06c:** GIVEN the user has 5 beliefs about system design  
WHEN recall is called  
THEN the response includes only the most relevant beliefs (ranked), not all beliefs

**AC-06d:** GIVEN a new user with no memory  
WHEN recall is called  
THEN the response returns an empty context gracefully (no error)

---

### US-07: Filter recall by time range

**As** Alex,  
**I want** to recall what I was working on in a specific time period,  
**So that** I can reconstruct my context from months ago.

**Acceptance Criteria:**

**AC-07a:** GIVEN a recall request with `time_range: { from: "2026-03-01", to: "2026-03-31" }`  
WHEN the request is processed  
THEN only memories, beliefs, and timeline events from that period are returned

---

## Epic 4: Distillation

---

### US-08: Automatic distillation on schedule

**As** The System,  
**I want** to run the distillation pipeline automatically every 4 hours,  
**So that** memory stays current without user intervention.

**Acceptance Criteria:**

**AC-08a:** GIVEN the distillation scheduler is configured  
WHEN 4 hours pass  
THEN a DistillationCycle runs automatically

**AC-08b:** GIVEN a DistillationCycle runs  
WHEN it completes  
THEN a DistillationCycle log object is written with: observations_processed, candidates_promoted, beliefs_updated

**AC-08c:** GIVEN a DistillationCycle fails midway  
WHEN the next scheduled run occurs  
THEN it picks up unprocessed items without duplicating work

---

## Epic 5: Reflection

---

### US-09: Automatic nightly self-reflection

**As** The System,  
**I want** to ask myself reflective questions every night,  
**So that** memory remains coherent and evolving without user prompting.

**Acceptance Criteria:**

**AC-09a:** GIVEN the reflection scheduler is active  
WHEN 02:00 UTC arrives  
THEN a Reflection cycle runs automatically

**AC-09b:** GIVEN a Reflection cycle runs  
WHEN it completes  
THEN a Reflection object is stored with a human-readable `digest`

**AC-09c:** GIVEN a belief has not been reinforced in 60 days and has confidence < 0.3  
WHEN reflection runs  
THEN the belief is archived (not deleted) and a TimelineEvent is logged

**AC-09d:** GIVEN reflection detects a pattern across projects  
WHEN the cycle completes  
THEN the pattern is recorded as a new Observation in the candidate queue for future promotion

---

### US-10: Manual reflection trigger

**As** Alex,  
**I want** to manually trigger a reflection over a specific time period,  
**So that** I can get an instant summary of what changed during a project sprint.

**Acceptance Criteria:**

**AC-10a:** GIVEN a request to `POST /v1/reflect` with a date range  
WHEN the request is processed  
THEN a Reflection object is returned with digest covering that period

**AC-10b:** GIVEN `dry_run: true` in the request  
WHEN reflection runs  
THEN the digest is returned but NO changes are written to memory

---

## Epic 6: Explainability

---

### US-11: Explain why a belief exists

**As** Alex,  
**I want** to ask UMS "why do you think I like Neo4j?",  
**So that** I can verify that the memory is correct and trace it to real conversations.

**Acceptance Criteria:**

**AC-11a:** GIVEN a belief ID  
WHEN `POST /v1/explain` is called  
THEN the response includes: the belief statement, confidence, and the full evidence chain (Observations → Candidates → Verified Memory)

**AC-11b:** GIVEN the belief's evidence chain  
WHEN rendered  
THEN each piece of evidence includes: which application it came from, when it was observed, and the raw excerpt from the conversation

**AC-11c:** GIVEN a belief with no evidence chain  
THEN such a belief CANNOT exist in UMS (invariant enforced at creation)

---

## Epic 7: Timeline

---

### US-12: View history of thinking

**As** Alex,  
**I want** to see a timeline of my intellectual activity and project progress,  
**So that** I can reconstruct what I was thinking at any point in the past.

**Acceptance Criteria:**

**AC-12a:** GIVEN the timeline endpoint is called with no filters  
WHEN the response is returned  
THEN events are ordered chronologically (newest first by default)

**AC-12b:** GIVEN a filter `project = "UMS"`  
WHEN the timeline is queried  
THEN only events related to the UMS project are returned

**AC-12c:** GIVEN a belief formation event  
WHEN it appears in the timeline  
THEN it includes: `what` (which belief), `when` (promoted date), `where` (source app)

---

## Epic 8: Portability & Ownership

---

### US-13: Export all memory

**As** Alex,  
**I want** to export all of my memory in a portable format,  
**So that** I am never locked in and can migrate to a self-hosted or different instance.

**Acceptance Criteria:**

**AC-13a:** GIVEN an export request  
WHEN the export is generated  
THEN all objects are included: Observations, Candidates, Verified Memory, Beliefs, Timeline, Identity Model, Audit Log

**AC-13b:** GIVEN the export format is JSON  
WHEN the export is complete  
THEN the JSON is valid, self-describing, and can be re-imported without data loss

**AC-13c:** GIVEN the export format is Markdown  
WHEN the export is complete  
THEN a human-readable document is produced that a person can read without tooling

**AC-13d:** GIVEN the export is requested  
WHEN the process runs  
THEN it completes in under 30 seconds for a user with 1 year of history

---

### US-14: Delete all memory

**As** Alex,  
**I want** to delete all of my memory with a single command,  
**So that** I am always in control of my data.

**Acceptance Criteria:**

**AC-14a:** GIVEN a confirmed delete request  
WHEN it is executed  
THEN all user data is removed from all stores (graph, vector index, timeline, audit log)

**AC-14b:** GIVEN a delete request without confirmation  
WHEN it is received  
THEN the system returns a 400 error requiring explicit confirmation

---

## Epic 9: SDK & Integrations

---

### US-15: Use UMS from Python in 5 lines

**As** Dev,  
**I want** to integrate UMS memory into my Python application with minimal code,  
**So that** I can add memory to my app without understanding internal architecture.

**Acceptance Criteria:**

**AC-15a:** GIVEN the Python SDK is installed  
WHEN `memory.observe(conversation=..., source=...)` is called  
THEN the conversation is queued for processing with no additional configuration required

**AC-15b:** GIVEN the Python SDK is installed  
WHEN `context = memory.recall(task=...)` is called  
THEN a structured context object is returned with a `prompt_ready_summary` attribute

---

### US-16: Use UMS as an MCP tool

**As** Alex (via Claude Desktop),  
**I want** Claude to automatically observe and recall from UMS via MCP,  
**So that** every Claude conversation contributes to and benefits from persistent memory.

**Acceptance Criteria:**

**AC-16a:** GIVEN the UMS MCP server is configured in Claude Desktop  
WHEN a conversation starts  
THEN Claude can call the `recall` tool and receive relevant context automatically

**AC-16b:** GIVEN a conversation ends  
WHEN the `observe` MCP tool is called with the conversation  
THEN the conversation is queued for memory processing

**AC-16c:** GIVEN the MCP server exposes tools  
WHEN listing available tools  
THEN exactly these tools appear: `observe`, `recall`, `search`, `timeline`, `reflect`, `explain`
