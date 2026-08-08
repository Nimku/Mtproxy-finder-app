"""
Local bot-side state: admin-editable settings (price/period/free mode) and the
list of known users (for language memory, /status and /admin broadcast/stats).

This is separate from license/status.json on GitHub, which is the
authoritative source the app reads. This file never leaves the VPS.
"""

import asyncio
import json
import os
from dataclasses import asdict, dataclass, field

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")
USERS_PATH = os.path.join(DATA_DIR, "users.json")

_lock = asyncio.Lock()


@dataclass
class Config:
    price_stars: int = 20
    subscription_days: int = 30
    free_mode: bool = False


def _load_json(path: str, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: str, obj) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
    os.replace(tmp_path, path)


async def load_config() -> Config:
    async with _lock:
        raw = _load_json(CONFIG_PATH, {})
        return Config(**{**asdict(Config()), **raw})


async def save_config(config: Config) -> None:
    async with _lock:
        _save_json(CONFIG_PATH, asdict(config))


async def load_users() -> dict:
    """chat_id (str) -> {"language": str}"""
    async with _lock:
        return _load_json(USERS_PATH, {})


async def upsert_user(chat_id: int, language: str | None = None) -> dict:
    async with _lock:
        users = _load_json(USERS_PATH, {})
        entry = users.get(str(chat_id), {})
        if language is not None:
            entry["language"] = language
        users[str(chat_id)] = entry
        _save_json(USERS_PATH, users)
        return entry


async def get_user_language(chat_id: int, default: str) -> str:
    users = await load_users()
    return users.get(str(chat_id), {}).get("language", default)
