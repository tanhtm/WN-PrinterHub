#!/usr/bin/env bash
set -euo pipefail

echo "WARNING: Lệnh này sẽ xóa containers + network + volumes (bao gồm dữ liệu Postgres)." >&2
read -p "Nhập YES để xác nhận: " CONFIRM
if [ "${CONFIRM}" != "YES" ]; then
  echo "Hủy bỏ." >&2
  exit 1
fi

echo "[INFO] Bringing down stack & removing volumes..."
docker compose --env-file .env.docker down --volumes --remove-orphans

echo "[INFO] Dangling volumes (nếu còn):"
docker volume ls | grep dinehub || true

echo "[DONE] Stack destroyed."
