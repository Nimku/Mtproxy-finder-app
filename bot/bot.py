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


def touch_user(user_id: int) -> None:
    """Anyone who interacts is a live user again — someone who blocked the bot
    and later unblocked it should start receiving broadcasts once more."""
    record = users.setdefault(str(user_id), {})
    record["seen"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if record.pop("blocked", None):
        _save_users()


def broadcast_targets() -> list[int]:
    return [int(uid) for uid, rec in users.items() if not rec.get("blocked")]


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


def language_kb(with_back: bool = False) -> dict:
    """Two per row — seven languages in one column is a lot of scrolling on a
    phone, which is where essentially every user of this bot is."""
    codes = list(i18n.LANGUAGES.items())
    rows = [
        [{"text": label, "callback_data": f"setlang:{code}"}
         for code, label in codes[i:i + 2]]
        for i in range(0, len(codes), 2)
    ]
    if with_back:
        rows.append([{"text": i18n.t(i18n.DEFAULT_LANGUAGE, "menu_back"),
                      "callback_data": "menu"}])
    return {"inline_keyboard": rows}


def after_file_kb(lang: str) -> dict:
    """Shown with the file itself. The two things a user needs next are right
    there: another list if these don't work, or the app if they can't open it."""
    return {"inline_keyboard": [
        [{"text": i18n.t(lang, "btn_again"), "callback_data": "get"}],
        [{"text": i18n.t(lang, "btn_noapp"), "callback_data": "app"}],
        [{"text": i18n.t(lang, "menu_help"), "callback_data": "help"}],
        [{"text": i18n.t(lang, "menu_back"), "callback_data": "menu"}],
    ]}


def admin_kb(lang: str = i18n.DEFAULT_LANGUAGE) -> dict:
    """Admin actions plus the ordinary ones.

    This keyboard is attached to the hourly report, which is the message the
    owner actually sees most often — so it has to be a place you can act from,
    not a dead end that sends you back to typing /start.
    """
    return {"inline_keyboard": [
        [{"text": i18n.t(lang, "menu_get"), "callback_data": "get"}],
        [{"text": "📊 Stats", "callback_data": "adm:stats"},
         {"text": "🔄 Rebuild now", "callback_data": "adm:rebuild"}],
        [{"text": "📢 Broadcast to all users", "callback_data": "adm:bc"}],
        [{"text": i18n.t(lang, "menu_back"), "callback_data": "menu"}],
    ]}


def confirm_kb() -> dict:
    return {"inline_keyboard": [
        [{"text": "✅ Send it", "callback_data": "adm:send"}],
        [{"text": "❌ Cancel", "callback_data": "adm:cancel"}],
    ]}


# What the admin is in the middle of doing, e.g. composing a broadcast.
admin_state: dict = {}

# Set by "Rebuild list now" to wake the refresh loop out of its sleep.
rebuild_now = asyncio.Event()


def is_admin(user_id: int) -> bool:
    return bool(cfg.admin_id) and user_id == cfg.admin_id


# ─────────────────────────────────────────────────────────────
#  Admin
# ─────────────────────────────────────────────────────────────

async def send_admin_menu(session, chat_id: int) -> None:
    await send_message(session, chat_id, "⚙️ <b>Admin</b>", admin_kb())


async def send_stats(session, chat_id: int) -> None:
    by_lang: dict[str, int] = {}
    blocked = 0
    for record in users.values():
        if record.get("blocked"):
            blocked += 1
            continue
        code = record.get("lang", i18n.DEFAULT_LANGUAGE)
        by_lang[code] = by_lang.get(code, 0) + 1
    breakdown = "\n".join(
        f"  {i18n.LANGUAGES.get(code, code)}  {n}"
        for code, n in sorted(by_lang.items(), key=lambda kv: -kv[1])
    ) or "  nobody yet"

    built = state["built_at"]
    age = "never" if not built else (
        f"{int((datetime.now(timezone.utc) - built).total_seconds() // 60)} min ago")
    await send_message(session, chat_id, (
        f"📊 <b>Stats</b>\n\n"
        f"Users: <b>{len(users) - blocked}</b>"
        + (f"  (+{blocked} blocked the bot)" if blocked else "") + "\n\n"
        f"<b>By language</b>\n{breakdown}\n\n"
        f"<b>Current list</b>\n"
        f"  {state['count']} proxies, {state['confirmed']} confirmed\n"
        f"  built {age}"
    ), admin_kb())


async def run_broadcast(session, text: str) -> None:
    """Sends to every user, slowly enough that Telegram doesn't rate-limit us.

    The Bot API tolerates roughly 30 messages a second across different chats;
    20/s leaves headroom so a large broadcast doesn't start getting 429s
    partway through and silently miss people. Anyone who has blocked the bot
    comes back as 403 — mark them so later broadcasts skip them instead of
    burning quota on chats that will never deliver.
    """
    targets = broadcast_targets()
    sent = failed = 0
    for user_id in targets:
        result = await send_message(session, user_id, text)
        if result.get("ok"):
            sent += 1
        else:
            failed += 1
            description = str(result.get("description", "")).lower()
            if "blocked" in description or "chat not found" in description \
                    or "user is deactivated" in description:
                users.setdefault(str(user_id), {})["blocked"] = True
        await asyncio.sleep(0.05)
    _save_users()
    await send_message(session, cfg.admin_id, (
        f"📢 <b>Broadcast finished</b>\n\n"
        f"Delivered: <b>{sent}</b>\n"
        f"Failed: {failed}"
        + ("\n\nFailures are mostly people who blocked the bot; "
           "they're now skipped in future broadcasts." if failed else "")
    ), admin_kb())


async def handle_admin_callback(session, data: str, chat_id: int, callback_id: str) -> bool:
    if data == "adm:stats":
        await answer_callback(session, callback_id)
        await send_stats(session, chat_id)
    elif data == "adm:bc":
        await answer_callback(session, callback_id)
        admin_state["awaiting"] = "broadcast"
        await send_message(session, chat_id, (
            "📢 <b>Broadcast</b>\n\n"
            "Send me the message now and I'll show you a preview before "
            "anything goes out.\n\n"
            f"It will reach <b>{len(broadcast_targets())}</b> users.\n\n"
            "HTML formatting works: &lt;b&gt;bold&lt;/b&gt;, &lt;i&gt;italic&lt;/i&gt;, "
            "&lt;a href=\"...\"&gt;link&lt;/a&gt;\n\n"
            "Send /cancel to abort."
        ))
    elif data == "adm:send":
        await answer_callback(session, callback_id)
        text = admin_state.pop("draft", None)
        admin_state.pop("awaiting", None)
        if not text:
            await send_message(session, chat_id, "Nothing to send.", admin_kb())
            return True
        await send_message(session, chat_id,
                           f"Sending to {len(broadcast_targets())} users…")
        asyncio.create_task(run_broadcast(session, text))
    elif data == "adm:cancel":
        await answer_callback(session, callback_id, "Cancelled")
        admin_state.clear()
        await send_message(session, chat_id, "❌ Broadcast cancelled.", admin_kb())
    elif data == "adm:rebuild":
        await answer_callback(session, callback_id, "Rebuilding…")
        rebuild_now.set()
        await send_message(session, chat_id,
                           "🔄 Rebuilding the list now — the report arrives when it's done.")
    else:
        return False
    return True


async def handle_admin_message(session, text: str, chat_id: int) -> bool:
    """Returns True if the message was consumed by an admin flow."""
    if text.strip().lower() in ("/admin", "/settings"):
        await send_admin_menu(session, chat_id)
        return True
    if text.strip().lower() == "/cancel" and admin_state:
        admin_state.clear()
        await send_message(session, chat_id, "❌ Cancelled.", admin_kb())
        return True
    if admin_state.get("awaiting") == "broadcast":
        admin_state["draft"] = text
        await send_message(session, chat_id, (
            "👀 <b>Preview — this is exactly what users will see:</b>"))
        await send_message(session, chat_id, text)
        await send_message(session, chat_id, (
            f"Send this to <b>{len(broadcast_targets())}</b> users?"), confirm_kb())
        return True
    return False


# ─────────────────────────────────────────────────────────────
#  Handlers
# ─────────────────────────────────────────────────────────────

async def handle_start(session, user: dict, chat_id: int) -> None:
    """First contact shows the language picker; everything after it is in the
    user's own language.

    Guessing silently from Telegram's language_code isn't enough on its own —
    plenty of people in Iran and Russia run their Telegram in English, and a
    wall of English text is exactly where a non-technical user gives up. The
    guess still decides which language the picker itself is written in, so even
    that first screen is usually readable.
    """
    user_id = user["id"]
    if str(user_id) not in users:
        guess = i18n.match_language(user.get("language_code")) or i18n.DEFAULT_LANGUAGE
        await send_message(session, chat_id,
                           i18n.t(guess, "choose_language"), language_kb())
        return
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
                        caption, after_file_kb(lang))


async def handle_callback(session, callback: dict) -> None:
    user = callback.get("from", {})
    user_id = user.get("id")
    chat_id = (callback.get("message") or {}).get("chat", {}).get("id")
    data = callback.get("data", "")
    callback_id = callback.get("id")
    if not user_id or not chat_id:
        return
    if is_admin(user_id) and data.startswith("adm:"):
        await handle_admin_callback(session, data, chat_id, callback_id)
        return
    touch_user(user_id)
    lang = lang_of(user_id)

    if data == "get":
        await handle_get(session, user_id, chat_id, callback_id)
        return

    await answer_callback(session, callback_id)

    if data == "app":
        # A url button opens the page in one tap; the link stays in the text too
        # so it survives being forwarded to someone else.
        await send_message(session, chat_id,
                           i18n.t(lang, "app", url=i18n.APK_URL, readme=i18n.README_URL),
                           {"inline_keyboard": [
                               [{"text": i18n.t(lang, "menu_app"), "url": i18n.APK_URL}],
                               [{"text": i18n.t(lang, "menu_help"), "callback_data": "help"}],
                               [{"text": i18n.t(lang, "menu_back"), "callback_data": "menu"}],
                           ]})
    elif data == "help":
        await send_message(session, chat_id, i18n.t(lang, "help"), menu_kb(lang))
    elif data == "lang":
        await send_message(session, chat_id, i18n.t(lang, "choose_language"),
                           language_kb(with_back=True))
    elif data == "menu":
        await send_message(session, chat_id, i18n.t(lang, "welcome"), menu_kb(lang))
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
    user_id = user.get("id")
    if not user_id or not chat_id:
        return
    text = message.get("text") or ""
    if is_admin(user_id) and await handle_admin_message(session, text, chat_id):
        return
    touch_user(user_id)
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
                                   f"🔄 <b>List rebuilt</b>\n\n<pre>{report}</pre>",
                                   admin_kb(lang_of(cfg.admin_id)))
            if cfg.publish_channel and stats.published:
                await send_document(
                    session, cfg.publish_channel, path, "nimku-proxies.txt",
                    f"📥 {stats.published} proxies · {stats.started_at.strftime('%H:%M UTC')}",
                )
        except Exception as exc:  # noqa: BLE001 — the loop must outlive any single failure
            log.error("refresh failed: %s", exc, exc_info=True)
            if cfg.admin_id:
                await send_message(session, cfg.admin_id, f"⚠️ Refresh failed: {exc}",
                                   admin_kb(lang_of(cfg.admin_id)))
        # Sleep until the next scheduled rebuild, unless the admin asks for one
        # sooner — then wake immediately rather than waiting out the hour.
        try:
            await asyncio.wait_for(rebuild_now.wait(), timeout=cfg.refresh_minutes * 60)
        except asyncio.TimeoutError:
            pass
        rebuild_now.clear()


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
            await send_message(session, cfg.admin_id,
                               "🟢 Proxy list bot online — building first list…\n\n"
                               "Send /admin for stats, broadcast and manual rebuild.",
                               admin_kb(lang_of(cfg.admin_id)))
        await asyncio.gather(refresh_loop(session), poll_updates(session))


if __name__ == "__main__":
    asyncio.run(main())
