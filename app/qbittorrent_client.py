from __future__ import annotations

from pathlib import Path

import requests


class QBittorrentClient:
    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        save_path: str = "",
        category: str = "telegram",
        tags: str = "telegram",
        add_stopped: bool = False,
    ):
        self.url = url.rstrip("/")
        self.username = username
        self.password = password
        self.save_path = save_path
        self.category = category
        self.tags = tags
        self.add_stopped = add_stopped

    def session(self) -> requests.Session:
        if not self.url:
            raise RuntimeError("QBT_URL is required")

        session = requests.Session()
        response = session.post(
            f"{self.url}/api/v2/auth/login",
            data={
                "username": self.username,
                "password": self.password,
            },
            headers={
                "Referer": self.url,
                "Origin": self.url,
            },
            timeout=20,
        )

        # qBittorrent 5.2.0 may return HTTP 204 No Content for successful empty responses.
        if response.status_code == 204:
            return session

        if response.status_code == 200 and "Ok." in response.text:
            return session

        raise RuntimeError(
            f"qB login failed: HTTP {response.status_code}, response: {response.text[:300]}"
        )

    def version(self) -> str:
        session = self.session()
        response = session.get(
            f"{self.url}/api/v2/app/version",
            headers={"Referer": self.url},
            timeout=15,
        )
        response.raise_for_status()
        return response.text.strip()

    def _add_common_fields(self) -> dict:
        data = {
            "category": self.category,
            "tags": self.tags,
        }

        if self.save_path:
            data["savepath"] = self.save_path

        if self.add_stopped:
            data["stopped"] = "true"
            data["paused"] = "true"

        return data

    def add_url(self, url_text: str):
        session = self.session()
        data = self._add_common_fields()
        data["urls"] = url_text

        response = session.post(
            f"{self.url}/api/v2/torrents/add",
            data=data,
            headers={
                "Referer": self.url,
                "Origin": self.url,
            },
            timeout=60,
        )

        if response.status_code not in (200, 204):
            raise RuntimeError(
                f"Add URL failed: HTTP {response.status_code}, response: {response.text[:300]}"
            )

        if "Fails." in response.text:
            raise RuntimeError(f"Add URL failed: {response.text}")

    def add_torrent_file(self, file_path: str):
        session = self.session()
        path = Path(file_path)

        if not path.exists():
            raise RuntimeError(f"Torrent file does not exist: {path}")

        data = self._add_common_fields()

        with open(path, "rb") as f:
            files = {
                "torrents": (
                    path.name,
                    f,
                    "application/x-bittorrent",
                )
            }

            response = session.post(
                f"{self.url}/api/v2/torrents/add",
                data=data,
                files=files,
                headers={
                    "Referer": self.url,
                    "Origin": self.url,
                },
                timeout=120,
            )

        if response.status_code not in (200, 204):
            raise RuntimeError(
                f"Add torrent failed: HTTP {response.status_code}, response: {response.text[:300]}"
            )

        if "Fails." in response.text:
            raise RuntimeError(f"Add torrent failed: {response.text}")

    def torrents(self) -> list[dict]:
        session = self.session()
        response = session.get(
            f"{self.url}/api/v2/torrents/info",
            headers={"Referer": self.url},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def transfer_info(self) -> dict:
        session = self.session()
        response = session.get(
            f"{self.url}/api/v2/transfer/info",
            headers={"Referer": self.url},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()
