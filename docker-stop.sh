#!/usr/bin/env bash
set -euo pipefail

# Tạm dừng container nhưng GIỮ nguyên network + volumes + dữ liệu
# Dùng lại bằng: scripts/docker-start.sh

echo "[INFO] Stopping containers (preserve volumes & network)..."
docker compose --env-file .env.docker stop

echo "[HINT] Khởi động lại: bash scripts/docker-start.sh"
echo "[HINT] Nếu muốn xóa hết (containers + network + volumes): bash scripts/docker-destroy.sh"
