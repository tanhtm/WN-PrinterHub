# syntax=docker/dockerfile:1

# ================== BUILD STAGE ==================
FROM python:3.11-slim AS build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

# System build dependencies (uvicorn[standard] -> uvloop, httptools)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential curl iputils-ping netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./

# Install only runtime deps (no dev extras)
RUN pip install --upgrade --no-cache-dir pip \
    && pip install --no-cache-dir .

COPY app ./app

# ================== RUNTIME STAGE ==================
FROM python:3.11-slim AS runtime
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    WN_HOST=0.0.0.0 \
    WN_PORT=8088 \
    WN_LOG_LEVEL=INFO \
    WN_PRINTER_DEFAULT_PORT=9100 \
    USE_AUTH=true

LABEL org.opencontainers.image.title="WN-PrinterHub" \
      org.opencontainers.image.description="Local LAN printer connector (FastAPI)" \
      org.opencontainers.image.source="https://github.com/whiteneuron/WN-PrinterHub" \
      org.opencontainers.image.licenses="MIT"

# Copy only what we need from build image (python + site-packages + app)
COPY --from=build /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=build /usr/local/bin /usr/local/bin
COPY --from=build /app/app ./app
COPY README.md ./
COPY LICENSE ./

# Add a non-root user
RUN addgroup --system app && adduser --system --ingroup app app \
    && chown -R app:app /app

EXPOSE 8088

# Lightweight healthcheck using curl
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -fsS http://127.0.0.1:8088/health >/dev/null || exit 1

USER app

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8088", "--log-level", "info"]
