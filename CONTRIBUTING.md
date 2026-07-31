# Contributing to UMS

We love contributions! Here's how to get started.

## 🚀 Quick Start

```bash
# Fork and clone
git clone https://github.com/your-org/ums.git
cd ums

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .

# Type check
mypy ums
```

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=ums --cov-report=html

# Run specific test categories
pytest tests/unit/          # Unit tests (fast)
pytest tests/component/     # Component tests (with DB)
pytest tests/integration/   # Integration tests (with mocks)

# Run a specific test
pytest tests/unit/test_deduplication.py -k "test_identical_texts"
```

## 📝 Code Style

- **Line length:** 100 characters
- **Formatting:** [Ruff](https://docs.astral.sh/ruff/)
- **Types:** All functions must have type annotations
- **Docstrings:** Google-style docstrings for public APIs

```python
def calculate_new_confidence(current: float, new_obs: float, decay: float = 1.0) -> float:
    """Calculate updated confidence using Bayesian combination.
    
    Args:
        current: Current confidence value (0.0-1.0)
        new_obs: New observation confidence (0.0-1.0)
        decay: Optional decay factor (default: 1.0)
        
    Returns:
        Updated confidence value clamped to [0.0, 1.0]
    """
    if current <= 0.0:
        return min(new_obs, 1.0)
    result = 1 - (1 - current) * (1 - new_obs) * decay
    return min(max(result, 0.0), 1.0)
```

## 🏗️ Project Structure

```
ums/
├── ums/                    # Main package
│   ├── gateway/           # FastAPI REST API
│   ├── observation/       # Observation engine
│   ├── memory/            # Memory engine
│   ├── recall/            # Recall engine
│   ├── distillation/      # Distillation pipeline
│   ├── llm/               # LLM abstraction
│   ├── models/            # Pydantic data models
│   ├── storage/           # Storage layer
│   └── utils/             # Utilities
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── component/         # Component tests
│   └── integration/       # Integration tests
└── docs/                  # Documentation
```

## 🔧 Adding a New Feature

1. **Create an issue** describing the feature
2. **Fork the repo** and create a feature branch
3. **Write tests first** (TDD approach)
4. **Implement the feature**
5. **Run the full test suite**
6. **Submit a PR** with a clear description

## 🐛 Reporting Bugs

Include in your bug report:
- Python version and OS
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs or error messages
- Minimal code example if possible

## 📦 Publishing (Maintainers)

```bash
# Bump version in pyproject.toml
# Update CHANGELOG.md
git tag v0.1.1
git push origin v0.1.1

# Build and publish
python -m build
twine upload dist/*
```

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.