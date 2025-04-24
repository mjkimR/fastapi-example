# ---- Builder Stage ----
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ENV TZ=UTC

WORKDIR /.app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies using uv
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# ---- Runtime Stage ----
FROM python:3.12.3-slim AS runtime
ENV TZ=UTC
ENV PYTHONUNBUFFERED=1
ENV PATH="/.app/.venv/bin:$PATH"

# Create a non-root user and group
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --create-home --shell /sbin/nologin appuser

WORKDIR /.app

# Copy virtual environment from builder stage with correct ownership
COPY --from=builder --chown=appuser:appuser /.app/.venv /.app/.venv

# Copy application code and necessary files directly into the runtime stage
# Ensure correct ownership with --chown
COPY --chown=appuser:appuser /alembic.ini /.app/alembic.ini
COPY --chown=appuser:appuser migrations /.app/migrations
COPY --chown=appuser:appuser init_data /.app/init_data
COPY --chown=appuser:appuser app /.app/app
COPY --chown=appuser:appuser docker/start.sh /.app/start.sh

# Grant execution permission to start script
RUN chmod +x /.app/start.sh

# Switch to non-root user
USER appuser

CMD ["sh", "start.sh"]