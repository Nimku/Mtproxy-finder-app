"""
Nimku Proxy subscription bot.

Handles Telegram Stars payments and writes/reads license/status.json in the
app's GitHub repo. This is the ONLY thing that talks to the app's "backend" —
the app itself never contacts this bot or this VPS directly (see README.md).

Run: python bot.py   (reads config from environment / .env — see .env.example)
"""

import asyncio
import hashlib
import logging
import os
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)

import github_store
import storage
from i18n import LANGUAGES, DEFAULT_LANGUAGE, t

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("mtproxyfinder-bot")

BOT_TOKEN = os.environ["BOT_TOKEN"]
HASH_SALT = os.environ.get("HASH_SALT", "mtpf-v1-change-this-salt")
ADMIN_IDS = {int(x) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip()}

router = Router()


class AdminStates(StatesGroup):
    waiting_price = State()
    waiting_days = State()
    waiting_broadcast = State()


def hash_user_id(user_id: int) -> str:
    """MUST match LicenseManager.hashTelegramId() in the Android app exactly."""
    return hashlib.sha256((HASH_SALT + str(user_id)).encode("utf-8")).hexdigest()


def format_expiry(iso: str) -> tuple[str, int]:
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    days_left = max(0, (dt - datetime.now(timezone.utc)).days)
    return dt.strftime("%Y-%m-%d"), days_left


async def lang_for(message_or_query) -> str:
    chat_id = message_or_query.from_user.id
    return await storage.get_user_language(chat_id, DEFAULT_LANGUAGE)


def language_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=name, callback_data=f"lang:{code}")]
        for code, name in LANGUAGES.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ---------------------------------------------------------------- user side


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    chat_id = message.from_user.id
    users = await storage.load_users()
    if str(chat_id) not in users:
        await storage.upsert_user(chat_id, language=(message.from_user.language_code or DEFAULT_LANGUAGE)
                                   if (message.from_user.language_code in LANGUAGES) else DEFAULT_LANGUAGE)
        lang = await lang_for(message)
        await message.answer(t(lang, "choose_language"), reply_markup=language_keyboard())
        return
    lang = await lang_for(message)
    await message.answer(t(lang, "welcome"))
    await send_status(message, lang)


@router.message(Command("language"))
async def cmd_language(message: Message) -> None:
    lang = await lang_for(message)
    await message.answer(t(lang, "choose_language"), reply_markup=language_keyboard())


@router.callback_query(F.data.startswith("lang:"))
async def on_language_chosen(query: CallbackQuery) -> None:
    code = query.data.split(":", 1)[1]
    if code not in LANGUAGES:
        return
    await storage.upsert_user(query.from_user.id, language=code)
    await query.message.edit_text(t(code, "language_set"))
    await query.answer()
    await query.message.answer(t(code, "welcome"))
    await send_status(query.message, code, user_id=query.from_user.id)


async def send_status(message: Message, lang: str, user_id: int | None = None) -> None:
    uid = user_id or message.from_user.id
    config = await storage.load_config()
    try:
        remote = await github_store.read_status()
    except Exception:
        remote = {"subscriptions": {}}
    subs = remote.get("subscriptions", {})
    free_expiry = subs.get(github_store.FREE_FOR_ALL_KEY)
    personal_expiry = subs.get(hash_user_id(uid))

    now = datetime.now(timezone.utc)

    def is_future(iso: str | None) -> bool:
        if not iso:
            return False
        try:
            return datetime.fromisoformat(iso.replace("Z", "+00:00")) > now
        except ValueError:
            return False

    if config.free_mode or is_future(free_expiry):
        await message.answer(t(lang, "status_free"))
    elif is_future(personal_expiry):
        expires, days_left = format_expiry(personal_expiry)
        await message.answer(t(lang, "status_active", expires=expires, days_left=days_left))
    else:
        await message.answer(t(lang, "status_none"))
    await message.answer(t(lang, "howto_link", user_id=uid))


@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    lang = await lang_for(message)
    await send_status(message, lang)


@router.message(Command("subscribe"))
async def cmd_subscribe(message: Message) -> None:
    lang = await lang_for(message)
    config = await storage.load_config()
    user_id = message.from_user.id

    if config.free_mode:
        await message.answer(t(lang, "free_mode_notice"))
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=t(lang, "subscribe_free_button"), callback_data="claim_free")]]
        )
        await message.answer(t(lang, "subscribe_free_button"), reply_markup=keyboard)
        return

    await message.answer_invoice(
        title=t(lang, "invoice_title", days=config.subscription_days),
        description=t(lang, "invoice_description", days=config.subscription_days, user_id=user_id),
        payload=f"sub:{user_id}:{config.subscription_days}",
        currency="XTR",
        prices=[LabeledPrice(label=t(lang, "invoice_label", days=config.subscription_days), amount=config.price_stars)],
        provider_token="",
    )


@router.callback_query(F.data == "claim_free")
async def on_claim_free(query: CallbackQuery) -> None:
    lang = await lang_for(query)
    config = await storage.load_config()
    if not config.free_mode:
        await query.answer()
        return
    user_id = query.from_user.id
    try:
        expiry = await github_store.grant_subscription(hash_user_id(user_id), config.subscription_days, user_id)
    except Exception:
        log.exception("Failed to grant free subscription")
        await query.message.answer(t(lang, "generic_error"))
        await query.answer()
        return
    expires, _ = format_expiry(expiry)
    await query.message.answer(t(lang, "free_activated", expires=expires, user_id=user_id))
    await query.answer()


@router.pre_checkout_query()
async def on_pre_checkout(pre_checkout_query: PreCheckoutQuery) -> None:
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def on_successful_payment(message: Message) -> None:
    lang = await lang_for(message)
    config = await storage.load_config()
    user_id = message.from_user.id
    try:
        expiry = await github_store.grant_subscription(hash_user_id(user_id), config.subscription_days, user_id)
    except Exception:
        log.exception("Failed to record payment for %s", user_id)
        await message.answer(t(lang, "generic_error"))
        return
    expires, _ = format_expiry(expiry)
    await message.answer(t(lang, "payment_success", expires=expires, user_id=user_id))


# --------------------------------------------------------------- admin side


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def admin_keyboard(config: storage.Config, lang: str) -> InlineKeyboardMarkup:
    free_btn = (
        InlineKeyboardButton(text=t(lang, "admin_btn_free_off"), callback_data="admin:free_off")
        if config.free_mode
        else InlineKeyboardButton(text=t(lang, "admin_btn_free_on"), callback_data="admin:free_on")
    )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "admin_btn_price"), callback_data="admin:price")],
            [InlineKeyboardButton(text=t(lang, "admin_btn_days"), callback_data="admin:days")],
            [free_btn],
            [InlineKeyboardButton(text=t(lang, "admin_btn_stats"), callback_data="admin:stats")],
            [InlineKeyboardButton(text=t(lang, "admin_btn_broadcast"), callback_data="admin:broadcast")],
            [InlineKeyboardButton(text=t(lang, "admin_btn_close"), callback_data="admin:close")],
        ]
    )


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    lang = await lang_for(message)
    if not is_admin(message.from_user.id):
        await message.answer(t(lang, "not_admin"))
        return
    config = await storage.load_config()
    await message.answer(
        t(
            lang,
            "admin_menu",
            price=config.price_stars,
            days=config.subscription_days,
            free_mode="ON" if config.free_mode else "OFF",
        ),
        reply_markup=admin_keyboard(config, lang),
    )


@router.callback_query(F.data.startswith("admin:"))
async def on_admin_action(query: CallbackQuery, state: FSMContext) -> None:
    lang = await lang_for(query)
    if not is_admin(query.from_user.id):
        await query.answer(t(lang, "not_admin"), show_alert=True)
        return
    action = query.data.split(":", 1)[1]
    config = await storage.load_config()

    if action == "price":
        await state.set_state(AdminStates.waiting_price)
        await query.message.answer(t(lang, "admin_ask_price"))
    elif action == "days":
        await state.set_state(AdminStates.waiting_days)
        await query.message.answer(t(lang, "admin_ask_days"))
    elif action == "free_on":
        await github_store.set_free_for_all(True)
        config.free_mode = True
        await storage.save_config(config)
        await query.message.answer(t(lang, "admin_free_on"))
    elif action == "free_off":
        await github_store.set_free_for_all(False)
        config.free_mode = False
        await storage.save_config(config)
        await query.message.answer(t(lang, "admin_free_off"))
    elif action == "stats":
        users = await storage.load_users()
        langs: dict[str, int] = {}
        for entry in users.values():
            code = entry.get("language", DEFAULT_LANGUAGE)
            langs[code] = langs.get(code, 0) + 1
        lang_summary = ", ".join(f"{code}:{count}" for code, count in sorted(langs.items()))
        await query.message.answer(t(lang, "admin_stats", total=len(users), languages=lang_summary or "-"))
    elif action == "broadcast":
        await state.set_state(AdminStates.waiting_broadcast)
        await query.message.answer(t(lang, "admin_ask_broadcast"))
    elif action == "close":
        await query.message.delete()
    await query.answer()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    lang = await lang_for(message)
    if await state.get_state() is not None:
        await state.clear()
        await message.answer(t(lang, "admin_cancelled"))


@router.message(AdminStates.waiting_price)
async def on_admin_price(message: Message, state: FSMContext) -> None:
    lang = await lang_for(message)
    if not is_admin(message.from_user.id):
        return
    text = (message.text or "").strip()
    if not text.isdigit() or int(text) <= 0:
        await message.answer(t(lang, "admin_bad_number"))
        return
    config = await storage.load_config()
    config.price_stars = int(text)
    await storage.save_config(config)
    await state.clear()
    await message.answer(t(lang, "admin_price_set", price=config.price_stars))


@router.message(AdminStates.waiting_days)
async def on_admin_days(message: Message, state: FSMContext) -> None:
    lang = await lang_for(message)
    if not is_admin(message.from_user.id):
        return
    text = (message.text or "").strip()
    if not text.isdigit() or int(text) <= 0:
        await message.answer(t(lang, "admin_bad_number"))
        return
    config = await storage.load_config()
    config.subscription_days = int(text)
    await storage.save_config(config)
    await state.clear()
    await message.answer(t(lang, "admin_days_set", days=config.subscription_days))


@router.message(AdminStates.waiting_broadcast)
async def on_admin_broadcast(message: Message, state: FSMContext, bot: Bot) -> None:
    lang = await lang_for(message)
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    users = await storage.load_users()
    sent, failed = 0, 0
    for chat_id_str in users:
        try:
            await bot.copy_message(chat_id=int(chat_id_str), from_chat_id=message.chat.id, message_id=message.message_id)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)  # stay well under Telegram's rate limits
    await message.answer(t(lang, "admin_broadcast_done", count=sent, failed=failed))


@router.message()
async def on_unknown(message: Message) -> None:
    lang = await lang_for(message)
    await message.answer(t(lang, "unknown_command"))


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_router(router)
    log.info("Nimku Proxy bot starting (repo=%s)", os.environ.get("GITHUB_REPO"))
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
