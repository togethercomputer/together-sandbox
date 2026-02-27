#!/usr/bin/env bash
# Regenerate both OpenAPI clients from the specs in the parent directory.
# Run from the together-sandbox-python/ directory.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Generating API client from api-openapi.json..."
openapi-python-client generate \
  --path "$SCRIPT_DIR/../api-openapi.json" \
  --output-path "$SCRIPT_DIR/.tmp-api" \
  --overwrite

echo "Generating Sandbox client from sandbox-openapi.json..."
openapi-python-client generate \
  --path "$SCRIPT_DIR/../sandbox-openapi.json" \
  --output-path "$SCRIPT_DIR/.tmp-sandbox" \
  --overwrite

echo "Copying generated code into together_sandbox package..."
rm -rf "$SCRIPT_DIR/together_sandbox/api" "$SCRIPT_DIR/together_sandbox/sandbox"
cp -r "$SCRIPT_DIR/.tmp-api"/*/. "$SCRIPT_DIR/together_sandbox/api/"
cp -r "$SCRIPT_DIR/.tmp-sandbox"/*/. "$SCRIPT_DIR/together_sandbox/sandbox/"
rm -rf "$SCRIPT_DIR/.tmp-api" "$SCRIPT_DIR/.tmp-sandbox"

echo "Done. Both clients available via: from together_sandbox import ApiClient, SandboxClient"
