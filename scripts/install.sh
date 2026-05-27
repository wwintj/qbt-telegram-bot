#!/usr/bin/env sh
set -eu

APP_DIR="${APP_DIR:-$(pwd)}"
IMAGE_NAME="${IMAGE_NAME:-qbt-telegram-bot:latest}"
CONTAINER_NAME="${CONTAINER_NAME:-qbt-telegram-bot}"

cd "$APP_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker command not found."
  exit 1
fi

if [ ! -f ".env" ]; then
  echo ".env not found. Starting configuration wizard..."
  sh scripts/configure.sh
fi

echo "Building Docker image..."
docker build -t "$IMAGE_NAME" .

echo "Removing old container if it exists..."
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

mkdir -p "$APP_DIR/tmp"

echo "Starting container..."
docker run -d \
  --name "$CONTAINER_NAME" \
  --restart unless-stopped \
  --network host \
  --env-file "$APP_DIR/.env" \
  -v "$APP_DIR/tmp:/tmp/telegram_qb" \
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
