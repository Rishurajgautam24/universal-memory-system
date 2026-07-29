# Success Criteria & KPIs
## Universal Memory System (UMS)

> **Version:** 1.0 · **Date:** 2026-07-29

---

## 1. The One-Year Test

Before a single line of code is written, we define what success looks like after **one year of real use**.
If the architecture cannot satisfy every item below, we redesign the architecture — not the criteria.

| # | Success Statement | How We Verify |
|---|---|---|
| S1 | Every AI application knows who you are | Any new UMS-connected app surfaces user identity on first request |
| S2 | No application stores its own memory | Connected apps contain zero user-specific memory locally |
| S3 | Memory evolves automatically | Memory changes without any manual user curation |
| S4 | Memory explains why it believes something | Every belief has a chain of source observations accessible via `explain` |
| S5 | Memory keeps a timeline of your thinking | `timeline` query returns chronological history of decisions and beliefs |
| S6 | Memory survives switching LLMs | Export from one LLM environment, import to another — zero data loss |
| S7 | Memory is portable | Full export to JSON/Markdown in under 30 seconds |
| S8 | Memory is owned by you | User can delete all memory with a single command; no copies elsewhere |

---

## 2. Phase-Gated Success Criteria

Each phase has mandatory success gates. A phase is not "done" until all gates pass.

### Phase 1 Gate — Core Memory Server

| Gate | Criteria |
|---|---|
| P1-G1 | `observe()` processes a 2,000-token conversation and produces ≥3 observations |
| P1-G2 | `recall()` returns relevant context given a task description |
| P1-G3 | Memory persists across service restarts |
| P1-G4 | All observations are stored as candidates — nothing writes directly to permanent memory |
| P1-G5 | Response time: `observe()` acknowledges in <200ms, `recall()` returns in <2s |

### Phase 2 Gate — Knowledge Graph + Timeline

| Gate | Criteria |
|---|---|
| P2-G1 | Named entities are extracted and linked in a graph |
| P2-G2 | Relationships between entities are queryable |
| P2-G3 | Timeline events are stored with `who/what/when/where` fields |
| P2-G4 | Hybrid retrieval (graph + embeddings) outperforms pure vector search on recall quality |
| P2-G5 | `timeline` endpoint returns chronologically ordered events |

### Phase 3 Gate — Distillation + Confidence

| Gate | Criteria |
|---|---|
| P3-G1 | Distillation runs on schedule without manual trigger |
| P3-G2 | A candidate promoted to verified memory has ≥2 independent source observations |
| P3-G3 | Duplicate observations are detected and merged, not duplicated |
| P3-G4 | Contradictions between beliefs are flagged and surfaced |
| P3-G5 | Confidence scores change over time as evidence accumulates or decays |

### Phase 4 Gate — Reflection Engine

| Gate | Criteria |
|---|---|
| P4-G1 | Nightly reflection runs automatically |
| P4-G2 | Reflection produces human-readable daily digest |
| P4-G3 | Obsolete beliefs are archived, not deleted |
| P4-G4 | Reflection results feed back into the distillation cycle |

### Phase 5 Gate — SDKs + Connectors

| Gate | Criteria |
|---|---|
| P5-G1 | Python SDK: `observe()` and `recall()` work with <5 lines of user code |
| P5-G2 | TypeScript SDK reaches same functionality parity as Python SDK |
| P5-G3 | MCP server exposes the six standard tools |
| P5-G4 | Claude Desktop, Cursor, and VS Code integration demonstrated end-to-end |

---

## 3. Product KPIs (Measurable Metrics)

### 3.1 Memory Quality KPIs

| KPI | Target (6 months) | Target (12 months) |
|---|---|---|
| Observation precision (% of extracted obs that are correct) | >80% | >90% |
| Candidate promotion false positive rate | <15% | <8% |
| Belief contradiction detection rate | >70% | >85% |
| Memory staleness (% of beliefs updated in last 30 days for active users) | >60% | >80% |

### 3.2 Performance KPIs

| KPI | Target |
|---|---|
| `recall()` p50 latency | <500ms |
| `recall()` p95 latency | <2,000ms |
| `observe()` acknowledgement latency | <200ms |
| Distillation cycle completion time (1k observations) | <60s |
| Full memory export time | <30s |

### 3.3 Reliability KPIs

| KPI | Target |
|---|---|
| Observation queue data loss on restart | 0% |
| API uptime (when self-hosted) | >99% |
| Distillation job failure rate | <1% |

### 3.4 Adoption KPIs (Open Source)

| KPI | Target (3 months) | Target (12 months) |
|---|---|---|
| GitHub stars | 1,000 | 10,000 |
| Active integrations (connectors built by community) | 3 | 20 |
| Developer-reported "memory is useful" rate | >75% | >85% |

---

## 4. Anti-Goals (What Success is NOT)

The following are explicitly **not** success metrics:

- **Volume of memories stored.** A user with 10 deeply accurate beliefs is more successful than one with 10,000 noisy ones.
- **Speed of promotion.** Slow, careful candidate promotion is better than fast, noisy promotion.
- **Number of API calls.** Fewer calls that produce better context beats many calls with shallow results.

---

## 5. Failure Conditions (Red Lines)

If any of these occur, the project has failed regardless of other metrics:

| Red Line | Why |
|---|---|
| Any LLM can write directly to permanent memory | Breaks the candidate system; fills memory with garbage |
| Memory cannot be exported by the user | Violates user ownership principle |
| A belief exists with no traceable source observations | Breaks explainability principle |
| Switching LLM providers causes memory data loss | Violates portability principle |
| An application must call two different endpoints for the same operation | Breaks the single unified API contract |
