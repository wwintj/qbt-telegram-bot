#!/usr/bin/env sh
set -eu

APP_DIR="${APP_DIR:-$(pwd)}"
REPO_TARBALL_URL="${REPO_TARBALL_URL:-https://github.com/wwintj/qbt-telegram-bot/archive/refs/heads/main.tar.gz}"

cd "$APP_DIR"

if [ ! -f ".env" ]; then
  echo "ERROR: .env not found in $APP_DIR"
  echo "Please run scripts/install.sh first."
  exit 1
fi

if command -v curl >/dev/null 2>&1; then
  DOWNLOADER="curl"
elif command -v wget >/dev/null 2>&1; then
  DOWNLOADER="wget"
else
  echo "ERROR: curl or wget is required."
  exit 1
fi

TMP_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT INT TERM

echo "Downloading latest source..."
if [ "$DOWNLOADER" = "curl" ]; then
  curl -fsSL "$REPO_TARBALL_URL" -o "$TMP_DIR/source.tar.gz"
else
  wget -qO "$TMP_DIR/source.tar.gz" "$REPO_TARBALL_URL"
fi

mkdir -p "$TMP_DIR/src"
tar -xzf "$TMP_DIR/source.tar.gz" -C "$TMP_DIR/src" --strip-components=1

cp -R "$TMP_DIR/src/." "$APP_DIR/"
chmod +x "$APP_DIR"/scripts/*.sh 2>/dev/null || true

sh "$APP_DIR/scripts/install.sh"
