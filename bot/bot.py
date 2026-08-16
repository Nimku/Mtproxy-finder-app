"""Nimku Proxy list bot.

Rebuilds a verified proxy list on a schedule and hands it out as a file, so the
app keeps working for people whose network can't reach GitHub. Telegram is
usually the last thing still reachable, which is exactly why the list travels
through it.

Talks to the Bot API directly over aiohttp rather than through a framework. That
is deliberate: the only heavyweight dependency a framework brought in was
pydantic, which has no wheel for current Python versions and tries (and fails)
to compile itself. Long-polling and a couple of JSON calls are all this needs.

Run:  python bot.py            (config comes from .env — see .env.example)
Test: python -m mtproto        (proves the proxy checker works on this host)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timezone

import aiohttp

import config
import i18n
import scraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("bot")

cfg = config.load()
API = f"https://api.telegram.org/bot{cfg.bot_token}"
USERS_FILE = os.path.join(cfg.output_dir, "users.json")

# The currently published list. Replaced wholesale by each refresh, so someone
# downloading mid-rebuild gets a complete older file rather than a half-written
# new one.
state: dict = {"path": None, "count": 0, "built_at": None, "confirmed": 0}


# ─────────────────────────────────────────────────────────────
#  Telegram Bot API
# ─────────────────────────────────────────────────────────────

async def api_call(session: aiohttp.ClientSession, method: str, payload: dict,
                   timeout: int = 20) -> dict:
    try:
        async with session.post(f"{API}/{method}", json=payload,
                                timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
            return await resp.json()
    except Exception as exc:  # noqa: BLE001 — a failed call must never kill the loop
        log.warning("%s failed: %s", method, exc)
        return {}


async def send_message(session, chat_id, text, keyboard=None) -> dict:
    payload = {
        "chat_id": chat_id, "text": text, "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    if keyboard is not None:
        payload["reply_markup"] = keyboard
    return await api_call(session, "sendMessage", payload)


async def send_document(session, chat_id, path, filename, caption, keyboard=None) -> dict:
    """Multipart upload — the only call here that isn't plain JSON."""
    form = aiohttp.FormData()
    form.add_field("chat_id", str(chat_id))
    form.add_field("caption", caption)
    form.add_field("parse_mode", "HTML")
    if keyboard is not None:
        form.add_field("reply_markup", json.dumps(keyboard))
    with open(path, "rb") as handle:
        form.add_field("document", handle.read(), filename=filename,
                       content_type="text/plain")
    try:
        async with session.post(f"{API}/sendDocument", data=form,
                                timeout=aiohttp.ClientTimeout(total=120)) as resp:
            return await resp.json()
    except Exception as exc:  # noqa: BLE001
        log.warning("sendDocument failed: %s", exc)
        return {}


async def answer_callback(session, callback_id: str, text: str = "", alert: bool = False):
    await api_call(session, "answerCallbackQuery", {
        "callback_query_id": callback_id, "text": text, "show_alert": alert,
    })


# ─────────────────────────────────────────────────────────────
#  Language preference
# ─────────────────────────────────────────────────────────────

def _load_users() -> dict:
    try:
        with open(USERS_FILE, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}


users: dict = _load_users()


def _save_users() -> None:
    os.makedirs(cfg.output_dir, exist_ok=True)
    tmp = USERS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(users, handle)
    os.replace(tmp, USERS_FILE)


def lang_of(user_id: int) -> str:
    return users.get(str(user_id), {}).get("lang", i18n.DEFAULT_LANGUAGE)


def set_lang(user_id: int, lang: str) -> None:
    users.setdefault(str(user_id), {})["lang"] = lang
    _save_users()


# ─────────────────────────────────────────────────────────────
#  Keyboards
# ─────────────────────────────────────────────────────────────

def menu_kb(lang: str) -> dict:
    return {"inline_keyboard": [
        [{"text": i18n.t(lang, "menu_get"), "callback_data": "get"}],
        [{"text": i18n.t(lang, "menu_app"), "callback_data": "app"}],
        [{"text": i18n.t(lang, "menu_help"), "callback_data": "help"}],
        [{"text": i18n.t(lang, "menu_language"), "callback_data": "lang"}],
    ]}


def language_kb() -> dict:
    return {"inline_keyboard": [
        [{"text": label, "callback_data": f"setlang:{code}"}]
        for code, label in i18n.LANGUAGES.items()
    ]}


# ─────────────────────────────────────────────────────────────
#  Handlers
# ─────────────────────────────────────────────────────────────

async def handle_start(session, user: dict, chat_id: int) -> None:
    user_id = user["id"]
    if str(user_id) not in users:
        # Telegram tells us the client's language; use it rather than making a
        # first-time user pick from a menu they may not be able to read.
        code = (user.get("language_code") or "")[:2]
        set_lang(user_id, code if code in i18n.LANGUAGES else i18n.DEFAULT_LANGUAGE)
    lang = lang_of(user_id)
    await send_message(session, chat_id, i18n.t(lang, "welcome"), menu_kb(lang))


async def handle_get(session, user_id: int, chat_id: int, callback_id: str) -> None:
    lang = lang_of(user_id)
    path = state["path"]
    if not path or not os.path.exists(path):
        await answer_callback(session, callback_id, i18n.t(lang, "not_ready"), alert=True)
        return

    await answer_callback(session, callback_id, i18n.t(lang, "preparing"))
    minutes = 0
    if state["built_at"]:
        minutes = int((datetime.now(timezone.utc) - state["built_at"]).total_seconds() // 60)
    # Only claim proxies were verified when some actually were; in protocol mode
    # the file is a mix of confirmed and unproven entries.
    caption_key = "file_caption_verified" if state["confirmed"] else "file_caption"
    caption = i18n.t(
        lang, caption_key,
        count=state["count"],
        confirmed=state["confirmed"],
        age=i18n.age_text(lang, minutes),
    )
    # A dated filename means saved copies don't overwrite each other, and the
    # user can see at a glance which one they're opening.
    stamp = (state["built_at"] or datetime.now(timezone.utc)).strftime("%Y%m%d-%H%M")
    await send_document(session, chat_id, path, f"nimku-proxies-{stamp}.txt",
                        caption, menu_kb(lang))


async def handle_callback(session, callback: dict) -> None:
    user = callback.get("from", {})
    user_id = user.get("id")
    chat_id = (callback.get("message") or {}).get("chat", {}).get("id")
    data = callback.get("data", "")
    callback_id = callback.get("id")
    if not user_id or not chat_id:
        return
    lang = lang_of(user_id)

    if data == "get":
        await handle_get(session, user_id, chat_id, callback_id)
        return

    await answer_callback(session, callback_id)

    if data == "app":
        await send_message(session, chat_id,
                           i18n.t(lang, "app", url=i18n.APK_URL, readme=i18n.README_URL),
                           menu_kb(lang))
    elif data == "help":
        await send_message(session, chat_id, i18n.t(lang, "help"), menu_kb(lang))
    elif data == "lang":
        await send_message(session, chat_id, i18n.t(lang, "choose_language"), language_kb())
    elif data.startswith("setlang:"):
        code = data.split(":", 1)[1]
        if code in i18n.LANGUAGES:
            set_lang(user_id, code)
        lang = lang_of(user_id)
        await send_message(session, chat_id, i18n.t(lang, "welcome"), menu_kb(lang))


async def handle_update(session, update: dict) -> None:
    if "callback_query" in update:
        await handle_callback(session, update["callback_query"])
        return
    message = update.get("message")
    if not message:
        return
    user = message.get("from") or {}
    chat_id = message.get("chat", {}).get("id")
    if not user.get("id") or not chat_id:
        return
    # Any message opens the menu, not just /start. Someone who types "hi" or
    # taps through from a channel link otherwise gets silence, which reads as a
    # broken bot.
    await handle_start(session, user, chat_id)


async def poll_updates(session: aiohttp.ClientSession) -> None:
    await api_call(session, "deleteWebhook", {"drop_pending_updates": True})
    offset = 0
    while True:
        try:
            data = await api_call(session, "getUpdates", {
                "offset": offset, "timeout": 25,
                "allowed_updates": ["message", "callback_query"],
            }, timeout=35)
            if not data.get("ok"):
                await asyncio.sleep(3)
                continue
            for update in data.get("result", []):
                offset = update["update_id"] + 1
                try:
                    await handle_update(session, update)
                except Exception as exc:  # noqa: BLE001
                    log.error("update handling failed: %s", exc, exc_info=True)
        except Exception as exc:  # noqa: BLE001
            log.error("polling error: %s — retrying in 5s", exc)
            await asyncio.sleep(5)


# ─────────────────────────────────────────────────────────────
#  Refresh loop
# ─────────────────────────────────────────────────────────────

async def make_telethon_client():
    """Optional — without it the bot simply skips the Telegram channels.

    The session name must not collide with any other Telethon process on this
    machine; two processes sharing one session file corrupt it.
    """
    if not cfg.has_telethon:
        log.warning("TG_API_ID/TG_API_HASH/TG_PHONE not set — scraping feeds only, no channels")
        return None
    try:
        from telethon import TelegramClient
    except ImportError:
        log.warning("telethon is not installed — scraping feeds only, no channels")
        return None

    client = TelegramClient(cfg.session_name, cfg.api_id, cfg.api_hash)
    await client.start(phone=cfg.phone)
    if not await client.is_user_authorized():
        log.error("Telethon session is not authorised — channels will be skipped")
        return None
    me = await client.get_me()
    log.info("Telethon signed in as %s", me.username or me.first_name)
    return client


async def refresh_loop(session: aiohttp.ClientSession) -> None:
    client = await make_telethon_client()
    while True:
        try:
            path, stats = await scraper.run_once(client, cfg)
            state.update({
                "path": path,
                "count": stats.published,
                "built_at": stats.started_at,
                "confirmed": stats.confirmed,
            })
            report = scraper.summary(stats, cfg)
            log.info("refresh complete — %s", report.splitlines()[0])
            if cfg.admin_id:
                await send_message(session, cfg.admin_id,
                                   f"🔄 <b>List rebuilt</b>\n\n<pre>{report}</pre>")
            if cfg.publish_channel and stats.published:
                await send_document(
                    session, cfg.publish_channel, path, "nimku-proxies.txt",
                    f"📥 {stats.published} proxies · {stats.started_at.strftime('%H:%M UTC')}",
                )
        except Exception as exc:  # noqa: BLE001 — the loop must outlive any single failure
            log.error("refresh failed: %s", exc, exc_info=True)
            if cfg.admin_id:
                await send_message(session, cfg.admin_id, f"⚠️ Refresh failed: {exc}")
        await asyncio.sleep(cfg.refresh_minutes * 60)


async def main() -> None:
    log.info("Nimku Proxy list bot starting")
    log.info("sources: %d channels + %d feeds | refresh: %dm | verify mode: %s",
             len(scraper.src.CHANNELS), len(scraper.src.FEEDS),
             cfg.refresh_minutes, cfg.verify_mode)
    async with aiohttp.ClientSession() as session:
        me = await api_call(session, "getMe", {})
        if not me.get("ok"):
            raise SystemExit(
                "Telegram rejected BOT_TOKEN. Check the value in .env — "
                "get a fresh one from @BotFather if you revoked the old one."
            )
        log.info("signed in as @%s", me["result"].get("username"))
        if cfg.admin_id:
            await send_message(session, cfg.admin_id, "🟢 Proxy list bot online — building first list…")
        await asyncio.gather(refresh_loop(session), poll_updates(session))


if __name__ == "__main__":
    asyncio.run(main())
