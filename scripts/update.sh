#!/usr/bin/env sh
set -eu

APP_DIR="${APP_DIR:-$(pwd)}"
IMAGE_NAME="${IMAGE_NAME:-qbt-telegram-bot:latest}"
CONTAINER_NAME="${CONTAINER_NAME:-qbt-telegram-bot}"
LOCAL_TG_HOST_PATH="${LOCAL_TELEGRAM_FILE_HOST_PATH:-/mnt/user/appdata/telegram-bot-api}"
LOCAL_TG_CONTAINER_PATH="/var/lib/telegram-bot-api"

cd "$APP_DIR"

if [ -d ".git" ] && command -v git >/dev/null 2>&1; then
  echo "Pulling latest changes..."
  git pull
fi

USE_LOCAL_TG="false"
if grep -q '^USE_LOCAL_TELEGRAM_API=true' .env 2>/dev/null; then
  USE_LOCAL_TG="true"
fi

LOCAL_TG_MOUNT_ARGS=""
if [ "$USE_LOCAL_TG" = "true" ] && [ -d "$LOCAL_TG_HOST_PATH" ]; then
  LOCAL_TG_MOUNT_ARGS="-v $LOCAL_TG_HOST_PATH:$LOCAL_TG_CONTAINER_PATH:ro"
fi

echo "Rebuilding Docker image..."
docker build -t "$IMAGE_NAME" .

echo "Restarting container..."
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

mkdir -p "$APP_DIR/tmp"

# Intentional word splitting for optional LOCAL_TG_MOUNT_ARGS.
docker run -d \
  --name "$CONTAINER_NAME" \
  --restart unless-stopped \
  --network host \
  --env-file "$APP_DIR/.env" \
  -v "$APP_DIR/tmp:/tmp/telegram_qb" \
  $LOCAL_TG_MOUNT_ARGS \
  "$IMAGE_NAME"

echo "Updated."
