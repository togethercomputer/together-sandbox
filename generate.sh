#!/usr/bin/env bash
# generate.sh — regenerate all SDKs from the OpenAPI specs.
#
# Run from the repo root:
#   bash generate.sh
#
# What this does:
#   1. Patches api-openapi.json: promotes every inline `data` object inside
#      allOf response schemas to a named $ref schema (e.g. VMStartResponseData).
#      The management API spec was written with anonymous inline objects, which
#      confuses Python code generators that need real class names at runtime.
#      TypeScript is unaffected because its type system can express inline shapes
#      directly, but Python generators collide all anonymous objects onto a single
#      Data_ class and lose the field information.
#   2. Regenerates the TypeScript SDK (together-sandbox-typescript).
#   3. Regenerates the Python SDK (together-sandbox-python).
#   4. Bundles per-SDK docs (LLMS.md + docs/) into each SDK package. This is a
#      build prerequisite, not just a publish step: the Python wheel's
#      force-include validates the doc paths exist on every wheel build,
#      including the one `pip install .[dev]` performs.
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_SPEC="$REPO_ROOT/api-openapi.json"

# ─── Step 1: patch api-openapi.json ──────────────────────────────────────────
#
# For every schema that has an allOf part containing an inline `data` object
# (i.e. `"data": { "type": "object", "properties": { ... } }` instead of
# `"data": { "$ref": "..." }`), we:
#   • extract the inline object into a new top-level named schema
#     called <ParentSchemaName>Data
#   • replace the inline definition with a $ref pointing to that new schema
#
# This is idempotent: if the $ref already exists the script leaves it alone.

echo "Patching $API_SPEC: promoting inline data objects to named schemas..."
python3 - "$API_SPEC" <<'PYEOF'
import json, copy, sys

path = sys.argv[1]
with open(path) as f:
    spec = json.load(f)

schemas = spec["components"]["schemas"]
new_schemas = {}

for schema_name, schema in schemas.items():
    for part in schema.get("allOf", []):
        data_prop = part.get("properties", {}).get("data", {})
        # Only act on inline objects — skip if it is already a $ref
        if data_prop and "$ref" not in data_prop:
            named = f"{schema_name}Data"
            new_schemas[named] = copy.deepcopy(data_prop)
            part["properties"]["data"] = {"$ref": f"#/components/schemas/{named}"}

added = [n for n in new_schemas if n not in schemas]
schemas.update(new_schemas)

# Fix global security: replace empty [] with a reference to the defined scheme.
# An empty security array means "no global default", which triggers security linters.
# The authorization scheme is defined in components/securitySchemes.
if spec.get("security") == []:
    spec["security"] = [{"authorization": []}]
    print("  Fixed global security: set to [{authorization: []}]")

with open(path, "w") as f:
    json.dump(spec, f, indent=2)

if added:
    print(f"  Promoted {len(added)} inline schema(s): {', '.join(sorted(added))}")
else:
    print("  Nothing to promote — spec is already clean.")
PYEOF

# ─── Step 2: TypeScript SDK ───────────────────────────────────────────────────
#
# Uses @hey-api/openapi-ts with @hey-api/client-fetch to generate typed fetch
# clients from both OpenAPI specs into together-sandbox-typescript/src/api-clients/.

echo "Generating TypeScript SDK..."
cd "$REPO_ROOT/together-sandbox-typescript"
npm run generate

# ─── Step 3: Python SDK ───────────────────────────────────────────────────────
#
# Uses pyopenapi-gen to generate async Python clients. The sandbox spec is
# pre-processed to wrap any remaining pure $ref alias schemas in allOf (a
# separate known limitation of pyopenapi-gen — see generate.sh in that package
# for details).

echo "Generating Python SDK..."
cd "$REPO_ROOT/together-sandbox-python"
bash generate.sh

# ─── Step 4: Bundle per-SDK docs ──────────────────────────────────────────────
#
# Copies /docs/*.md into each SDK package (renamed to sdk.md / cli.md /
# sandboxes.md) and renders LLMS.md from LLMS-template.md with per-package
# substitutions. Folded into generate.sh because the Python wheel's
# [tool.hatch.build.targets.wheel.force-include] requires these files to
# exist on disk before any wheel build — including the one triggered by
# `pip install .[dev]` — will succeed.

echo "Bundling per-SDK docs..."

SRC_DOCS="$REPO_ROOT/docs"
TEMPLATE="$REPO_ROOT/LLMS-template.md"

if [[ ! -d "$SRC_DOCS" ]]; then
  echo "error: source docs directory not found: $SRC_DOCS" >&2
  exit 1
fi

if [[ ! -f "$TEMPLATE" ]]; then
  echo "error: LLMS template not found: $TEMPLATE" >&2
  exit 1
fi

bundle_docs() {
  local package_dir="$1"  # e.g. together-sandbox-typescript
  local sdk_doc="$2"      # e.g. typescript-sdk.md
  local language="$3"     # e.g. TypeScript
  local install_cmd="$4"  # e.g. npm install together-sandbox

  local target_dir="$REPO_ROOT/$package_dir"
  local docs_target="$target_dir/docs"

  if [[ ! -d "$target_dir" ]]; then
    echo "error: package directory not found: $target_dir" >&2
    exit 1
  fi

  echo "  → $package_dir"

  # Clean previous output so deletions in /docs propagate
  rm -rf "$docs_target"
  mkdir -p "$docs_target"

  cp "$SRC_DOCS/$sdk_doc"     "$docs_target/sdk.md"
  cp "$SRC_DOCS/cli.md"       "$docs_target/cli.md"
  cp "$SRC_DOCS/sandboxes.md" "$docs_target/sandboxes.md"

  # Render LLMS.md from the shared template:
  #   - strip the leading <!-- ... --> editor note
  #   - substitute {{LANGUAGE}} and {{INSTALL_COMMAND}}
  #   - drop any leading blank lines left by the comment removal
  sed \
    -e '/^<!--$/,/^-->$/d' \
    -e "s|{{LANGUAGE}}|$language|g" \
    -e "s|{{INSTALL_COMMAND}}|$install_cmd|g" \
    "$TEMPLATE" \
    | sed '/./,$!d' \
    > "$target_dir/LLMS.md"
}

bundle_docs "together-sandbox-typescript" "typescript-sdk.md" "TypeScript" "npm install together-sandbox"
bundle_docs "together-sandbox-python"     "python-sdk.md"     "Python"     "pip install together-sandbox"

echo ""
echo "All SDKs generated successfully."
