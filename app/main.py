from __future__ import annotations

import time
import traceback

from app.config import load_config
from app.telegram_client import TelegramClient
from app.qbittorrent_client import QBittorrentClient
from app.handlers import MessageHandler


def main():
    config = load_config()

    telegram = TelegramClient(
        token=config.telegram_token,
        api_base=config.telegram_api_base,
        use_local_api=config.use_local_telegram_api,
        local_file_root=config.local_telegram_file_root,
    )

    qbittorrent = QBittorrentClient(
        url=config.qbt_url,
        username=config.qbt_username,
        password=config.qbt_password,
        save_path=config.qbt_save_path,
        category=config.qbt_category,
        tags=config.qbt_tags,
        add_stopped=config.add_stopped,
    )

    handler = MessageHandler(config, telegram, qbittorrent)

    print("====================================", flush=True)
    print("qB Telegram Bot started", flush=True)
    print(f"Telegram API: {config.telegram_api_base}", flush=True)
    print(f"qB URL: {config.qbt_url}", flush=True)
    print("====================================", flush=True)

    try:
        telegram.setup_commands()
    except Exception:
        print("Failed to set Telegram command menu. Bot will continue.", flush=True)
        traceback.print_exc()

    offset = None

    while True:
        try:
            updates = telegram.get_updates(offset=offset, timeout=50)

            for update in updates:
                offset = update["update_id"] + 1
                msg = update.get("message")
                if msg:
                    handler.handle(msg)

        except KeyboardInterrupt:
            print("Bot stopped.", flush=True)
            break

        except Exception:
            print("Main loop error:", flush=True)
            traceback.print_exc()
            time.sleep(5)


if __name__ == "__main__":
    main()
