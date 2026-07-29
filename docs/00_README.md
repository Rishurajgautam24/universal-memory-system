# Universal Memory System (UMS) — Documentation Index

> **Status:** Pre-Engineering · **Phase:** Product Definition  
> **Last Updated:** 2026-07-29  
> **Owner:** Product Management

---

## What This Is

UMS is the **memory layer that every AI application plugs into** — not another AI app.
It is infrastructure, like a database, but for identity, belief, and context.

---

## Document Map

| # | Document | Purpose | Audience |
|---|----------|---------|----------|
| 01 | [Product Requirements Document](./01_PRD.md) | What we are building and why | All |
| 02 | [Success Criteria & KPIs](./02_SUCCESS_CRITERIA.md) | How we know we won | PM, Exec |
| 03 | [Architecture Design Document](./03_ARCHITECTURE.md) | Six-layer system design | Eng, Arch |
| 04 | [Data Model Specification](./04_DATA_MODEL.md) | Every object in the system | Eng, Arch |
| 05 | [API Specification](./05_API_SPEC.md) | Public Gateway contract | Eng, SDK authors |
| 06 | [Internal Pipeline Spec](./06_PIPELINE_SPEC.md) | From raw input → graph | Eng |
| 07 | [User Stories & Acceptance Criteria](./07_USER_STORIES.md) | Feature-level requirements | PM, QA, Eng |
| 08 | [Roadmap & Milestones](./08_ROADMAP.md) | Five-phase delivery plan | All |
| 09 | [Risk Register](./09_RISK_REGISTER.md) | What can go wrong | PM, Eng |
| 10 | [Glossary](./10_GLOSSARY.md) | Shared language | All |

---

## First Principles

1. **Applications never touch storage.** They only speak to the Gateway.  
2. **LLMs never write directly to memory.** Everything is a candidate first.  
3. **Memory is owned by the user**, not by the application, not by the model.  
4. **Memory is portable and model-agnostic.** Switching LLMs must cost zero.  
5. **Memory explains itself.** Every belief has a chain of evidence.

---

## How to Use These Docs

- Read in order `01 → 10` for full context.  
- Engineers: start at `03` after reading `01`.  
- QA: `07` is your source of truth.  
- If anything contradicts another document, `01_PRD.md` wins.
