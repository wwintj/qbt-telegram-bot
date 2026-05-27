#!/usr/bin/env sh
set -eu

REPO_TARBALL_URL="${REPO_TARBALL_URL:-https://github.com/wwintj/qbt-telegram-bot/archive/refs/heads/main.tar.gz}"
APP_DIR="${APP_DIR:-}"

if [ -z "$APP_DIR" ]; then
  if [ -d "/mnt/user/appdata" ]; then
    APP_DIR="/mnt/user/appdata/qbt-telegram-bot"
  else
    APP_DIR="$HOME/qbt-telegram-bot"
  fi
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker command not found. Please install Docker first."
  exit 1
fi

DOWNLOADER=""
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

mkdir -p "$APP_DIR"

if [ -f "$APP_DIR/.env" ]; then
  echo "Existing .env detected. It will be preserved."
fi

echo "Downloading qBittorrent Telegram Bot from GitHub..."
if [ "$DOWNLOADER" = "curl" ]; then
  curl -fsSL "$REPO_TARBALL_URL" -o "$TMP_DIR/source.tar.gz"
else
  wget -qO "$TMP_DIR/source.tar.gz" "$REPO_TARBALL_URL"
fi

echo "Extracting project..."
tar -xzf "$TMP_DIR/source.tar.gz" -C "$TMP_DIR"
SRC_DIR="$(find "$TMP_DIR" -maxdepth 1 -type d -name 'qbt-telegram-bot-*' | head -n 1)"

if [ -z "$SRC_DIR" ] || [ ! -d "$SRC_DIR" ]; then
  echo "ERROR: failed to locate extracted project directory."
  exit 1
fi

cp -R "$SRC_DIR/." "$APP_DIR/"
chmod +x "$APP_DIR"/scripts/*.sh 2>/dev/null || true

cd "$APP_DIR"

echo "Starting installer in: $APP_DIR"
sh scripts/install.sh
