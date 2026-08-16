"""Configuration, all of it from the environment.

Nothing secret is ever written in code here. Copy .env.example to .env, fill it
in, and keep .env off git — see README.md.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # dotenv is a convenience, not a requirement
    pass


def _int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    try:
        return int(raw) if raw else default
    except ValueError:
        return default


def _bool(name: str, default: bool) -> bool:
    raw = os.getenv(name, "").strip().lower()
    if not raw:
        return default
    return raw in ("1", "true", "yes", "on")


def _verify_mode() -> str:
    """Also understands the older VERIFY=true/false switch, so an existing .env
    keeps working: VERIFY=false means the same as VERIFY_MODE=off."""
    raw = os.getenv("VERIFY_MODE", "").strip().lower()
    if raw in ("protocol", "strict", "off"):
        return raw
    legacy = os.getenv("VERIFY", "").strip().lower()
    if legacy in ("0", "false", "no", "off"):
        return "off"
    return "protocol"


@dataclass(frozen=True)
class Config:
    bot_token: str
    admin_id: int

    # Telethon — only needed to read Telegram channels. Without these the bot
    # still works, it just scrapes the GitHub feeds and skips the channels.
    api_id: int
    api_hash: str
    phone: str
    session_name: str

    refresh_minutes: int
    proxies_per_channel: int
    channel_message_limit: int

    # "protocol" (default) — drop only proxies that answered and then failed the
    #                        MTProto protocol; keep ones we simply couldn't reach,
    #                        since that may be our route rather than the proxy.
    # "strict"             — publish only what passed from this server.
    # "off"                — publish everything scraped, no network test.
    verify_mode: str
    verify_workers: int
    connect_timeout: float
    response_timeout: float
    max_published: int

    output_dir: str
    publish_channel: str

    @property
    def has_telethon(self) -> bool:
        return bool(self.api_id and self.api_hash and self.phone)


def load() -> Config:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise SystemExit(
            "BOT_TOKEN is not set. Copy .env.example to .env and fill it in.\n"
            "Get a token from @BotFather in Telegram."
        )
    return Config(
        bot_token=token,
        admin_id=_int("ADMIN_ID", 0),
        api_id=_int("TG_API_ID", 0),
        api_hash=os.getenv("TG_API_HASH", "").strip(),
        phone=os.getenv("TG_PHONE", "").strip(),
        # Deliberately NOT the same session name as any other bot on the box.
        # Two processes sharing one Telethon session file corrupt it and can get
        # the account flagged for concurrent logins from the same session.
        session_name=os.getenv("TG_SESSION", "nimku_scraper_session").strip(),
        refresh_minutes=_int("REFRESH_MINUTES", 60),
        proxies_per_channel=_int("PROXIES_PER_CHANNEL", 30),
        channel_message_limit=_int("CHANNEL_MESSAGE_LIMIT", 120),
        verify_mode=_verify_mode(),
        verify_workers=_int("VERIFY_WORKERS", 60),
        connect_timeout=float(_int("CONNECT_TIMEOUT_MS", 2500)) / 1000.0,
        response_timeout=float(_int("RESPONSE_TIMEOUT_MS", 3500)) / 1000.0,
        max_published=_int("MAX_PUBLISHED", 2000),
        output_dir=os.getenv("OUTPUT_DIR", "data").strip() or "data",
        publish_channel=os.getenv("PUBLISH_CHANNEL", "").strip(),
    )
