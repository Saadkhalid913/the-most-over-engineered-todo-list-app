# AGENTS.md

Guidance for coding agents working in this repository.

## What this is

A deliberately over-engineered todo list app used to introduce real-world backend, frontend, and systems design ideas over time. Prefer small, incremental changes that teach one concept well. See `readme.md` for the planned progression.

## Stack

| Area | Tech |
|------|------|
| Backend | FastAPI + Pydantic (`backend/`) |
| Frontend | Next.js App Router + React + Tailwind (`frontend/`) |
| Database | MariaDB 11 via Docker Compose (`dev/docker-compose.yml`) |
| ORM / SQL | SQLAlchemy 2.0 + PyMySQL (sync) |
| Migrations | Alembic (`backend/alembic/`) |
| Local run | `./dev/start.sh` — MariaDB `:3306`, API `:8000`, web `:3000` |
| Format | Ruff (backend), Prettier (frontend) |
| Hooks | pre-commit runs formatters before each commit |
| CI | `.github/workflows/format.yml` checks formatting on PRs |

Todos persist in MariaDB. API/domain shape: `id: UUID`, `text: str`, `done: bool`. DB also stores `created_at` / `updated_at` (not exposed on the API yet).

Default connection URL: `mysql+pymysql://todos:todos@127.0.0.1:3306/todos` (override with `DATABASE_URL`).

## Formatting

Formatters must stay green in CI. Rely on pre-commit so commits are already formatted.

```bash
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/pre-commit install
.venv/bin/pre-commit run --all-files   # format / verify locally
(cd frontend && npm run format)        # prettier write
.venv/bin/ruff format backend          # ruff write
```

- Backend config: `pyproject.toml` (`[tool.ruff]`)
- Frontend config: `frontend/.prettierrc.json`
- Hook config: `.pre-commit-config.yaml`

## Git / PR workflow (required)

**Do not push commits directly to `main`.** Every change lands via pull request.

1. Create a branch from latest `main` (`feat/…`, `fix/…`, `docs/…`, `chore/…`).
2. Make focused commits on that branch.
3. Push the branch and open a PR targeting `main` with `gh pr create`.
4. Wait for required checks (when present), then merge the PR. Do not force-push `main`.

Only use direct pushes to `main` if the user explicitly overrides this rule for that change.

## Working agreements

- Keep the first versions simple; complexity is added intentionally later (logging, auth, etc.).
- Match existing style and file layout. Avoid drive-by refactors.
- Backend layers:
  - Routes in `backend/app/main.py` (HTTP + Depends wiring)
  - Domain logic in `TodoService` (`backend/app/todo_service.py`)
  - Persistence in `TodoRepository` (`backend/app/repositories/todo_repository.py`)
  - SQLAlchemy row model in `backend/app/db/models.py`; sessions in `backend/app/db/session.py`
  - Pydantic API models in `backend/app/models.py`
- Schema changes go through Alembic revisions under `backend/alembic/versions/`.
- Frontend: interactive UI is client components (`"use client"`). Before Next.js changes, read `frontend/AGENTS.md` and the local guides under `frontend/node_modules/next/dist/docs/`.
- Do not commit secrets, `.venv/`, `node_modules/`, or `.next/`.
- Do not amend commits that are already pushed; prefer a new commit.
- Update this file when workflow or conventions change.

## Useful commands

```bash
./dev/start.sh                          # MariaDB + migrate + API + frontend
./dev/db.sh                             # interactive mariadb client in the db container
(cd backend && ../.venv/bin/alembic upgrade head)
.venv/bin/uvicorn app.main:app --app-dir backend --reload --port 8000
(cd frontend && npm run dev)
gh pr create --base main                # open PR for current branch
```
