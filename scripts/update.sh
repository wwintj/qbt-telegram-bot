#!/usr/bin/env sh
set -eu

APP_DIR="${APP_DIR:-$(pwd)}"
REFRESH_URL="${REFRESH_URL:-https://raw.githubusercontent.com/wwintj/qbt-telegram-bot/main/scripts/refresh.sh}"

cd "$APP_DIR"
mkdir -p scripts

if [ ! -f "scripts/refresh.sh" ]; then
  echo "scripts/refresh.sh not found. Downloading it from GitHub..."
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$REFRESH_URL" -o scripts/refresh.sh
  elif command -v wget >/dev/null 2>&1; then
    wget -qO scripts/refresh.sh "$REFRESH_URL"
  else
    echo "ERROR: curl or wget is required."
    exit 1
  fi
  chmod +x scripts/refresh.sh 2>/dev/null || true
fi

sh scripts/refresh.sh
