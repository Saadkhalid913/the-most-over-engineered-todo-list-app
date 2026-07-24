#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAME="${1:-}"
BASE="${2:-}"

usage() {
  echo "Usage: $0 <branch-name> [base-branch]"
  echo "Creates a worktree at .worktrees/<branch-name>"
  exit 1
}

[[ -n "$NAME" ]] || usage

if [[ -z "$BASE" ]]; then
  BASE="$(git -C "$ROOT" rev-parse --abbrev-ref HEAD)"
fi

WORKTREE_DIR="${ROOT}/.worktrees/${NAME}"

if [[ -e "$WORKTREE_DIR" ]]; then
  echo "Worktree already exists: $WORKTREE_DIR"
  exit 1
fi

mkdir -p "${ROOT}/.worktrees"

if git -C "$ROOT" show-ref --verify --quiet "refs/heads/${NAME}"; then
  git -C "$ROOT" worktree add "$WORKTREE_DIR" "$NAME"
else
  git -C "$ROOT" worktree add -b "$NAME" "$WORKTREE_DIR" "$BASE"
fi

echo "Worktree ready: $WORKTREE_DIR"
echo "  cd $WORKTREE_DIR"
echo "  ./dev/start.sh"
