#!/usr/bin/env bash
# Regenerate both OpenAPI clients from the specs in the parent directory.
# Run from the together-sandbox-python/ directory.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# pyopenapi-gen cannot handle top-level schemas that are pure $ref aliases
# (e.g. "Task": { "$ref": "#/components/schemas/TaskItem" }).
# Pre-process: wrap them in allOf, which is semantically identical.
preprocess_spec() {
  local input="$1"
  local output="$2"
  python3 - "$input" "$output" <<'EOF'
import json, sys

with open(sys.argv[1]) as f:
    spec = json.load(f)

schemas = spec.get("components", {}).get("schemas", {})
for name, schema in schemas.items():
    if list(schema.keys()) == ["$ref"]:
        schemas[name] = {"allOf": [{"$ref": schema["$ref"]}]}

with open(sys.argv[2], "w") as f:
    json.dump(spec, f)
EOF
}

echo "Generating API client from api-openapi.json..."
pyopenapi-gen "$SCRIPT_DIR/../api-openapi.json" \
  --project-root "$SCRIPT_DIR" \
  --output-package together_sandbox.api \
  --core-package together_sandbox.core \
  --force \
  --no-postprocess

echo "Generating Sandbox client from sandbox-openapi.json..."
SANDBOX_SPEC="$SCRIPT_DIR/.tmp-sandbox-spec.json"
preprocess_spec "$SCRIPT_DIR/../sandbox-openapi.json" "$SANDBOX_SPEC"
pyopenapi-gen "$SANDBOX_SPEC" \
  --project-root "$SCRIPT_DIR" \
  --output-package together_sandbox.sandbox \
  --core-package together_sandbox.core \
  --force \
  --no-postprocess
rm -f "$SANDBOX_SPEC"

# pyopenapi-gen bug: it writes literal "\n" (backslash-n) instead of real newlines
# in the main client __init__.py files. This makes the entire file a single comment
# line to Python's parser, so nothing is exported and everything is typed as Any.
# Fix by replacing b'\n' (literal 2-byte sequence 0x5C 0x6E) with real newlines.
echo "Post-processing: fixing literal \\n bug in generated __init__.py files..."
python3 - "$SCRIPT_DIR" <<'EOF'
import sys, pathlib

root = pathlib.Path(sys.argv[1]) / "together_sandbox"
for rel in ["api/__init__.py", "sandbox/__init__.py"]:
    path = root / rel
    if not path.exists():
        continue
    content = path.read_bytes()
    fixed = content.replace(b'\\n', b'\n')
    if fixed != content:
        path.write_bytes(fixed)
        print(f"  Fixed {rel} ({content.count(b'\\n')} replacements)")
    else:
        print(f"  {rel}: no literal \\n found (already clean)")
EOF

echo "Done. Both clients available via: from together_sandbox import ApiClient, SandboxClient"
