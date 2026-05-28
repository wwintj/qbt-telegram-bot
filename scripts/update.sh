#!/usr/bin/env sh
set -eu

APP_DIR="${APP_DIR:-$(pwd)}"
cd "$APP_DIR"

if [ -f "scripts/refresh.sh" ]; then
  sh scripts/refresh.sh
else
  echo "ERROR: scripts/refresh.sh not found."
  exit 1
fi
