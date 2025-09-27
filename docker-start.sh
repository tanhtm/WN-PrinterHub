#!/usr/bin/env bash
set -euo pipefail

# Khởi động lại các container đã stop (không rebuild, không chạy migrate)
echo "[INFO] Starting previously stopped containers..."
docker compose --env-file .env.docker start

echo "[INFO] Containers status:"
docker compose --env-file .env.docker ps
