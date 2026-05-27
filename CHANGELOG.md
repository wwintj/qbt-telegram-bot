# Changelog

## v0.2.1

- Fixed `scripts/configure.sh` prompt display issue on Unraid terminals
- Changed configuration wizard token/password prompts to visible input for better compatibility
- Ensured shell prompts are printed to stderr so command substitution does not swallow prompt text
- Improved README notes for official Telegram Bot API and local Telegram Bot API modes

## v0.2.0

- Refactored into modular `app/` package
- Default Telegram API changed to official `https://api.telegram.org`
- Local Telegram Bot API is now optional advanced mode
- Added interactive configuration script
- Added install/update/uninstall scripts
- Added Unraid template
- Added project icon
- Improved Telegram message formatting
- Kept qBittorrent v5.2.0 HTTP 204 login compatibility
