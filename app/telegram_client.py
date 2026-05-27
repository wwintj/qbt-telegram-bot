from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from urllib.parse import quote

import requests


class TelegramClient:
    def __init__(
        self,
        token: str,
        api_base: str,
        use_local_api: bool = False,
        local_file_root: str = "/var/lib/telegram-bot-api",
    ):
        self.token = token
        self.api_base = api_base.rstrip("/")
        self.use_local_api = use_local_api
        self.local_file_root = local_file_root.rstrip("/")
        self.api_url = f"{self.api_base}/bot{self.token}"
        self.file_url = f"{self.api_base}/file/bot{self.token}"

    def call(self, method: str, data: dict | None = None, timeout: int = 60):
        response = requests.post(f"{self.api_url}/{method}", data=data or {}, timeout=timeout)
        response.raise_for_status()
        payload = response.json()

        if not payload.get("ok"):
            raise RuntimeError(payload)

        return payload.get("result")

    def send_message(self, chat_id, text: str, show_menu: bool = True):
        payload = {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": "true",
        }

        if show_menu:
            payload["reply_markup"] = self.bottom_menu()

        self.call("sendMessage", payload, timeout=20)

    def bottom_menu(self) -> str:
        return json.dumps(
            {
                "keyboard": [
                    [
                        {"text": "📊 状态"},
                        {"text": "📋 任务列表"},
                    ]
                ],
                "resize_keyboard": True,
                "is_persistent": True,
                "one_time_keyboard": False,
                "input_field_placeholder": "发送 magnet 链接或 .torrent 文件",
            },
            ensure_ascii=False,
        )

    def setup_commands(self):
        commands = [
            {"command": "status", "description": "查看 qB 下载状态"},
            {"command": "list", "description": "查看任务列表"},
            {"command": "test", "description": "测试 qB 连接"},
            {"command": "add", "description": "查看如何添加下载"},
            {"command": "id", "description": "查看当前 chat_id"},
            {"command": "help", "description": "显示帮助"},
        ]

        self.call(
            "setMyCommands",
            {"commands": json.dumps(commands, ensure_ascii=False)},
            timeout=20,
        )

    def get_updates(self, offset=None, timeout=50):
        data = {
            "timeout": timeout,
            "allowed_updates": '["message"]',
        }

        if offset is not None:
            data["offset"] = offset

        return self.call("getUpdates", data=data, timeout=timeout + 20)

    def get_file(self, file_id: str) -> dict:
        return self.call("getFile", {"file_id": file_id}, timeout=60)

    def resolve_file_path(self, file_id: str, original_name: str) -> str:
        file_info = self.get_file(file_id)
        file_path = file_info.get("file_path")

        if not file_path:
            raise RuntimeError("Telegram getFile did not return file_path")

        print(f"Telegram file_path: {file_path}", flush=True)

        # Local Telegram Bot API may return an absolute local filesystem path.
        if self.use_local_api and os.path.isabs(file_path):
            candidates = [file_path]

            if file_path.startswith("/data/"):
                candidates.append(file_path.replace("/data", self.local_file_root, 1))

            if self.local_file_root and not file_path.startswith(self.local_file_root):
                candidates.append(f"{self.local_file_root}/{file_path.lstrip('/')}")

            for candidate in candidates:
                if os.path.exists(candidate):
                    return candidate

        # Official Telegram Bot API path, or fallback for local API.
        tmp_dir = Path(tempfile.gettempdir()) / "telegram_qb"
        tmp_dir.mkdir(parents=True, exist_ok=True)

        safe_name = original_name or Path(file_path).name or "download.torrent"
        local_path = tmp_dir / safe_name

        download_url = f"{self.file_url}/{quote(file_path, safe='/')}"
        print(f"Downloading Telegram file: {download_url}", flush=True)

        with requests.get(download_url, stream=True, timeout=300) as response:
            response.raise_for_status()
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)

        return str(local_path)
