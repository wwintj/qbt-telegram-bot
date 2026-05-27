from __future__ import annotations

import traceback

from app import formatters as fmt


def is_admin(chat_id, admin_chat_ids: set[str]) -> bool:
    if not admin_chat_ids:
        return True
    return str(chat_id) in admin_chat_ids


def extract_links(text: str) -> list[str]:
    links = []
    for line in (text or "").replace("\r", "\n").split("\n"):
        item = line.strip()
        if not item:
            continue
        if item.startswith("magnet:"):
            links.append(item)
        elif item.startswith("http://") or item.startswith("https://"):
            links.append(item)
    return links


class MessageHandler:
    def __init__(self, config, telegram, qbittorrent):
        self.config = config
        self.telegram = telegram
        self.qbt = qbittorrent

    def send(self, chat_id, text: str):
        try:
            self.telegram.send_message(chat_id, text)
        except Exception:
            print("Failed to send Telegram message:", flush=True)
            traceback.print_exc()

    def handle(self, msg: dict):
        chat_id = msg.get("chat", {}).get("id")
        if chat_id is None:
            return

        if not is_admin(chat_id, self.config.admin_chat_ids):
            self.send(chat_id, fmt.panel("⛔ 访问被拒绝", ["你不在授权列表中，无法控制 qBittorrent。"]))
            return

        text = (msg.get("text") or msg.get("caption") or "").strip()
        text = {"📊 状态": "/status", "📋 任务列表": "/list", "菜单": "/help", "/menu": "/help"}.get(text, text)

        if text.startswith("/start") or text.startswith("/help"):
            self.send(chat_id, fmt.help_text())
            return
        if text.startswith("/add"):
            self.send(chat_id, fmt.add_help_text(self.config.qbt_category, self.config.qbt_tags))
            return
        if text.startswith("/id"):
            self.send(chat_id, fmt.panel("🆔 Telegram Chat ID", [str(chat_id)]))
            return
        if text.startswith("/test"):
            self.handle_test(chat_id)
            return
        if text.startswith("/status"):
            self.handle_status(chat_id)
            return
        if text.startswith("/list"):
            self.handle_list(chat_id)
            return

        links = extract_links(text)
        if links:
            self.handle_links(chat_id, links)
            return

        doc = msg.get("document")
        if doc:
            self.handle_document(chat_id, doc)
            return

        self.send(chat_id, fmt.panel("🤔 未识别的内容", ["你可以发送：", "1. magnet 链接", "2. .torrent 文件", "3. .torrent 下载链接", "", "也可以点击底部按钮查看状态或任务列表。"]))

    def handle_test(self, chat_id):
        try:
            version = self.qbt.version()
            self.send(chat_id, fmt.panel("✅ qBittorrent 连接正常", [f"🌐 地址：{self.config.qbt_url}", f"👤 用户：{self.config.qbt_username}", f"🧩 版本：{version}", "📡 状态：Web API 可用"]))
        except Exception as e:
            self.send(chat_id, fmt.panel("❌ qBittorrent 连接失败", [f"错误信息：{e}"]))

    def handle_status(self, chat_id):
        try:
            self.send(chat_id, fmt.status_text(self.config.qbt_url, self.qbt.torrents(), self.qbt.transfer_info()))
        except Exception as e:
            self.send(chat_id, fmt.panel("❌ 获取状态失败", [f"错误信息：{e}"]))

    def handle_list(self, chat_id):
        try:
            self.send(chat_id, fmt.list_text(self.qbt.torrents()))
        except Exception as e:
            self.send(chat_id, fmt.panel("❌ 获取任务列表失败", [f"错误信息：{e}"]))

    def handle_links(self, chat_id, links: list[str]):
        ok_count = 0
        errors = []
        for link in links:
            try:
                self.qbt.add_url(link)
                ok_count += 1
            except Exception as e:
                errors.append(f"{fmt.short_name(link, 80)}\n错误：{e}")

        if ok_count and not errors:
            self.send(chat_id, fmt.panel("✅ 下载任务已提交", [f"成功添加：{ok_count} 个任务", f"分类：{self.config.qbt_category}", f"标签：{self.config.qbt_tags}", "", "你可以点击底部「📊 状态」查看进度。"] ))
        elif ok_count:
            self.send(chat_id, fmt.panel("⚠️ 下载任务部分提交成功", [f"成功：{ok_count}", f"失败：{len(errors)}", "", *errors[:3]]))
        else:
            self.send(chat_id, fmt.panel("❌ 下载任务提交失败", errors[:3] or ["未知错误"]))

    def handle_document(self, chat_id, doc: dict):
        file_name = doc.get("file_name", "download.torrent")
        mime_type = doc.get("mime_type", "")
        file_size = int(doc.get("file_size", 0) or 0)

        if not file_name.lower().endswith(".torrent") and mime_type != "application/x-bittorrent":
            self.send(chat_id, fmt.panel("⚠️ 文件类型不支持", [f"文件名：{file_name}", f"类型：{mime_type}", "", "当前只处理 .torrent 种子文件。"] ))
            return

        try:
            self.send(chat_id, fmt.panel("📥 已收到种子文件", [f"文件名：{file_name}", f"大小：{fmt.fmt_size(file_size)}", "", "正在提交到 qBittorrent..."]))
            local_file = self.telegram.resolve_file_path(doc["file_id"], file_name)
            self.qbt.add_torrent_file(local_file)
            self.send(chat_id, fmt.panel("✅ 种子任务已提交", [f"文件名：{file_name}", f"分类：{self.config.qbt_category}", f"标签：{self.config.qbt_tags}", "", "你可以点击底部「📊 状态」查看进度。"] ))
        except Exception as e:
            self.send(chat_id, fmt.panel("❌ 种子任务提交失败", [f"文件名：{file_name}", f"错误信息：{e}"]))
