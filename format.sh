#!/usr/bin/env bash
# Format all TS/JS/JSON/MD/YAML with Prettier and all Python with Ruff.
#
# Usage:
#   bash format.sh         # write changes in place
#   bash format.sh check   # exit non-zero if any file would change (CI)
#
# First run auto-creates a local venv at .venv-format/ and installs Ruff
# into it. Prettier comes from `npm install` at the repo root.

set -euo pipefail
cd "$(dirname "$0")"

VENV=".venv-format"
RUFF_VERSION="0.15.15"

if [ ! -x "$VENV/bin/ruff" ]; then
  echo "→ Bootstrapping $VENV (one-time, ~10MB)…"
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install --quiet --upgrade pip
  "$VENV/bin/pip" install --quiet "ruff==$RUFF_VERSION"
fi
RUFF="$VENV/bin/ruff"

mode="${1:-write}"
case "$mode" in
  write)
    npx prettier --write .
    "$RUFF" format together-sandbox-python
    ;;
  check)
    npx prettier --check .
    "$RUFF" format --check together-sandbox-python
    ;;
  *)
    echo "usage: $0 [write|check]" >&2
    exit 2
    ;;
esac