#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

docker compose -f dev/docker-compose.yml exec db \
  mariadb -utodos -ptodos todos "$@"
