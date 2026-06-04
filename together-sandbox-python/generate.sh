#!/usr/bin/env bash
# Regenerate both OpenAPI clients from the specs in the parent directory.
# Run from the repo root: bash together-sandbox-python/generate.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

mkdir -p "$SCRIPT_DIR/together_sandbox"

# Output dirs are underscore-prefixed (_api, _sandbox_client) to mark the
# generated clients as internal/private — they are not part of the SDK's public
# API. See EXPORTED_TYPES.md at the repo root.
echo "Generating API client from api-openapi.json..."
python3 -m openapi_python_client generate \
  --path "$REPO_ROOT/api-openapi.json" \
  --meta none \
  --output-path "$SCRIPT_DIR/together_sandbox/_api" \
  --overwrite

echo "Generating Sandbox client from sandbox-openapi.json..."
python3 -m openapi_python_client generate \
  --path "$REPO_ROOT/sandbox-openapi.json" \
  --meta none \
  --output-path "$SCRIPT_DIR/together_sandbox/_sandbox_client" \
  --overwrite

echo "Done. Generated internal clients into together_sandbox/_api and together_sandbox/_sandbox_client."
