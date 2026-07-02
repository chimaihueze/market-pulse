FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    HOME=/app \
    UV_CACHE_DIR=/app/.cache

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev

COPY app ./app
COPY observability ./observability

RUN groupadd --system app && useradd --system --gid app app && \
    mkdir -p /app/.cache && \
    chown -R app:app /app

USER app

CMD ["uv", "run", "python", "-m", "app.ingestion.main"]
