#!/usr/bin/env sh
set -eu

CONTAINER_NAME="${CONTAINER_NAME:-qbt-telegram-bot}"
IMAGE_NAME="${IMAGE_NAME:-qbt-telegram-bot:latest}"

echo "Stopping and removing container..."
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

printf "Remove Docker image %s? [y/N]: " "$IMAGE_NAME"
read -r answer || true
case "$(printf "%s" "${answer:-n}" | tr '[:upper:]' '[:lower:]')" in
  y|yes)
    docker rmi "$IMAGE_NAME" 2>/dev/null || true
    ;;
esac

echo "Uninstalled container. Configuration files were not deleted."
