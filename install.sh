#!/usr/bin/env bash
set -euo pipefail

REPO="togethercomputer/together-sandbox"
VERSION="${VERSION:-latest}"
# Install into a user-owned prefix by default, as rustup/bun/deno/uv do, so the
# script never needs sudo. The cost is that the prefix may not be on PATH — we
# check for that below and print the line to add.
INSTALL_DIR="${INSTALL_DIR:-${XDG_BIN_HOME:-$HOME/.local/bin}}"

# Detect OS
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
case "$OS" in
  linux)   ;;
  darwin)  ;;
  msys*|mingw*|cygwin*) OS="windows" ;;
  *)
    echo "Error: Unsupported operating system: $OS" >&2
    exit 1
    ;;
esac

# Detect architecture
ARCH=$(uname -m)
case "$ARCH" in
  x86_64)        ARCH="x64"   ;;
  arm64|aarch64) ARCH="arm64" ;;
  *)
    echo "Error: Unsupported architecture: $ARCH" >&2
    exit 1
    ;;
esac

# Build binary name
BINARY="together-sandbox-${OS}-${ARCH}"
[ "$OS" = "windows" ] && BINARY="${BINARY}.exe"

# Build download URL. Release tags are prefixed by the release-please component
# name, so accept either a bare version ("3.2.0") or the full tag.
if [ "$VERSION" = "latest" ]; then
  URL="https://github.com/${REPO}/releases/latest/download/${BINARY}"
else
  TAG="$VERSION"
  case "$TAG" in
    together-sandbox-workspace-v*) ;;
    v*) TAG="together-sandbox-workspace-${TAG}" ;;
    *)  TAG="together-sandbox-workspace-v${TAG}" ;;
  esac
  URL="https://github.com/${REPO}/releases/download/${TAG}/${BINARY}"
fi

TARGET="${INSTALL_DIR}/together-sandbox"

mkdir -p "$INSTALL_DIR" ||
  { echo "Error: could not create install directory $INSTALL_DIR" >&2; exit 1; }

if [ ! -w "$INSTALL_DIR" ]; then
  echo "Error: $INSTALL_DIR is not writable." >&2
  echo "Choose a directory you own, e.g.:" >&2
  echo "  curl -fsSL https://raw.githubusercontent.com/${REPO}/main/install.sh | INSTALL_DIR=\$HOME/.local/bin bash" >&2
  exit 1
fi

TMP=$(mktemp "${TMPDIR:-/tmp}/together-sandbox.XXXXXX")
trap 'rm -f "$TMP"' EXIT

echo "Downloading together-sandbox ${VERSION} (${OS}/${ARCH})..."
# --retry covers the transient 5xx the release CDN occasionally returns; without
# it a blip fails the whole install after the user has already waited.
curl -fSL --progress-bar --retry 3 --retry-delay 1 --retry-all-errors "$URL" -o "$TMP"
chmod +x "$TMP"
mv "$TMP" "$TARGET"
trap - EXIT

# ─── PATH check ───────────────────────────────────────────────────────────────

# Resolve a directory to its physical path so that symlinked or non-canonical
# PATH entries (e.g. /home -> /System/Volumes/Data/home) still match.
canonicalize() {
  (cd "$1" 2>/dev/null && pwd -P) || printf '%s' "$1"
}

on_path() {
  local target entry
  target=$(canonicalize "$1")
  local IFS=:
  for entry in $PATH; do
    [ -n "$entry" ] || continue
    if [ "$entry" = "$1" ] || [ "$(canonicalize "$entry")" = "$target" ]; then
      return 0
    fi
  done
  return 1
}

# Print the display form of the install dir, abbreviating $HOME for readability.
display_dir() {
  case "$INSTALL_DIR" in
    "$HOME"/*) printf '$HOME/%s' "${INSTALL_DIR#"$HOME"/}" ;;
    *)         printf '%s' "$INSTALL_DIR" ;;
  esac
}

echo ""
echo "✓ together-sandbox installed to $TARGET"

if on_path "$INSTALL_DIR"; then
  echo ""
  echo "  together-sandbox --help"
  echo ""
else
  dir=$(display_dir)
  echo ""
  echo "$INSTALL_DIR is not on your PATH. Add it by running:"
  echo ""
  if [ "${SHELL##*/}" = "fish" ]; then
    # fish_add_path persists to a universal variable, so it is run once rather
    # than appended to a config file.
    echo "  fish_add_path $dir"
    echo ""
    echo "That takes effect in new shells, and in this one after:"
    echo ""
    echo "  set -x PATH $INSTALL_DIR \$PATH"
  else
    case "${SHELL##*/}" in
      zsh)  rc="${ZDOTDIR:-\$HOME}/.zshrc" ;;
      # macOS login shells read .bash_profile; elsewhere .bashrc is the norm.
      bash) [ "$OS" = "darwin" ] && rc="\$HOME/.bash_profile" || rc="\$HOME/.bashrc" ;;
      *)    rc="\$HOME/.profile" ;;
    esac
    echo "  echo 'export PATH=\"$dir:\$PATH\"' >> $rc"
    echo ""
    echo "Then restart your shell, or run this to use it right now:"
    echo ""
    echo "  export PATH=\"$INSTALL_DIR:\$PATH\""
  fi
  echo ""
fi

# A copy left over from an older install (which defaulted to /usr/local/bin)
# would shadow this one if it comes first on PATH. Say so rather than let the
# user wonder why `--version` is stale.
if command -v together-sandbox >/dev/null 2>&1; then
  found=$(command -v together-sandbox)
  if [ "$(canonicalize "$(dirname "$found")")" != "$(canonicalize "$INSTALL_DIR")" ]; then
    echo "Warning: another together-sandbox earlier on your PATH will take precedence:"
    echo "  $found"
    echo "Remove it, or put $INSTALL_DIR first on your PATH."
    echo ""
  fi
fi
