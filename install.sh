#!/usr/bin/env bash
set -euo pipefail

REPO="togethercomputer/together-sandbox"
VERSION="${VERSION:-latest}"
INSTALL_DIR="${INSTALL_DIR:-/usr/local/bin}"

# Require GitHub token for private repository access
if [ -z "${GITHUB_TOKEN:-}" ]; then
  echo "Error: GITHUB_TOKEN is not set."
  echo "Authenticate with the GitHub CLI and re-run:"
  echo ""
  echo "  GITHUB_TOKEN=\$(gh auth token) curl -fsSL -H \"Authorization: Bearer \$(gh auth token)\" \\"
  echo "    https://raw.githubusercontent.com/${REPO}/main/install.sh | bash"
  echo ""
  exit 1
fi

# Detect OS
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
case "$OS" in
  linux)   ;;
  darwin)  ;;
  msys*|mingw*|cygwin*) OS="windows" ;;
  *)
    echo "Error: Unsupported operating system: $OS"
    exit 1
    ;;
esac

# Detect architecture
ARCH=$(uname -m)
case "$ARCH" in
  x86_64)        ARCH="x64"   ;;
  arm64|aarch64) ARCH="arm64" ;;
  *)
    echo "Error: Unsupported architecture: $ARCH"
    exit 1
    ;;
esac

# Build binary name
BINARY="together-sandbox-${OS}-${ARCH}"
[ "$OS" = "windows" ] && BINARY="${BINARY}.exe"

# Build download URL
if [ "$VERSION" = "latest" ]; then
  URL="https://github.com/${REPO}/releases/latest/download/${BINARY}"
else
  URL="https://github.com/${REPO}/releases/download/${VERSION}/${BINARY}"
fi

TARGET="${INSTALL_DIR}/together-sandbox"

echo "Downloading together-sandbox ${VERSION} (${OS}/${ARCH})..."
curl -fsSL --progress-bar -H "Authorization: Bearer ${GITHUB_TOKEN}" "$URL" -o /tmp/together-sandbox-download
chmod +x /tmp/together-sandbox-download

if [ -w "$INSTALL_DIR" ]; then
  mv /tmp/together-sandbox-download "$TARGET"
else
  sudo mv /tmp/together-sandbox-download "$TARGET"
fi

echo ""
echo "✓ together-sandbox installed to $TARGET"
echo ""
echo "  together-sandbox --help"
echo ""
