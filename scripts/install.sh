#!/usr/bin/env sh
set -eu

APP_DIR="${APP_DIR:-$(pwd)}"
IMAGE_NAME="${IMAGE_NAME:-qbt-telegram-bot:latest}"
CONTAINER_NAME="${CONTAINER_NAME:-qbt-telegram-bot}"
LOCAL_TG_HOST_PATH="${LOCAL_TELEGRAM_FILE_HOST_PATH:-/mnt/user/appdata/telegram-bot-api}"
LOCAL_TG_CONTAINER_PATH="/var/lib/telegram-bot-api"

cd "$APP_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker command not found."
  exit 1
fi

if [ ! -f ".env" ]; then
  echo ".env not found. Starting configuration wizard..."
  sh scripts/configure.sh
fi

USE_LOCAL_TG="false"
if grep -q '^USE_LOCAL_TELEGRAM_API=true' .env 2>/dev/null; then
  USE_LOCAL_TG="true"
fi

LOCAL_TG_MOUNT_ARGS=""
if [ "$USE_LOCAL_TG" = "true" ]; then
  if [ -d "$LOCAL_TG_HOST_PATH" ]; then
    LOCAL_TG_MOUNT_ARGS="-v $LOCAL_TG_HOST_PATH:$LOCAL_TG_CONTAINER_PATH:ro"
    echo "Local Telegram Bot API enabled. Mounting: $LOCAL_TG_HOST_PATH -> $LOCAL_TG_CONTAINER_PATH"
  else
    echo "WARNING: USE_LOCAL_TELEGRAM_API=true but host path does not exist: $LOCAL_TG_HOST_PATH"
    echo "Torrent files may fail unless you mount the local Telegram Bot API data directory."
  fi
fi

echo "Building Docker image..."
docker build -t "$IMAGE_NAME" .

echo "Removing old container if it exists..."
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

mkdir -p "$APP_DIR/tmp"

echo "Starting container..."
# Intentional word splitting for optional LOCAL_TG_MOUNT_ARGS.
docker run -d \
  --name "$CONTAINER_NAME" \
  --restart unless-stopped \
  --network host \
  --env-file "$APP_DIR/.env" \
  -v "$APP_DIR/tmp:/tmp/telegram_qb" \
  $LOCAL_TG_MOUNT_ARGS \
  "$IMAGE_NAME"

echo
echo "Installed and started."
echo
echo "Useful commands:"
echo "  docker logs -f $CONTAINER_NAME"
echo "  docker restart $CONTAINER_NAME"
echo
echo "Next steps:"
echo "  1. Send /id to your Telegram bot."
echo "  2. Put that chat ID into ADMIN_CHAT_IDS in .env."
echo "  3. Restart: docker restart $CONTAINER_NAME"
echo "  4. Send /test to verify qBittorrent connection."
