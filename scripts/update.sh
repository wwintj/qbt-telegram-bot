#!/usr/bin/env sh
set -eu

APP_DIR="${APP_DIR:-$(pwd)}"
REFRESH_URL="${REFRESH_URL:-https://raw.githubusercontent.com/wwintj/qbt-telegram-bot/main/scripts/refresh.sh}"
TMP_REFRESH="$(mktemp)"

cleanup() {
  rm -f "$TMP_REFRESH"
}
trap cleanup EXIT INT TERM

if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$REFRESH_URL" -o "$TMP_REFRESH"
elif command -v wget >/dev/null 2>&1; then
  wget -qO "$TMP_REFRESH" "$REFRESH_URL"
else
  echo "ERROR: curl or wget is required."
  exit 1
fi

chmod +x "$TMP_REFRESH" 2>/dev/null || true
APP_DIR="$APP_DIR" exec sh "$TMP_REFRESH"
