#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

API_HOST="${API_HOST:-127.0.0.1}"
API_PORT="${API_PORT:-8000}"
WEB_PORT="${WEB_PORT:-3000}"
DATABASE_URL="${DATABASE_URL:-mysql+pymysql://todos:todos@127.0.0.1:3306/todos}"
export DATABASE_URL

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required to run the local MariaDB instance" >&2
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "docker compose is required to run the local MariaDB instance" >&2
  exit 1
fi

if [[ ! -x .venv/bin/uvicorn ]]; then
  echo "Creating .venv and installing backend deps..."
  python3 -m venv .venv
  .venv/bin/pip install -r backend/requirements.txt
fi

# Reinstall when SQLAlchemy/Alembic are missing (deps were added after first venv create).
if [[ ! -x .venv/bin/alembic ]] || ! .venv/bin/python -c "import sqlalchemy, pymysql" 2>/dev/null; then
  echo "Installing/updating backend deps..."
  .venv/bin/pip install -r backend/requirements.txt
fi

if [[ ! -x .venv/bin/pre-commit ]] || [[ ! -x .venv/bin/ruff ]]; then
  echo "Installing dev tooling (ruff, pre-commit)..."
  .venv/bin/pip install -r requirements-dev.txt
fi

if [[ ! -d frontend/node_modules ]]; then
  echo "Installing frontend deps..."
  (cd frontend && npm install)
fi

if [[ ! -f .git/hooks/pre-commit ]] || ! grep -q "pre-commit" .git/hooks/pre-commit 2>/dev/null; then
  echo "Installing git pre-commit hooks..."
  .venv/bin/pre-commit install
fi

echo "Starting MariaDB..."
docker compose -f dev/docker-compose.yml up -d

echo "Waiting for MariaDB to become healthy..."
for _ in $(seq 1 60); do
  health_status="$(docker inspect --format='{{.State.Health.Status}}' todo-mariadb 2>/dev/null || true)"
  if [[ "$health_status" == "healthy" ]]; then
    break
  fi
  sleep 1
done

if [[ "$(docker inspect --format='{{.State.Health.Status}}' todo-mariadb)" != "healthy" ]]; then
  echo "MariaDB did not become healthy in time" >&2
  docker compose -f dev/docker-compose.yml logs db >&2 || true
  exit 1
fi

echo "Running database migrations..."
(cd backend && ../.venv/bin/alembic upgrade head)

PIDS=()

cleanup() {
  for pid in "${PIDS[@]:-}"; do
    kill "$pid" 2>/dev/null || true
  done
}

trap cleanup EXIT INT TERM

echo "DB   → MariaDB on localhost:3306 (database: todos)"
echo "API  → http://${API_HOST}:${API_PORT}  (docs: /docs)"
echo "Web  → http://localhost:${WEB_PORT}"
echo

.venv/bin/uvicorn app.main:app \
  --app-dir backend \
  --reload \
  --host "$API_HOST" \
  --port "$API_PORT" &
PIDS+=($!)

(cd frontend && npm run dev -- --port "$WEB_PORT") &
PIDS+=($!)

wait
