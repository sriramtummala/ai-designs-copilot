# syntax=docker/dockerfile:1.4
# Build context: monorepo root
#   docker build -f apps/api/Dockerfile .
#   docker run --env-file .env -p 8000:8000 <image>

# ── Stage 1: install deps into an isolated venv ─────────────────────────────
FROM python:3.11-slim-bookworm AS builder

WORKDIR /build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY apps/api/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.11-slim-bookworm

WORKDIR /app

# Copy only the pre-built venv — no build tools in the final image
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Non-root user
RUN addgroup --system appgroup \
 && adduser --system --ingroup appgroup appuser

# Copy monorepo libs and API source — build context must be the repo root
COPY libs/ libs/
COPY apps/api/src/ apps/api/src/

USER appuser

EXPOSE 8000

ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Runtime secrets (OPENAI_API_KEY, CONTENTFUL_*) must be injected at run time
# via --env-file or -e flags — never bake credentials into the image.

CMD ["uvicorn", "apps.api.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
