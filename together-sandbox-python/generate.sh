#!/usr/bin/env bash
# Regenerate both OpenAPI clients from the specs in the parent directory.
# Run from the repo root: bash together-sandbox-python/generate.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Generating API client from api-openapi.json..."
python3 -m openapi_python_client generate \
  --path "$REPO_ROOT/api-openapi.json" \
  --meta none \
  --output-path "$SCRIPT_DIR/together_sandbox/api" \
  --overwrite

echo "Generating Sandbox client from sandbox-openapi.json..."
python3 -m openapi_python_client generate \
  --path "$REPO_ROOT/sandbox-openapi.json" \
  --meta none \
  --output-path "$SCRIPT_DIR/together_sandbox/sandbox" \
  --overwrite

echo "Done. Both clients available via: from together_sandbox import ApiClient, SandboxClient"
