# syntax=docker/dockerfile:1
# ═══════════════════════════════════════════════════════════════════════
# Price-My-Car (AutoIntel) — Streamlit used-car price intelligence app
#
# Build targets:
#   prod (default) — production Streamlit server (:8501)
#   dev            — hot reload for local development
#
# The ML artifacts in ml_ready/ (models, preprocessor) are baked into the
# image when present in the build context. If missing, the app degrades
# to demo mode gracefully. Run setup.sh inside the image to (re)generate
# artifacts from Cleaned_Car_data.csv.
#
# Usage:
#   docker build -t autointel .
#   docker compose up -d
# ═══════════════════════════════════════════════════════════════════════

# ── Base stage ─────────────────────────────────────────────────────────
FROM python:3.12-slim AS base

LABEL org.opencontainers.image.title="AutoIntel"
LABEL org.opencontainers.image.description="Used car price prediction dashboard (Streamlit)"
LABEL org.opencontainers.image.version="6.0"
LABEL org.opencontainers.image.vendor="Price-My-Car"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        tini \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Deps stage ─────────────────────────────────────────────────────────
FROM base AS deps

COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    # Upgrade build-time/transitive packages with known HIGH CVEs
    # (setuptools CVE-2025-47273, wheel CVE-2026-24049, msgpack GHSA-6v7p-g79w-8964,
    #  jaraco.context CVE-2026-23949) — flagged by the CI trivy gate.
    pip install --no-cache-dir --upgrade \
        "setuptools>=78.1.1" \
        "wheel>=0.46.2" \
        "msgpack>=1.2.1" \
        "jaraco-context>=6.1.0"

# ── Prod stage ─────────────────────────────────────────────────────────
FROM deps AS prod

RUN useradd --create-home --uid 10001 appuser && \
    mkdir -p /app/ml_ready /app/report_output /app/archived_logs /app/latest_logs && \
    chown -R appuser:appuser /app

# Application code + data + ML artifacts
COPY app/ ./app/
COPY scripts/backfills/prepare_ml_data.py ./scripts/backfills/
COPY data/ ./data/
COPY ml_ready/ ./ml_ready/
COPY .streamlit/ ./.streamlit/

# Generate the gitignored .npy preprocessed files at build time from the
# committed CSV so the dashboard runs with real data, not demo mode.
# prepare_ml_data.py only needs pandas/numpy/sklearn/joblib (already in
# requirements) and the committed CSV — if it fails, the build fails
# loudly rather than silently shipping a demo-mode image.
RUN python scripts/backfills/prepare_ml_data.py

USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -fsS http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["streamlit", "run", "app/streamlit_app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]

# ── Dev stage: hot reload + test tooling ───────────────────────────────
FROM deps AS dev

RUN pip install --no-cache-dir pytest

RUN useradd --create-home --uid 10001 appuser && \
    mkdir -p /app/ml_ready /app/report_output && \
    chown -R appuser:appuser /app

COPY app/ ./app/
COPY tests/ ./tests/
COPY scripts/backfills/prepare_ml_data.py ./scripts/backfills/
COPY data/ ./data/
COPY ml_ready/ ./ml_ready/
COPY .streamlit/ ./.streamlit/
RUN python scripts/backfills/prepare_ml_data.py

USER appuser

EXPOSE 8501

CMD ["streamlit", "run", "app/streamlit_app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false", \
     "--server.fileWatcherType=polling", \
     "--server.runOnSave=true"]
