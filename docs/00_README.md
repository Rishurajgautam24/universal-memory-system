# Universal Memory System (UMS) — Documentation Index

> **Status:** Production-Ready · **Phase:** v0.1.0 Released  
> **Last Updated:** 2026-07-30  
> **Owner:** UMS Core Team

---

## What This Is

UMS is the **memory layer that every AI application plugs into** — not another AI app.
It is infrastructure, like a database, but for identity, belief, and context.

---

## Quick Navigation

### 📚 Top-Level Documentation
| File | Purpose | Audience |
|------|---------|----------|
| [README.md](../README.md) | **Start here** — Overview, quick start, API reference | All |
| [CHANGELOG.md](../CHANGELOG.md) | Version history and release notes | All |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | How to contribute | Developers |
| [DEPLOYMENT.md](../DEPLOYMENT.md) | Production deployment guide | DevOps, Eng |
| [SECURITY.md](../SECURITY.md) | Security policy and reporting | All |
| [LICENSE](../LICENSE) | MIT License | All |

### 📖 Detailed Documentation
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

- **New users:** Start at [README.md](../README.md)  
- **Developers:** Read `01 → 03` then jump to specific modules
- **Contributors:** Read [CONTRIBUTING.md](../CONTRIBUTING.md) first
- **DevOps:** Read [DEPLOYMENT.md](../DEPLOYMENT.md) and `03_ARCHITECTURE.md`
- **QA:** `07` is your source of truth for acceptance criteria

---

## Repository Structure

```
ums/
├── README.md                 # Main documentation and quick start
├── CHANGELOG.md              # Version history
├── CONTRIBUTING.md           # Contribution guidelines
├── DEPLOYMENT.md             # Production deployment guide
├── SECURITY.md               # Security policy
├── LICENSE                   # MIT License
├── pyproject.toml            # Package configuration
├── Dockerfile                # Docker image
├── docker-compose.yml        # Docker Compose config
├── .github/                  # GitHub templates and CI/CD
│   ├── workflows/ci.yml      # CI/CD pipeline
│   └── ISSUE_TEMPLATE/       # Issue templates
├── ums/                      # Main package
│   ├── gateway/              # FastAPI REST API
│   ├── observation/          # Observation engine
│   ├── memory/               # Memory engine
│   ├── recall/               # Recall engine
│   ├── distillation/         # Distillation pipeline
│   ├── llm/                  # LLM abstraction
│   ├── models/               # Pydantic data models
│   ├── storage/              # Storage layer
│   └── utils/                # Utilities
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   ├── component/            # Component tests
│   └── integration/          # Integration tests
├── scripts/                  # Utility scripts
└── docs/                     # Detailed documentation
    ├── 00_README.md          # This file
    ├── 01_PRD.md             # Product requirements
    ├── 02_SUCCESS_CRITERIA.md
    ├── 03_ARCHITECTURE.md    # Architecture design
    ├── 04_DATA_MODEL.md      # Data models
    ├── 05_API_SPEC.md        # API specification
    ├── 06_PIPELINE_SPEC.md   # Pipeline specification
    ├── 07_USER_STORIES.md    # User stories
    ├── 08_ROADMAP.md         # Roadmap
    ├── 09_RISK_REGISTER.md   # Risk register
    └── 10_GLOSSARY.md        # Glossary
```

---

## Getting Help

- 📖 **Documentation:** Start with [README.md](../README.md)
- 🐛 **Bug Reports:** Use [GitHub Issues](https://github.com/your-org/ums/issues)
- 💡 **Feature Requests:** Use [GitHub Issues](https://github.com/your-org/ums/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/your-org/ums/discussions)
- 📧 **Security:** `security@ums.dev`

---

## License

MIT License — see [LICENSE](../LICENSE) for details.