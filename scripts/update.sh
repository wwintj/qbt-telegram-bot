#!/usr/bin/env sh
set -eu

APP_DIR="${APP_DIR:-$(pwd)}"
IMAGE_NAME="${IMAGE_NAME:-qbt-telegram-bot:latest}"
CONTAINER_NAME="${CONTAINER_NAME:-qbt-telegram-bot}"

cd "$APP_DIR"

if [ -d ".git" ] && command -v git >/dev/null 2>&1; then
  echo "Pulling latest changes..."
  git pull
fi

echo "Rebuilding Docker image..."
docker build -t "$IMAGE_NAME" .

echo "Restarting container..."
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

mkdir -p "$APP_DIR/tmp"

docker run -d \
  --name "$CONTAINER_NAME" \
  --restart unless-stopped \
  --network host \
  --env-file "$APP_DIR/.env" \
  -v "$APP_DIR/tmp:/tmp/telegram_qb" \
  "$IMAGE_NAME"

echo "Updated."
