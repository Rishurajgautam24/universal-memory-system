.PHONY: install dev test test-unit test-component test-e2e lint migrate distill

install:; uv sync --all-extras
dev:; uv run python -m ums.main
test:; uv run pytest tests/ -v --tb=short
test-unit:; uv run pytest tests/unit -v
test-component:; uv run pytest tests/component -v
test-e2e:; uv run pytest tests/integration -v
lint:; uv run ruff check . --fix && uv run mypy ums/
migrate:; uv run python scripts/migrate.py
distill:; uv run python scripts/run_distillation.py
