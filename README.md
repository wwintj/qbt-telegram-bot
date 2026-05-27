<p align="center">
  <img src="assets/icon.png" width="120" alt="qBittorrent Telegram Bot icon">
</p>

# qBittorrent Telegram Bot

A lightweight Telegram bot for controlling qBittorrent through Telegram.

## Features

- Add magnet links from Telegram
- Add `.torrent` files from Telegram
- Add HTTP/HTTPS `.torrent` links
- View qBittorrent status
- View torrent task list
- Test qBittorrent Web API connection
- Telegram bottom menu
- Telegram slash command menu
- Docker deployment
- qBittorrent v5.2.0 compatible login handling
- Official Telegram Bot API by default
- Optional local Telegram Bot API support

## Commands

```text
/status - View qBittorrent download status
/list   - View torrent task list
/test   - Test qBittorrent connection
/add    - Show how to add downloads
/id     - Show current Telegram chat ID
/help   - Show help
```

Bottom menu:

```text
📊 状态
📋 任务列表
```

## Quick Start

v0.2.1 includes a fixed Unraid-friendly configuration wizard. Token and password input are visible to avoid the terminal appearing frozen.

```bash
git clone https://github.com/wwintj/qbt-telegram-bot.git
cd qbt-telegram-bot

sh scripts/install.sh
```

The installer will ask for:

- Telegram Bot Token
- qBittorrent IP/domain
- qBittorrent WebUI port
- qBittorrent username
- qBittorrent password
- Optional admin chat ID
- Optional local Telegram Bot API settings

## Manual Docker Run

```bash
cp .env.example .env
nano .env

docker build -t qbt-telegram-bot:latest .

docker rm -f qbt-telegram-bot 2>/dev/null || true

docker run -d \
  --name qbt-telegram-bot \
  --restart unless-stopped \
  --network host \
  --env-file .env \
  -v $(pwd)/tmp:/tmp/telegram_qb \
  qbt-telegram-bot:latest
```

## Unraid

Recommended appdata path:

```bash
mkdir -p /mnt/user/appdata/qbt-telegram-bot
cd /mnt/user/appdata/qbt-telegram-bot
```

Then run:

```bash
sh scripts/install.sh
```

### Official Telegram Bot API

By default, the bot uses:

```env
TELEGRAM_API_BASE=https://api.telegram.org
USE_LOCAL_TELEGRAM_API=false
```

This is enough for most users. `.torrent` files are usually small, so the official Telegram Bot API is normally sufficient.

### Local Telegram Bot API

Advanced users can use a local Telegram Bot API server:

```env
TELEGRAM_API_BASE=http://192.168.8.198:8081
USE_LOCAL_TELEGRAM_API=true
LOCAL_TELEGRAM_FILE_ROOT=/var/lib/telegram-bot-api
```

If you use local Telegram Bot API, add the relevant volume mapping manually:

```bash
-v /mnt/user/appdata/telegram-bot-api:/var/lib/telegram-bot-api:ro
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `TELEGRAM_TOKEN` | required | Telegram Bot token from BotFather |
| `TELEGRAM_API_BASE` | `https://api.telegram.org` | Official or local Telegram Bot API endpoint |
| `ADMIN_CHAT_IDS` | empty | Allowed Telegram chat IDs, comma-separated |
| `QBT_URL` | `http://127.0.0.1:8080` | qBittorrent WebUI/API URL |
| `QBT_USERNAME` | `admin` | qBittorrent username |
| `QBT_PASSWORD` | `adminadmin` | qBittorrent password |
| `QBT_SAVE_PATH` | empty | Optional qBittorrent-side download path |
| `QBT_CATEGORY` | `telegram` | Category for new tasks |
| `QBT_TAGS` | `telegram` | Tags for new tasks |
| `ADD_STOPPED` | `false` | Add tasks stopped/paused |
| `USE_LOCAL_TELEGRAM_API` | `false` | Enable local Telegram Bot API mode |
| `LOCAL_TELEGRAM_FILE_ROOT` | `/var/lib/telegram-bot-api` | File root for local Telegram Bot API |

## Security

- Do not commit `.env`.
- Do not expose qBittorrent WebUI to the public internet.
- Do not expose local Telegram Bot API to the public internet.
- Set `ADMIN_CHAT_IDS` after the first `/id` test.

## Maintenance

View logs:

```bash
docker logs -f qbt-telegram-bot
```

Restart:

```bash
docker restart qbt-telegram-bot
```

Update:

```bash
sh scripts/update.sh
```

Uninstall:

```bash
sh scripts/uninstall.sh
```
