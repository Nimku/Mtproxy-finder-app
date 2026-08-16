"""Nimku Proxy list bot.

Rebuilds a verified proxy list on a schedule and hands it out as a file, so the
app keeps working for people whose network can't reach GitHub. Telegram is
usually the last thing still reachable, which is exactly why the list travels
through it.

Run:  python bot.py            (config comes from .env — see .env.example)
Test: python -m mtproto        (proves the proxy checker works on this host)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

import config
import i18n
import scraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("bot")

cfg = config.load()
bot = Bot(cfg.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

USERS_FILE = os.path.join(cfg.output_dir, "users.json")

# Current published list. Replaced wholesale by each refresh, so a user
# downloading while a rebuild is running always gets a complete older file
# rather than a half-written new one.
state: dict = {"path": None, "count": 0, "built_at": None, "verified": cfg.verify}


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

def menu_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=i18n.t(lang, "menu_get"), callback_data="get")],
        [InlineKeyboardButton(text=i18n.t(lang, "menu_app"), callback_data="app")],
        [InlineKeyboardButton(text=i18n.t(lang, "menu_help"), callback_data="help")],
        [InlineKeyboardButton(text=i18n.t(lang, "menu_language"), callback_data="lang")],
    ])


def language_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=label, callback_data=f"setlang:{code}")]
        for code, label in i18n.LANGUAGES.items()
    ])


# ─────────────────────────────────────────────────────────────
#  Handlers
# ─────────────────────────────────────────────────────────────

@dp.message(CommandStart())
async def on_start(message: Message) -> None:
    user_id = message.from_user.id
    if str(user_id) not in users:
        # Telegram tells us the client's language; use it rather than making a
        # first-time user pick from a menu they may not be able to read.
        code = (message.from_user.language_code or "")[:2]
        set_lang(user_id, code if code in i18n.LANGUAGES else i18n.DEFAULT_LANGUAGE)
    lang = lang_of(user_id)
    await message.answer(i18n.t(lang, "welcome"), reply_markup=menu_kb(lang))


@dp.callback_query(F.data == "get")
async def on_get(call: CallbackQuery) -> None:
    lang = lang_of(call.from_user.id)
    path = state["path"]
    if not path or not os.path.exists(path):
        await call.answer(i18n.t(lang, "not_ready"), show_alert=True)
        return

    await call.answer(i18n.t(lang, "preparing"))
    minutes = 0
    if state["built_at"]:
        minutes = int((datetime.now(timezone.utc) - state["built_at"]).total_seconds() // 60)
    caption_key = "file_caption_verified" if state["verified"] else "file_caption"
    caption = i18n.t(
        lang, caption_key,
        count=state["count"],
        age=i18n.age_text(lang, minutes),
    )
    # A dated filename means saved copies don't overwrite each other, and the
    # user can see at a glance which one they're opening.
    stamp = (state["built_at"] or datetime.now(timezone.utc)).strftime("%Y%m%d-%H%M")
    await bot.send_document(
        call.from_user.id,
        FSInputFile(path, filename=f"nimku-proxies-{stamp}.txt"),
        caption=caption,
        reply_markup=menu_kb(lang),
    )


@dp.callback_query(F.data == "app")
async def on_app(call: CallbackQuery) -> None:
    lang = lang_of(call.from_user.id)
    await call.answer()
    await call.message.answer(
        i18n.t(lang, "app", url=i18n.APK_URL, readme=i18n.README_URL),
        reply_markup=menu_kb(lang),
        disable_web_page_preview=True,
    )


@dp.callback_query(F.data == "help")
async def on_help(call: CallbackQuery) -> None:
    lang = lang_of(call.from_user.id)
    await call.answer()
    await call.message.answer(i18n.t(lang, "help"), reply_markup=menu_kb(lang))


@dp.callback_query(F.data == "lang")
async def on_lang(call: CallbackQuery) -> None:
    await call.answer()
    await call.message.answer(
        i18n.t(lang_of(call.from_user.id), "choose_language"),
        reply_markup=language_kb(),
    )


@dp.callback_query(F.data.startswith("setlang:"))
async def on_setlang(call: CallbackQuery) -> None:
    code = call.data.split(":", 1)[1]
    if code in i18n.LANGUAGES:
        set_lang(call.from_user.id, code)
    lang = lang_of(call.from_user.id)
    await call.answer()
    await call.message.answer(i18n.t(lang, "welcome"), reply_markup=menu_kb(lang))


# ─────────────────────────────────────────────────────────────
#  Refresh loop
# ─────────────────────────────────────────────────────────────

async def _make_telethon_client():
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


async def refresh_loop() -> None:
    client = await _make_telethon_client()
    while True:
        try:
            path, stats = await scraper.run_once(client, cfg)
            state.update({
                "path": path,
                "count": stats.published,
                "built_at": stats.started_at,
                "verified": cfg.verify,
            })
            report = scraper.summary(stats, cfg)
            log.info("refresh complete — %s", report.splitlines()[0])
            if cfg.admin_id:
                await bot.send_message(cfg.admin_id, f"🔄 <b>List rebuilt</b>\n\n<pre>{report}</pre>")
            if cfg.publish_channel and stats.published:
                await bot.send_document(
                    cfg.publish_channel,
                    FSInputFile(path, filename="nimku-proxies.txt"),
                    caption=(f"📥 {stats.published} proxies · "
                             f"{stats.started_at.strftime('%H:%M UTC')}"),
                )
        except Exception as exc:  # noqa: BLE001 — the loop must outlive any single failure
            log.error("refresh failed: %s", exc, exc_info=True)
            if cfg.admin_id:
                try:
                    await bot.send_message(cfg.admin_id, f"⚠️ Refresh failed: {exc}")
                except Exception:  # noqa: BLE001
                    pass
        await asyncio.sleep(cfg.refresh_minutes * 60)


async def main() -> None:
    log.info("Nimku Proxy list bot starting")
    log.info("sources: %d channels + %d feeds | refresh: %dm | verify: %s",
             len(scraper.src.CHANNELS), len(scraper.src.FEEDS),
             cfg.refresh_minutes, cfg.verify)
    asyncio.create_task(refresh_loop())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
