"""
Bot text, in every supported language.

To add a language: copy one of the dicts below, translate the values (keep the
{placeholders} exactly as-is), add it to TEXT, and add one line to LANGUAGES.
Nothing else in the bot needs to change — this file is the only place language
strings live.
"""

LANGUAGES = {
    "en": "English",
    "ru": "Русский",
    "fa": "فارسی",
}

DEFAULT_LANGUAGE = "en"

TEXT = {
    "en": {
        "choose_language": "Choose your language:",
        "language_set": "Language set to English.",
        "welcome": (
            "👋 Welcome to the MTProxy Finder subscription bot.\n\n"
            "This bot manages your app subscription. Payment happens here, in "
            "Telegram — the app itself never talks to this bot or to any server "
            "directly, which keeps it working even where direct connections are "
            "blocked.\n\n"
            "Use /subscribe to pay, /status to check your subscription, or "
            "/language to change language."
        ),
        "status_active": "✅ Active until {expires} ({days_left} day(s) left).",
        "status_none": "❌ No active subscription yet. Use /subscribe.",
        "status_free": "🆓 Subscriptions are currently free for everyone.",
        "howto_link": (
            "In the app, open the subscription screen and enter this Telegram ID "
            "so it can find your subscription: <code>{user_id}</code>"
        ),
        "subscribe_free_button": "🆓 Activate free access",
        "subscribe_button": "⭐ Pay {price} Stars — {days} days",
        "free_mode_notice": "Subscriptions are free right now — tap below to activate.",
        "invoice_title": "MTProxy Finder — {days} day subscription",
        "invoice_description": "Unlocks the app for {days} days for Telegram ID {user_id}.",
        "invoice_label": "{days}-day subscription",
        "payment_success": (
            "✅ Payment received! Your subscription is active until {expires}.\n\n"
            "If you haven't already, open the app's subscription screen and enter "
            "this Telegram ID: <code>{user_id}</code>"
        ),
        "free_activated": (
            "✅ Free access activated until {expires}.\n\n"
            "Open the app's subscription screen and enter this Telegram ID: "
            "<code>{user_id}</code>"
        ),
        "generic_error": "Something went wrong talking to GitHub. Please try again in a moment.",
        "not_admin": "This command is for the bot admin only.",
        "admin_menu": (
            "⚙️ Admin panel\n\n"
            "Price: {price} ⭐\n"
            "Period: {days} day(s)\n"
            "Free mode: {free_mode}\n"
        ),
        "admin_btn_price": "💰 Set price",
        "admin_btn_days": "📅 Set period (days)",
        "admin_btn_free_on": "🆓 Turn free mode ON",
        "admin_btn_free_off": "🆓 Turn free mode OFF",
        "admin_btn_stats": "📊 Stats",
        "admin_btn_broadcast": "📢 Broadcast",
        "admin_btn_close": "Close",
        "admin_ask_price": "Send the new price in Stars (whole number, e.g. 20).",
        "admin_ask_days": "Send the new subscription period in days (whole number, e.g. 30).",
        "admin_ask_broadcast": "Send the message to broadcast to every known user.",
        "admin_bad_number": "That's not a valid whole number. Try again, or send /cancel.",
        "admin_price_set": "Price updated to {price} ⭐.",
        "admin_days_set": "Subscription period updated to {days} day(s).",
        "admin_free_on": "Free mode is now ON — everyone gets free access immediately.",
        "admin_free_off": "Free mode is now OFF — payment is required again.",
        "admin_stats": "👥 Known users: {total}\n💬 Languages: {languages}",
        "admin_broadcast_done": "Broadcast sent to {count} user(s) ({failed} failed).",
        "admin_cancelled": "Cancelled.",
        "unknown_command": "Unknown command. Try /start.",
    },
    "ru": {
        "choose_language": "Выберите язык:",
        "language_set": "Язык изменён на русский.",
        "welcome": (
            "👋 Добро пожаловать в бот подписки MTProxy Finder.\n\n"
            "Этот бот управляет подпиской в приложении. Оплата происходит здесь, "
            "в Telegram — само приложение никогда не обращается напрямую к боту "
            "или к серверу, поэтому оно продолжает работать даже там, где прямые "
            "соединения блокируются.\n\n"
            "Команда /subscribe — оплатить, /status — проверить подписку, "
            "/language — сменить язык."
        ),
        "status_active": "✅ Активна до {expires} (осталось {days_left} дн.).",
        "status_none": "❌ Подписки пока нет. Используйте /subscribe.",
        "status_free": "🆓 Сейчас подписка бесплатна для всех.",
        "howto_link": (
            "В приложении откройте экран подписки и введите этот Telegram ID, "
            "чтобы оно нашло вашу подписку: <code>{user_id}</code>"
        ),
        "subscribe_free_button": "🆓 Активировать бесплатный доступ",
        "subscribe_button": "⭐ Оплатить {price} Stars — {days} дн.",
        "free_mode_notice": "Сейчас подписка бесплатна — нажмите ниже, чтобы активировать.",
        "invoice_title": "MTProxy Finder — подписка на {days} дн.",
        "invoice_description": "Открывает приложение на {days} дн. для Telegram ID {user_id}.",
        "invoice_label": "Подписка на {days} дн.",
        "payment_success": (
            "✅ Оплата получена! Подписка активна до {expires}.\n\n"
            "Если ещё не сделали этого — откройте экран подписки в приложении и "
            "введите этот Telegram ID: <code>{user_id}</code>"
        ),
        "free_activated": (
            "✅ Бесплатный доступ активирован до {expires}.\n\n"
            "Откройте экран подписки в приложении и введите этот Telegram ID: "
            "<code>{user_id}</code>"
        ),
        "generic_error": "Не удалось связаться с GitHub. Попробуйте ещё раз через момент.",
        "not_admin": "Эта команда доступна только администратору бота.",
        "admin_menu": (
            "⚙️ Панель администратора\n\n"
            "Цена: {price} ⭐\n"
            "Период: {days} дн.\n"
            "Бесплатный режим: {free_mode}\n"
        ),
        "admin_btn_price": "💰 Изменить цену",
        "admin_btn_days": "📅 Изменить период (дней)",
        "admin_btn_free_on": "🆓 Включить бесплатный режим",
        "admin_btn_free_off": "🆓 Выключить бесплатный режим",
        "admin_btn_stats": "📊 Статистика",
        "admin_btn_broadcast": "📢 Рассылка",
        "admin_btn_close": "Закрыть",
        "admin_ask_price": "Отправьте новую цену в Stars (целое число, например 20).",
        "admin_ask_days": "Отправьте новый период подписки в днях (целое число, например 30).",
        "admin_ask_broadcast": "Отправьте сообщение для рассылки всем известным пользователям.",
        "admin_bad_number": "Это не целое число. Попробуйте ещё раз или отправьте /cancel.",
        "admin_price_set": "Цена изменена на {price} ⭐.",
        "admin_days_set": "Период подписки изменён на {days} дн.",
        "admin_free_on": "Бесплатный режим включён — у всех сразу бесплатный доступ.",
        "admin_free_off": "Бесплатный режим выключен — снова нужна оплата.",
        "admin_stats": "👥 Известно пользователей: {total}\n💬 Языки: {languages}",
        "admin_broadcast_done": "Рассылка отправлена {count} пользователям (ошибок: {failed}).",
        "admin_cancelled": "Отменено.",
        "unknown_command": "Неизвестная команда. Попробуйте /start.",
    },
    "fa": {
        "choose_language": "زبان خود را انتخاب کنید:",
        "language_set": "زبان به فارسی تغییر کرد.",
        "welcome": (
            "👋 به ربات اشتراک MTProxy Finder خوش آمدید.\n\n"
            "این ربات اشتراک برنامه شما را مدیریت می‌کند. پرداخت همینجا در "
            "تلگرام انجام می‌شود — خود برنامه هرگز مستقیماً با این ربات یا هیچ "
            "سروری صحبت نمی‌کند، به همین دلیل حتی جایی که اتصال مستقیم مسدود "
            "است هم کار می‌کند.\n\n"
            "برای پرداخت /subscribe، برای وضعیت اشتراک /status و برای تغییر "
            "زبان /language را بفرستید."
        ),
        "status_active": "✅ فعال تا {expires} ({days_left} روز باقی‌مانده).",
        "status_none": "❌ هنوز اشتراکی فعال نیست. از /subscribe استفاده کنید.",
        "status_free": "🆓 در حال حاضر اشتراک برای همه رایگان است.",
        "howto_link": (
            "در برنامه، صفحه اشتراک را باز کنید و این شناسه تلگرام را وارد کنید "
            "تا اشتراک شما پیدا شود: <code>{user_id}</code>"
        ),
        "subscribe_free_button": "🆓 فعال‌سازی دسترسی رایگان",
        "subscribe_button": "⭐ پرداخت {price} استارز — {days} روز",
        "free_mode_notice": "در حال حاضر اشتراک رایگان است — برای فعال‌سازی روی دکمه زیر بزنید.",
        "invoice_title": "MTProxy Finder — اشتراک {days} روزه",
        "invoice_description": "برنامه را برای {days} روز برای شناسه تلگرام {user_id} باز می‌کند.",
        "invoice_label": "اشتراک {days} روزه",
        "payment_success": (
            "✅ پرداخت دریافت شد! اشتراک شما تا {expires} فعال است.\n\n"
            "اگر هنوز انجام نداده‌اید، صفحه اشتراک برنامه را باز کنید و این "
            "شناسه تلگرام را وارد کنید: <code>{user_id}</code>"
        ),
        "free_activated": (
            "✅ دسترسی رایگان تا {expires} فعال شد.\n\n"
            "صفحه اشتراک برنامه را باز کنید و این شناسه تلگرام را وارد کنید: "
            "<code>{user_id}</code>"
        ),
        "generic_error": "ارتباط با GitHub با خطا مواجه شد. لطفاً کمی بعد دوباره تلاش کنید.",
        "not_admin": "این دستور فقط برای مدیر ربات است.",
        "admin_menu": (
            "⚙️ پنل مدیریت\n\n"
            "قیمت: {price} ⭐\n"
            "مدت: {days} روز\n"
            "حالت رایگان: {free_mode}\n"
        ),
        "admin_btn_price": "💰 تنظیم قیمت",
        "admin_btn_days": "📅 تنظیم مدت (روز)",
        "admin_btn_free_on": "🆓 روشن کردن حالت رایگان",
        "admin_btn_free_off": "🆓 خاموش کردن حالت رایگان",
        "admin_btn_stats": "📊 آمار",
        "admin_btn_broadcast": "📢 پیام همگانی",
        "admin_btn_close": "بستن",
        "admin_ask_price": "قیمت جدید را به استارز بفرستید (عدد صحیح، مثلاً ۲۰).",
        "admin_ask_days": "مدت جدید اشتراک را به روز بفرستید (عدد صحیح، مثلاً ۳۰).",
        "admin_ask_broadcast": "پیامی که باید برای همه کاربران شناخته‌شده ارسال شود را بفرستید.",
        "admin_bad_number": "این یک عدد صحیح معتبر نیست. دوباره امتحان کنید یا /cancel را بفرستید.",
        "admin_price_set": "قیمت به {price} ⭐ تغییر کرد.",
        "admin_days_set": "مدت اشتراک به {days} روز تغییر کرد.",
        "admin_free_on": "حالت رایگان روشن شد — همه فوراً دسترسی رایگان دارند.",
        "admin_free_off": "حالت رایگان خاموش شد — پرداخت دوباره لازم است.",
        "admin_stats": "👥 کاربران شناخته‌شده: {total}\n💬 زبان‌ها: {languages}",
        "admin_broadcast_done": "پیام همگانی برای {count} کاربر ارسال شد ({failed} ناموفق).",
        "admin_cancelled": "لغو شد.",
        "unknown_command": "دستور نامشخص. /start را امتحان کنید.",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    lang_dict = TEXT.get(lang) or TEXT[DEFAULT_LANGUAGE]
    template = lang_dict.get(key) or TEXT[DEFAULT_LANGUAGE].get(key, key)
    return template.format(**kwargs)
