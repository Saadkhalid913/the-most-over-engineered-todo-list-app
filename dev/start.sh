#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

API_HOST="${API_HOST:-127.0.0.1}"
API_PORT="${API_PORT:-8000}"
WEB_PORT="${WEB_PORT:-3000}"

if [[ ! -x .venv/bin/uvicorn ]]; then
  echo "Creating .venv and installing backend deps..."
  python3 -m venv .venv
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

PIDS=()

cleanup() {
  for pid in "${PIDS[@]:-}"; do
    kill "$pid" 2>/dev/null || true
  done
}

trap cleanup EXIT INT TERM

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
