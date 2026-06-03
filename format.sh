#!/usr/bin/env bash
# Format all TS/JS/JSON/MD/YAML with Prettier and all Python with Ruff.
#
# Usage:
#   bash format.sh         # write changes in place
#   bash format.sh check   # exit non-zero if any file would change (CI)
#
# Prereqs:
#   - Node + `npm install` at the repo root (provides Prettier)
#   - Ruff:  `brew install ruff`  (or `pip install ruff`)

set -euo pipefail
cd "$(dirname "$0")"

mode="${1:-write}"
case "$mode" in
  write)
    npx prettier --write .
    ruff format together-sandbox-python
    ;;
  check)
    npx prettier --check .
    ruff format --check together-sandbox-python
    ;;
  *)
    echo "usage: $0 [write|check]" >&2
    exit 2
    ;;
esac