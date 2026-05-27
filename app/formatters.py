from __future__ import annotations


def fmt_size(num_bytes) -> str:
    try:
        size = float(num_bytes)
    except Exception:
        return "-"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024 or unit == "TB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.2f} {unit}"
        size /= 1024
    return "-"


def fmt_speed(num_bytes_per_sec) -> str:
    return f"{fmt_size(num_bytes_per_sec)}/s"


def fmt_eta(seconds) -> str:
    try:
        seconds = int(seconds)
    except Exception:
        return "-"
    if seconds <= 0 or seconds >= 8640000:
        return "-"
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m"
    if seconds < 86400:
        return f"{seconds // 3600}h {seconds % 3600 // 60}m"
    return f"{seconds // 86400}d {seconds % 86400 // 3600}h"


def state_label(state: str) -> str:
    return {
        "downloading": "下载中", "metaDL": "获取元数据", "stalledDL": "等待下载",
        "forcedDL": "强制下载", "checkingDL": "校验中", "queuedDL": "排队下载",
        "uploading": "做种中", "stalledUP": "等待做种", "forcedUP": "强制做种",
        "queuedUP": "排队做种", "stoppedDL": "已停止", "stoppedUP": "已停止",
        "pausedDL": "已暂停", "pausedUP": "已暂停", "error": "错误", "missingFiles": "文件缺失",
    }.get(state, state or "未知")


def progress_bar(progress) -> str:
    try:
        progress = max(0, min(float(progress), 1))
    except Exception:
        progress = 0
    filled = int(progress * 10)
    return "█" * filled + "░" * (10 - filled)


def short_name(name: str | None, length: int = 44) -> str:
    name = name or "Unknown"
    return name if len(name) <= length else name[: length - 1] + "…"


def panel(title: str, lines: list[str]) -> str:
    return "\n".join([title, "━━━━━━━━━━━━━━━━━━━━", *lines])


def help_text() -> str:
    return panel("🤖 qBittorrent Telegram 控制器", [
        "底部按钮：", "📊 状态：查看当前下载状态", "📋 任务列表：查看 qB 任务列表", "",
        "左侧 / 命令菜单：", "/status - 查看 qB 下载状态", "/list - 查看任务列表",
        "/test - 测试 qB 连接", "/add - 查看添加下载方法", "/id - 查看当前 chat_id", "/help - 显示帮助", "",
        "添加下载：", "直接发送 magnet 链接、.torrent 文件，或 .torrent 下载链接即可。",
    ])


def add_help_text(category: str, tags: str) -> str:
    return panel("🧲 添加下载任务", [
        "你可以直接发送以下内容：", "", "1. magnet 磁力链接", "2. .torrent 种子文件", "3. .torrent 下载链接", "",
        "收到后，我会自动提交到 qBittorrent。", "", f"当前分类：{category}", f"当前标签：{tags}",
    ])


def sort_torrents(torrents: list[dict]) -> list[dict]:
    active = ["downloading", "metaDL", "stalledDL", "forcedDL", "uploading", "stalledUP", "forcedUP"]
    return sorted(torrents, key=lambda t: (t.get("state", "") not in active, -float(t.get("dlspeed", 0) or 0), -float(t.get("upspeed", 0) or 0), t.get("name", "")))


def status_text(qbt_url: str, torrents: list[dict], transfer: dict) -> str:
    counts = {"down": 0, "seed": 0, "stop": 0, "err": 0}
    for t in torrents:
        s = t.get("state", "")
        if s in ["downloading", "metaDL", "stalledDL", "forcedDL", "checkingDL", "queuedDL"]: counts["down"] += 1
        elif s in ["uploading", "stalledUP", "forcedUP", "queuedUP"]: counts["seed"] += 1
        elif s in ["stoppedDL", "stoppedUP", "pausedDL", "pausedUP"]: counts["stop"] += 1
        elif s in ["error", "missingFiles"]: counts["err"] += 1
    lines = [f"🌐 地址：{qbt_url}", "", f"📦 总任务：{len(torrents)}", f"⬇️ 下载中：{counts['down']}", f"⬆️ 做种中：{counts['seed']}", f"⏸ 停止/暂停：{counts['stop']}", f"⚠️ 异常任务：{counts['err']}", "", f"🚀 下载速度：{fmt_speed(transfer.get('dl_info_speed', 0))}", f"📤 上传速度：{fmt_speed(transfer.get('up_info_speed', 0))}"]
    active = sort_torrents(torrents)[:5]
    if active:
        lines += ["", "🔥 当前优先显示任务", "━━━━━━━━━━━━━━━━━━━━"]
        for i, t in enumerate(active, 1):
            p = float(t.get("progress", 0) or 0)
            lines.append(f"{i}. {short_name(t.get('name'), 46)}\n   {progress_bar(p)} {p*100:.1f}%\n   状态：{state_label(t.get('state', ''))} | 速度：{fmt_speed(t.get('dlspeed', 0))} | ETA：{fmt_eta(t.get('eta', 0))}")
    return panel("📊 qBittorrent 状态面板", lines)


def list_text(torrents: list[dict], limit: int = 12) -> str:
    torrents = sort_torrents(torrents)
    if not torrents:
        return panel("📋 qBittorrent 任务列表", ["当前没有任何任务。"])
    lines = [f"显示：前 {min(limit, len(torrents))} 个 / 共 {len(torrents)} 个", ""]
    for i, t in enumerate(torrents[:limit], 1):
        p = float(t.get("progress", 0) or 0)
        ratio = float(t.get("ratio", 0) or 0)
        lines.append(f"{i}. {short_name(t.get('name'), 48)}\n   {progress_bar(p)} {p*100:.1f}%\n   大小：{fmt_size(t.get('size', 0))} | 状态：{state_label(t.get('state', ''))}\n   ↓ {fmt_speed(t.get('dlspeed', 0))} | ↑ {fmt_speed(t.get('upspeed', 0))} | Ratio：{ratio:.2f}")
    return panel("📋 qBittorrent 任务列表", lines)
