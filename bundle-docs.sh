#!/usr/bin/env bash
#
# Bundle the canonical docs at /docs into each SDK package so they ship
# with the published artifacts (npm tarball, Python wheel) and become
# discoverable by AI agents that introspect installed packages.
#
# Outputs (all git-ignored — regenerated on every run):
#
#   together-sandbox-typescript/
#   ├── LLMS.md
#   └── docs/
#       ├── sdk.md         (← /docs/typescript-sdk.md)
#       ├── cli.md         (← /docs/cli.md)
#       └── sandboxes.md   (← /docs/sandboxes.md)
#
#   together-sandbox-python/
#   ├── LLMS.md
#   └── docs/
#       ├── sdk.md         (← /docs/python-sdk.md)
#       ├── cli.md         (← /docs/cli.md)
#       └── sandboxes.md   (← /docs/sandboxes.md)
#
# Run from anywhere — paths resolve relative to this script's location.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
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

bundle() {
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

  echo "==> Bundling docs into $package_dir"

  # Clean previous output so deletions in /docs propagate
  rm -rf "$docs_target"
  mkdir -p "$docs_target"

  cp "$SRC_DOCS/$sdk_doc"     "$docs_target/sdk.md"
  cp "$SRC_DOCS/cli.md"       "$docs_target/cli.md"
  cp "$SRC_DOCS/sandboxes.md" "$docs_target/sandboxes.md"

  # Render LLMS.md from the shared template with per-package substitutions
  sed \
    -e '/^<!--$/,/^-->$/d' \
    -e "s|{{LANGUAGE}}|$language|g" \
    -e "s|{{INSTALL_COMMAND}}|$install_cmd|g" \
    "$TEMPLATE" \
    | sed '/./,$!d' \
    > "$target_dir/LLMS.md"
}

bundle "together-sandbox-typescript" "typescript-sdk.md" "TypeScript" "npm install together-sandbox"
bundle "together-sandbox-python"     "python-sdk.md"     "Python"     "pip install together-sandbox"

echo "==> Done."
