import os
from dataclasses import dataclass


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Config:
    telegram_token: str
    telegram_api_base: str
    admin_chat_ids: set[str]

    qbt_url: str
    qbt_username: str
    qbt_password: str
    qbt_save_path: str
    qbt_category: str
    qbt_tags: str
    add_stopped: bool

    use_local_telegram_api: bool
    local_telegram_file_root: str


def load_config() -> Config:
    token = _env("TELEGRAM_TOKEN")
    if not token or token == "your_telegram_bot_token":
        raise RuntimeError("TELEGRAM_TOKEN is required. Please set it in .env")

    admin_ids = {
        item.strip()
        for item in _env("ADMIN_CHAT_IDS").split(",")
        if item.strip()
    }

    qbt_url = _env("QBT_URL")
    if not qbt_url:
        scheme = _env("QBT_SCHEME", "http")
        host = _env("QBT_HOST", "127.0.0.1")
        port = _env("QBT_PORT", "8080")
        qbt_url = f"{scheme}://{host}:{port}"

    return Config(
        telegram_token=token,
        telegram_api_base=_env("TELEGRAM_API_BASE", "https://api.telegram.org").rstrip("/"),
        admin_chat_ids=admin_ids,

        qbt_url=qbt_url.rstrip("/"),
        qbt_username=_env("QBT_USERNAME"),
        qbt_password=_env("QBT_PASSWORD"),
        qbt_save_path=_env("QBT_SAVE_PATH"),
        qbt_category=_env("QBT_CATEGORY", "telegram"),
        qbt_tags=_env("QBT_TAGS", "telegram"),
        add_stopped=_bool_env("ADD_STOPPED", False),

        use_local_telegram_api=_bool_env("USE_LOCAL_TELEGRAM_API", False),
        local_telegram_file_root=_env("LOCAL_TELEGRAM_FILE_ROOT", "/var/lib/telegram-bot-api"),
    )
