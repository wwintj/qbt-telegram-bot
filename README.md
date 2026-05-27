<p align="center">
  <img src="assets/icon.svg" width="120" alt="qBittorrent Telegram Bot icon">
</p>

# qBittorrent Telegram Bot

> 一个通过 Telegram 控制 qBittorrent 的轻量级 Docker Bot，适合 Unraid、NAS、VPS 和家庭内网环境。

---

## 中文说明

### 项目简介

`qbt-telegram-bot` 可以让你直接在 Telegram 里控制 qBittorrent：发送 magnet 链接、`.torrent` 种子文件或 `.torrent` 下载链接，Bot 会自动提交到 qBittorrent 开始下载。

它默认使用 Telegram 官方 Bot API，同时也支持高级用户使用本地部署的 Telegram Bot API。对于 Unraid 用户，如果启用本地 Telegram Bot API，安装脚本会自动尝试挂载本地文件目录，方便直接处理 `.torrent` 文件。

### 功能特性

- 发送 magnet 链接自动添加下载
- 发送 `.torrent` 文件自动添加下载
- 发送 HTTP/HTTPS `.torrent` 下载链接自动添加下载
- 查看 qBittorrent 当前下载状态
- 查看 qBittorrent 任务列表
- 测试 qBittorrent Web API 连接
- Telegram 底部常驻菜单
- Telegram 左侧 `/` 命令菜单
- Docker 部署
- 默认使用 Telegram 官方 Bot API
- 可选支持本地 Telegram Bot API
- 兼容 qBittorrent v5.2.0 的 HTTP 204 登录响应

### Telegram 命令

```text
/status - 查看 qBittorrent 下载状态
/list   - 查看任务列表
/test   - 测试 qBittorrent 连接
/add    - 查看如何添加下载任务
/id     - 查看当前 Telegram chat_id
/help   - 显示帮助
```

底部常驻菜单：

```text
📊 状态
📋 任务列表
```

### 一键安装

推荐用“两步法”，不要直接使用 `curl | sh`，这样在 Unraid 终端里交互输入更稳定。

```bash
cd /tmp
curl -fsSL https://raw.githubusercontent.com/wwintj/qbt-telegram-bot/main/scripts/bootstrap.sh -o qbt-install.sh
APP_DIR=/mnt/user/appdata/qbt-telegram-bot sh qbt-install.sh
```

如果没有 `curl`，可以用 `wget`：

```bash
cd /tmp
wget -qO qbt-install.sh https://raw.githubusercontent.com/wwintj/qbt-telegram-bot/main/scripts/bootstrap.sh
APP_DIR=/mnt/user/appdata/qbt-telegram-bot sh qbt-install.sh
```

安装脚本会提示你输入：

- Telegram Bot Token
- 允许控制 Bot 的 Telegram Chat ID，可先留空
- 是否使用本地 Telegram Bot API
- qBittorrent 协议，http 或 https
- qBittorrent IP 或域名
- qBittorrent WebUI 端口
- qBittorrent 用户名
- qBittorrent 密码
- 下载路径，可留空
- 分类和标签
- 是否添加任务后先暂停

### Git clone 安装

```bash
git clone https://github.com/wwintj/qbt-telegram-bot.git
cd qbt-telegram-bot
sh scripts/install.sh
```

### 手动 Docker 安装

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

如果你使用本地 Telegram Bot API，并且它的数据目录在 Unraid 上是 `/mnt/user/appdata/telegram-bot-api`，需要额外挂载：

```bash
-v /mnt/user/appdata/telegram-bot-api:/var/lib/telegram-bot-api:ro
```

当前 `scripts/install.sh` 会在检测到 `USE_LOCAL_TELEGRAM_API=true` 时，自动尝试添加这个挂载。

### Unraid 使用建议

推荐安装目录：

```bash
/mnt/user/appdata/qbt-telegram-bot
```

如果你想重新配置：

```bash
cd /mnt/user/appdata/qbt-telegram-bot
sh scripts/configure.sh
docker restart qbt-telegram-bot
```

如果你想更新：

```bash
cd /mnt/user/appdata/qbt-telegram-bot
sh scripts/update.sh
```

如果你想卸载：

```bash
cd /mnt/user/appdata/qbt-telegram-bot
sh scripts/uninstall.sh
```

### 官方 Telegram Bot API 模式

默认配置：

```env
TELEGRAM_API_BASE=https://api.telegram.org
USE_LOCAL_TELEGRAM_API=false
```

这个模式适合大多数用户，不需要额外部署 Telegram Bot API。普通 `.torrent` 文件一般很小，官方 API 通常够用。

### 本地 Telegram Bot API 模式

高级用户可以使用本地 Telegram Bot API，例如：

```env
TELEGRAM_API_BASE=http://192.168.8.198:8081
USE_LOCAL_TELEGRAM_API=true
LOCAL_TELEGRAM_FILE_ROOT=/var/lib/telegram-bot-api
```

如果使用本地 Telegram Bot API，qbt-telegram-bot 容器必须能读取 Telegram Bot API 的文件目录。Unraid 常见挂载如下：

```bash
-v /mnt/user/appdata/telegram-bot-api:/var/lib/telegram-bot-api:ro
```

### 环境变量说明

| 变量 | 默认值 | 说明 |
|---|---|---|
| `TELEGRAM_TOKEN` | 必填 | BotFather 创建的 Telegram Bot Token |
| `TELEGRAM_API_BASE` | `https://api.telegram.org` | Telegram 官方 API 或本地 Bot API 地址 |
| `ADMIN_CHAT_IDS` | 空 | 允许控制 Bot 的 Telegram chat_id，多个用英文逗号分隔 |
| `QBT_URL` | `http://127.0.0.1:8080` | qBittorrent WebUI/API 地址 |
| `QBT_USERNAME` | `admin` | qBittorrent 用户名 |
| `QBT_PASSWORD` | `adminadmin` | qBittorrent 密码 |
| `QBT_SAVE_PATH` | 空 | 可选，qBittorrent 内部下载路径 |
| `QBT_CATEGORY` | `telegram` | 新任务分类 |
| `QBT_TAGS` | `telegram` | 新任务标签 |
| `ADD_STOPPED` | `false` | 是否添加任务后先暂停/停止 |
| `USE_LOCAL_TELEGRAM_API` | `false` | 是否启用本地 Telegram Bot API 模式 |
| `LOCAL_TELEGRAM_FILE_ROOT` | `/var/lib/telegram-bot-api` | 容器内本地 Telegram Bot API 文件根目录 |

### 安全建议

- 不要把 `.env` 上传到 GitHub
- 不要公开 Telegram Bot Token
- 不要公开 qBittorrent WebUI 密码
- 不建议把 qBittorrent WebUI 暴露到公网
- 不建议把本地 Telegram Bot API 暴露到公网
- 首次运行后，发送 `/id` 获取自己的 chat_id，然后写入 `ADMIN_CHAT_IDS`

---

## English Documentation

### Overview

`qbt-telegram-bot` is a lightweight Docker-based Telegram bot for controlling qBittorrent. You can send magnet links, `.torrent` files, or HTTP/HTTPS `.torrent` URLs to Telegram, and the bot will submit them to qBittorrent automatically.

The bot uses the official Telegram Bot API by default. Advanced users can optionally use a local Telegram Bot API server, which is useful for Unraid, NAS, and LAN setups.

### Features

- Add magnet links from Telegram
- Add `.torrent` files from Telegram
- Add HTTP/HTTPS `.torrent` links
- View qBittorrent status
- View torrent task list
- Test qBittorrent Web API connection
- Telegram bottom menu
- Telegram slash command menu
- Docker deployment
- qBittorrent v5.2.0 HTTP 204 login compatibility
- Official Telegram Bot API by default
- Optional local Telegram Bot API support

### Commands

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
📊 Status
📋 Task List
```

### One-line style installation

Use the two-step method below instead of piping directly into `sh`, because it works better with interactive prompts on Unraid terminals.

```bash
cd /tmp
curl -fsSL https://raw.githubusercontent.com/wwintj/qbt-telegram-bot/main/scripts/bootstrap.sh -o qbt-install.sh
APP_DIR=/mnt/user/appdata/qbt-telegram-bot sh qbt-install.sh
```

With `wget`:

```bash
cd /tmp
wget -qO qbt-install.sh https://raw.githubusercontent.com/wwintj/qbt-telegram-bot/main/scripts/bootstrap.sh
APP_DIR=/mnt/user/appdata/qbt-telegram-bot sh qbt-install.sh
```

### Git clone installation

```bash
git clone https://github.com/wwintj/qbt-telegram-bot.git
cd qbt-telegram-bot
sh scripts/install.sh
```

### Manual Docker installation

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

For local Telegram Bot API users, add this mount when needed:

```bash
-v /mnt/user/appdata/telegram-bot-api:/var/lib/telegram-bot-api:ro
```

### Environment Variables

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

### Security

- Do not commit `.env`
- Do not expose your Telegram Bot Token
- Do not expose your qBittorrent password
- Do not expose qBittorrent WebUI to the public internet
- Do not expose local Telegram Bot API to the public internet
- Set `ADMIN_CHAT_IDS` after the first `/id` test
