FROM ubuntu:24.04

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl wget git build-essential \
    python3 python3-pip python3-venv python3-dev \
    ca-certificates gnupg lsb-release \
    # nodejs npm \
    dnsutils \
    supervisor

RUN ln -sf /usr/share/zoneinfo/Asia/Ho_Chi_Minh /etc/localtime

RUN python3 -m venv /app/.venv

RUN /app/.venv/bin/pip install --upgrade pip && \
    /app/.venv/bin/pip install uv

COPY . .

COPY .env.docker .env

RUN /app/.venv/bin/uv sync

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8088

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]