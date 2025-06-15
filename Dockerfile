FROM python:3.12-slim-bookworm AS builder

RUN groupadd -r app && useradd -r -g app app -d /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

RUN mkdir -p /app/.local/share/uv /app/.cache/uv && \
    chown -R app:app /app /app

USER app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN --mount=type=cache,target=/app/.cache/uv,uid=999,gid=999 \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --no-editable

COPY --chown=app:app . /app

RUN --mount=type=cache,target=/app/.cache/uv,uid=999,gid=999 \
    uv sync --frozen --no-dev --no-editable

FROM python:3.12-slim-bookworm

RUN groupadd -r app && useradd -r -g app app

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp/* /var/tmp/*

RUN mkdir -p /workspace /app && \
    chown -R app:app /workspace /app

WORKDIR /app

COPY --from=builder --chown=app:app /app/.local /app/.local
COPY --from=builder --chown=app:app /app/.venv /app/.venv

USER app

ENV PATH="/app/.venv/bin:$PATH"

CMD ["moco-voice-mcp"]