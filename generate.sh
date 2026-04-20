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

echo ""
echo "All SDKs generated successfully."
