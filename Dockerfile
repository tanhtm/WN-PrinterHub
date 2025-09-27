# syntax=docker/dockerfile:1

# ------------------ Base build image ------------------
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       iputils-ping netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir uv \
    && if [ -f uv.lock ]; then uv sync --frozen --no-dev; else uv pip install --system . ; fi

# ------------------ Runtime image ------------------
FROM python:3.11-slim AS runtime
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    WN_HOST=0.0.0.0 \
    WN_PORT=8088 \
    WN_LOG_LEVEL=INFO \
    USE_AUTH=true \
    WN_PRINTER_DEFAULT_PORT=9100

RUN addgroup --system app && adduser --system --ingroup app app

COPY --from=base /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=base /usr/local/bin /usr/local/bin

COPY app ./app
COPY README.md ./
COPY LICENSE ./

EXPOSE 8088

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request,sys,os;url=f'http://127.0.0.1:{os.getenv('WN_PORT','8088')}/health';\ntry:\n  with urllib.request.urlopen(url, timeout=2) as r: sys.exit(0 if r.status==200 else 1)\nexcept Exception: sys.exit(1)" || exit 1

USER app

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8088", "--log-level", "info"]
