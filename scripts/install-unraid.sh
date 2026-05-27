#!/usr/bin/env sh
set -eu

APP_DIR="${APP_DIR:-/mnt/user/appdata/qbt-telegram-bot}"

mkdir -p "$APP_DIR"

if [ "$(pwd)" != "$APP_DIR" ]; then
  echo "Please run this script from the project directory or set APP_DIR."
  echo "Current directory: $(pwd)"
  echo "Expected directory: $APP_DIR"
fi

sh scripts/install.sh
