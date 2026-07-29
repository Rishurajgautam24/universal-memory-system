# Risk Register
## Universal Memory System (UMS)

> **Version:** 1.0 · **Date:** 2026-07-29  
> **Owner:** Product Management  
> **Review Cadence:** Monthly

---

## Risk Scoring

**Likelihood:** 1 (Unlikely) → 5 (Near Certain)  
**Impact:** 1 (Negligible) → 5 (Project-ending)  
**Risk Score = Likelihood × Impact**

| Score | Severity |
|---|---|
| 1–4 | Low |
| 5–9 | Medium |
| 10–16 | High |
| 17–25 | Critical |

---

## Risk Register

### Technical Risks

---

**RISK-T01: LLM extraction quality is too noisy**

| Field | Value |
|---|---|
| **Description** | The LLM used for observation extraction produces too many incorrect, irrelevant, or low-quality observations, making memory unreliable. |
| **Likelihood** | 4 |
| **Impact** | 5 |
| **Score** | 20 (Critical) |
| **Mitigation** | The Candidate system is the primary mitigation — nothing is trusted until reinforced. Additionally: tune extraction prompts extensively, add confidence floor, test with diverse conversation types before launch. |
| **Contingency** | If extraction quality remains poor, add a human-review queue for early users. |
| **Owner** | Eng |
| **Status** | OPEN |

---

**RISK-T02: Semantic deduplication produces false positives**

| Field | Value |
|---|---|
| **Description** | The system incorrectly identifies two different observations as duplicates and merges them, losing a real distinction. |
| **Likelihood** | 3 |
| **Impact** | 3 |
| **Score** | 9 (Medium) |
| **Mitigation** | Use a conservative similarity threshold (e.g., 0.85). Test dedup logic with adversarial examples. Log all merges in audit log for review. |
| **Contingency** | Allow users to manually split merged candidates via an admin endpoint. |
| **Owner** | Eng |
| **Status** | OPEN |

---

**RISK-T03: Storage abstraction leaks implementation details**

| Field | Value |
|---|---|
| **Description** | The storage interface is insufficiently abstract, making it difficult to swap backends in Phase 2/3. |
| **Likelihood** | 3 |
| **Impact** | 4 |
| **Score** | 12 (High) |
| **Mitigation** | Define the storage interface before writing any storage implementation. Review interface design in Phase 1 architecture review. |
| **Contingency** | Refactor storage in Phase 2 before adding graph capabilities. |
| **Owner** | Arch |
| **Status** | OPEN |

---

**RISK-T04: Recall latency exceeds 2-second SLA**

| Field | Value |
|---|---|
| **Description** | The multi-stage recall pipeline is too slow for real-time AI assistant use cases. |
| **Likelihood** | 3 |
| **Impact** | 4 |
| **Score** | 12 (High) |
| **Mitigation** | Profile recall pipeline in Phase 1. Cache identity summary and frequently recalled context. Design for parallel execution of retrieval stages where possible. |
| **Contingency** | Add a `fast_recall` mode that skips graph traversal and embedding search for latency-sensitive clients. |
| **Owner** | Eng |
| **Status** | OPEN |

---

**RISK-T05: Candidate queue data loss on service restart**

| Field | Value |
|---|---|
| **Description** | The observation queue is not durable, and observations are lost if the service crashes before distillation runs. |
| **Likelihood** | 2 |
| **Impact** | 5 |
| **Score** | 10 (High) |
| **Mitigation** | Use a durable queue mechanism (write to disk before acknowledging). Idempotent processing so duplicate delivery doesn't cause duplicate memories. |
| **Contingency** | Expose a `POST /v1/reprocess` endpoint to replay raw conversations. |
| **Owner** | Eng |
| **Status** | OPEN |

---

**RISK-T06: Graph traversal performance degrades with memory scale**

| Field | Value |
|---|---|
| **Description** | As the knowledge graph grows to thousands of nodes over 1+ years, graph queries become too slow to use in the recall pipeline. |
| **Likelihood** | 2 |
| **Impact** | 3 |
| **Score** | 6 (Medium) |
| **Mitigation** | Design graph queries with depth limits from day one. Add traversal cost budgets to recall pipeline. Profile with synthetic 1-year datasets before Phase 2 ships. |
| **Contingency** | Introduce graph query caching layer. |
| **Owner** | Eng |
| **Status** | OPEN |

---

### Product Risks

---

**RISK-P01: Memory fills with noise despite the Candidate system**

| Field | Value |
|---|---|
| **Description** | Even with the Candidate threshold, noisy memories accumulate because users have many repetitive conversations about unimportant topics. |
| **Likelihood** | 3 |
| **Impact** | 4 |
| **Score** | 12 (High) |
| **Mitigation** | Category filtering — only categories [PREFERENCE, BELIEF, PROJECT, SKILL] are eligible for promotion. ACTIVITY and FACT categories require higher confidence. Reflection engine explicitly prunes stale noise. |
| **Contingency** | Add manual memory pruning UI in Phase 5. |
| **Owner** | PM + Eng |
| **Status** | OPEN |

---

**RISK-P02: Users don't trust that memory is accurate**

| Field | Value |
|---|---|
| **Description** | If users can't verify what the system believes about them, they won't trust it, and adoption stalls. |
| **Likelihood** | 3 |
| **Impact** | 4 |
| **Score** | 12 (High) |
| **Mitigation** | The `explain` endpoint is a core feature, not a nice-to-have. Daily digest from reflection gives users visibility. Confidence scores are always visible. |
| **Contingency** | Prioritize a simple memory review UI in Phase 5. |
| **Owner** | PM |
| **Status** | OPEN |

---

**RISK-P03: Switching LLM providers breaks extraction quality**

| Field | Value |
|---|---|
| **Description** | Extraction prompts optimized for GPT-4 perform poorly on Claude, or vice versa, leading to inconsistent memory quality. |
| **Likelihood** | 3 |
| **Impact** | 3 |
| **Score** | 9 (Medium) |
| **Mitigation** | Maintain separate prompt templates per provider. Build a memory quality test suite that runs against all supported providers before release. |
| **Contingency** | Document quality differences per provider in release notes. |
| **Owner** | Eng |
| **Status** | OPEN |

---

**RISK-P04: The project is perceived as "just another AI memory app"**

| Field | Value |
|---|---|
| **Description** | The positioning as "infrastructure" is not clearly communicated, and developers treat UMS as a consumer app rather than a platform they can build on. |
| **Likelihood** | 3 |
| **Impact** | 3 |
| **Score** | 9 (Medium) |
| **Mitigation** | Lead all messaging with the infrastructure framing. Open source from day one. SDKs and integrations (Phase 5) demonstrate the platform nature. |
| **Contingency** | Developer evangelist content specifically targeting the "memory as infrastructure" narrative. |
| **Owner** | PM |
| **Status** | OPEN |

---

### Privacy & Compliance Risks

---

**RISK-PR01: Personally identifiable information stored without user consent**

| Field | Value |
|---|---|
| **Description** | The observation engine extracts names, locations, or other PII from conversations and stores them in memory without explicit user awareness. |
| **Likelihood** | 4 |
| **Impact** | 5 |
| **Score** | 20 (Critical) |
| **Mitigation** | Document PII handling clearly in privacy policy. In Phase 1, flag PII in observations but don't strip. In Phase 2, add configurable PII filtering. Self-hosted deployment means user controls their own data. |
| **Contingency** | Add a pre-processing step to redact PII before extraction if the user configures it. |
| **Owner** | PM + Legal |
| **Status** | OPEN |

---

**RISK-PR02: Conversations are sent to third-party LLM APIs for extraction**

| Field | Value |
|---|---|
| **Description** | When using OpenAI or Anthropic for extraction, raw conversation text leaves the user's control. |
| **Likelihood** | 5 (Always happens) |
| **Impact** | 3 |
| **Score** | 15 (High) |
| **Mitigation** | Prominently disclose in documentation that extraction uses the configured LLM API. Support local model (Ollama) as an alternative that keeps data on-device. Make provider selection a required configuration step. |
| **Contingency** | Prioritize local model support if user privacy concerns block adoption. |
| **Owner** | PM + Eng |
| **Status** | OPEN (by design) |

---

### Dependency Risks

---

**RISK-D01: LLM API provider deprecates or changes API**

| Field | Value |
|---|---|
| **Description** | OpenAI or Anthropic makes a breaking API change that disrupts the extraction pipeline. |
| **Likelihood** | 2 |
| **Impact** | 3 |
| **Score** | 6 (Medium) |
| **Mitigation** | The LLM Provider abstraction isolates the impact. Pin API versions. Monitor provider changelogs. |
| **Contingency** | Switch to an alternative provider within the abstraction layer. |
| **Owner** | Eng |
| **Status** | OPEN |

---

**RISK-D02: MCP protocol changes break integrations**

| Field | Value |
|---|---|
| **Description** | The MCP specification evolves and breaks compatibility with existing MCP-based integrations. |
| **Likelihood** | 2 |
| **Impact** | 2 |
| **Score** | 4 (Low) |
| **Mitigation** | Follow MCP spec releases. Design MCP server as a thin wrapper (easy to update). |
| **Contingency** | Maintain direct HTTP SDK integration that doesn't depend on MCP. |
| **Owner** | Eng |
| **Status** | OPEN |

---

## Risk Summary Dashboard

| Risk ID | Description | Score | Severity | Status |
|---|---|---|---|---|
| RISK-T01 | LLM extraction noise | 20 | Critical | OPEN |
| RISK-PR01 | PII stored without consent | 20 | Critical | OPEN |
| RISK-T03 | Storage abstraction leak | 12 | High | OPEN |
| RISK-T04 | Recall latency SLA | 12 | High | OPEN |
| RISK-T05 | Queue data loss | 10 | High | OPEN |
| RISK-P01 | Memory fills with noise | 12 | High | OPEN |
| RISK-P02 | User trust in accuracy | 12 | High | OPEN |
| RISK-PR02 | Data sent to LLM APIs | 15 | High | OPEN (by design) |
| RISK-T02 | Dedup false positives | 9 | Medium | OPEN |
| RISK-T06 | Graph scale performance | 6 | Medium | OPEN |
| RISK-P03 | Cross-LLM extraction quality | 9 | Medium | OPEN |
| RISK-P04 | Positioning risk | 9 | Medium | OPEN |
| RISK-D01 | LLM API changes | 6 | Medium | OPEN |
| RISK-D02 | MCP protocol changes | 4 | Low | OPEN |
