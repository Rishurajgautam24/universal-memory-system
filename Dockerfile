FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

FROM python:3.12-slim

RUN groupadd -r ums && useradd -r -g ums -d /app -s /bin/false ums

WORKDIR /app

COPY --from=builder /app/.venv ./.venv
COPY ums/ ./ums/
COPY scripts/ ./scripts/

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app" \
    PYTHONUNBUFFERED=1

EXPOSE 8000

USER ums

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; exit(0 if httpx.get('http://localhost:8000/health').status_code == 200 else 1)"

CMD ["uvicorn", "ums.gateway.app:create_app", "--host", "0.0.0.0", "--port", "8000"]
