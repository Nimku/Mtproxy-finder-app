"""Every user-facing string, in each supported language.

To add a language: copy one block, translate the values, keep the {placeholders}
exactly as they are, and add it to LANGUAGES. Nothing else needs to change.
"""

LANGUAGES = {"en": "English", "ru": "Русский", "fa": "فارسی"}
DEFAULT_LANGUAGE = "en"

TEXT = {
    "en": {
        "choose_language": "Choose your language:",
        "welcome": (
            "👋 <b>Nimku Proxy</b>\n\n"
            "This bot sends you a fresh list of Telegram proxies as a file.\n\n"
            "It exists for one reason: in some regions GitHub is blocked, so the "
            "app can't download proxy lists on its own. Telegram usually still "
            "works — so the list comes to you through here instead.\n\n"
            "Tap <b>Get proxy list</b>, then open the file with the Nimku Proxy app."
        ),
        "menu_get": "📥 Get proxy list",
        "menu_app": "📲 Get the app",
        "menu_help": "❓ How to use",
        "menu_language": "🌐 Language",
        "preparing": "Preparing the list…",
        "not_ready": (
            "The list is still being built — this takes a few minutes after the bot "
            "starts. Please try again shortly."
        ),
        "file_caption": (
            "📥 <b>{count} proxies</b> · updated {age}\n\n"
            "Tap the file above → <b>Open with</b> → <b>Nimku Proxy</b>.\n"
            "The app will test each one and show those that work on your network."
        ),
        "file_caption_verified": (
            "📥 <b>{count} working proxies</b> · updated {age}\n\n"
            "Every one passed a real Telegram handshake on our server just now.\n\n"
            "Tap the file above → <b>Open with</b> → <b>Nimku Proxy</b>.\n"
            "The app re-tests them on your own network, because a proxy that works "
            "for us may still be blocked where you are."
        ),
        "help": (
            "❓ <b>How to use this</b>\n\n"
            "<b>1.</b> Tap <b>Get proxy list</b> — you'll receive a file.\n"
            "<b>2.</b> Tap the file here in Telegram.\n"
            "<b>3.</b> Choose <b>Open with → Nimku Proxy</b>.\n"
            "<b>4.</b> The app checks every proxy and shows the working ones, "
            "fastest first.\n"
            "<b>5.</b> Tap one to connect.\n\n"
            "Don't have the app? Tap <b>Get the app</b>.\n\n"
            "The list is rebuilt every hour, so come back for a fresh one whenever "
            "your proxy stops working."
        ),
        "app": (
            "📲 <b>Nimku Proxy for Android</b>\n\n"
            "Free, no subscription, no ads, no tracking.\n\n"
            "Download: {url}\n\n"
            "Install help for Xiaomi, Huawei and Samsung, plus how to verify the "
            "file before installing: {readme}"
        ),
        "age_just_now": "just now",
        "age_minutes": "{n} min ago",
        "age_hours": "{n} h ago",
    },
    "ru": {
        "choose_language": "Выберите язык:",
        "welcome": (
            "👋 <b>Nimku Proxy</b>\n\n"
            "Этот бот присылает свежий список прокси для Телеграм в виде файла.\n\n"
            "Он нужен по одной причине: в некоторых регионах GitHub заблокирован, "
            "и приложение не может само скачать списки прокси. Телеграм обычно "
            "продолжает работать — поэтому список приходит через него.\n\n"
            "Нажмите <b>Получить список</b> и откройте файл в приложении Nimku Proxy."
        ),
        "menu_get": "📥 Получить список",
        "menu_app": "📲 Скачать приложение",
        "menu_help": "❓ Как пользоваться",
        "menu_language": "🌐 Язык",
        "preparing": "Готовлю список…",
        "not_ready": (
            "Список ещё формируется — это занимает несколько минут после запуска "
            "бота. Попробуйте чуть позже."
        ),
        "file_caption": (
            "📥 <b>{count} прокси</b> · обновлено {age}\n\n"
            "Нажмите на файл выше → <b>Открыть с помощью</b> → <b>Nimku Proxy</b>.\n"
            "Приложение проверит каждый и покажет те, что работают в вашей сети."
        ),
        "file_caption_verified": (
            "📥 <b>{count} рабочих прокси</b> · обновлено {age}\n\n"
            "Каждый только что прошёл настоящее рукопожатие Телеграм на нашем сервере.\n\n"
            "Нажмите на файл выше → <b>Открыть с помощью</b> → <b>Nimku Proxy</b>.\n"
            "Приложение перепроверит их в вашей сети — прокси, работающий у нас, "
            "может быть заблокирован у вас."
        ),
        "help": (
            "❓ <b>Как этим пользоваться</b>\n\n"
            "<b>1.</b> Нажмите <b>Получить список</b> — придёт файл.\n"
            "<b>2.</b> Нажмите на этот файл здесь, в Телеграм.\n"
            "<b>3.</b> Выберите <b>Открыть с помощью → Nimku Proxy</b>.\n"
            "<b>4.</b> Приложение проверит все прокси и покажет рабочие, самые "
            "быстрые сверху.\n"
            "<b>5.</b> Нажмите на любой, чтобы подключиться.\n\n"
            "Нет приложения? Нажмите <b>Скачать приложение</b>.\n\n"
            "Список обновляется каждый час — возвращайтесь за свежим, когда прокси "
            "перестанет работать."
        ),
        "app": (
            "📲 <b>Nimku Proxy для Android</b>\n\n"
            "Бесплатно, без подписки, без рекламы, без слежки.\n\n"
            "Скачать: {url}\n\n"
            "Помощь с установкой на Xiaomi, Huawei и Samsung, а также как проверить "
            "файл перед установкой: {readme}"
        ),
        "age_just_now": "только что",
        "age_minutes": "{n} мин назад",
        "age_hours": "{n} ч назад",
    },
    "fa": {
        "choose_language": "زبان خود را انتخاب کنید:",
        "welcome": (
            "👋 <b>Nimku Proxy</b>\n\n"
            "این ربات فهرست تازه‌ای از پروکسی‌های تلگرام را به‌صورت فایل برایتان می‌فرستد.\n\n"
            "دلیل وجودش یک چیز است: در بعضی مناطق GitHub مسدود است و برنامه نمی‌تواند "
            "خودش فهرست پروکسی را دانلود کند. تلگرام معمولاً هنوز کار می‌کند — پس "
            "فهرست از این راه به شما می‌رسد.\n\n"
            "روی <b>دریافت فهرست</b> بزنید و فایل را با برنامهٔ Nimku Proxy باز کنید."
        ),
        "menu_get": "📥 دریافت فهرست",
        "menu_app": "📲 دریافت برنامه",
        "menu_help": "❓ راهنما",
        "menu_language": "🌐 زبان",
        "preparing": "در حال آماده‌سازی فهرست…",
        "not_ready": (
            "فهرست هنوز در حال ساخته‌شدن است — چند دقیقه پس از راه‌اندازی ربات طول "
            "می‌کشد. کمی بعد دوباره تلاش کنید."
        ),
        "file_caption": (
            "📥 <b>{count} پروکسی</b> · بروزرسانی {age}\n\n"
            "روی فایل بالا بزنید ← <b>باز کردن با</b> ← <b>Nimku Proxy</b>.\n"
            "برنامه هر کدام را آزمایش می‌کند و آن‌هایی را که در شبکهٔ شما کار می‌کنند نشان می‌دهد."
        ),
        "file_caption_verified": (
            "📥 <b>{count} پروکسی سالم</b> · بروزرسانی {age}\n\n"
            "همهٔ آن‌ها همین حالا روی سرور ما یک دست‌دادن واقعی تلگرام را با موفقیت گذرانده‌اند.\n\n"
            "روی فایل بالا بزنید ← <b>باز کردن با</b> ← <b>Nimku Proxy</b>.\n"
            "برنامه دوباره آن‌ها را در شبکهٔ خودتان آزمایش می‌کند، چون پروکسی‌ای که برای "
            "ما کار می‌کند ممکن است در محل شما مسدود باشد."
        ),
        "help": (
            "❓ <b>نحوهٔ استفاده</b>\n\n"
            "<b>۱.</b> روی <b>دریافت فهرست</b> بزنید — یک فایل دریافت می‌کنید.\n"
            "<b>۲.</b> همین‌جا در تلگرام روی فایل بزنید.\n"
            "<b>۳.</b> گزینهٔ <b>باز کردن با ← Nimku Proxy</b> را انتخاب کنید.\n"
            "<b>۴.</b> برنامه همهٔ پروکسی‌ها را بررسی می‌کند و سالم‌ها را، سریع‌ترین "
            "در بالا، نشان می‌دهد.\n"
            "<b>۵.</b> روی یکی بزنید تا وصل شوید.\n\n"
            "برنامه را ندارید؟ روی <b>دریافت برنامه</b> بزنید.\n\n"
            "فهرست هر ساعت بازسازی می‌شود — هر وقت پروکسی‌تان از کار افتاد، برای "
            "فهرست تازه برگردید."
        ),
        "app": (
            "📲 <b>Nimku Proxy برای اندروید</b>\n\n"
            "رایگان، بدون اشتراک، بدون تبلیغات، بدون ردیابی.\n\n"
            "دانلود: {url}\n\n"
            "راهنمای نصب برای شیائومی، هواوی و سامسونگ، و روش بررسی فایل پیش از نصب: {readme}"
        ),
        "age_just_now": "هم‌اکنون",
        "age_minutes": "{n} دقیقه پیش",
        "age_hours": "{n} ساعت پیش",
    },
}

APK_URL = "https://github.com/Nimku/Mtproxy-finder-app/releases/latest/download/NimkuProxy.apk"
README_URL = "https://github.com/Nimku/Mtproxy-finder-app#installing-the-apk"


def t(lang: str, key: str, **kwargs) -> str:
    table = TEXT.get(lang) or TEXT[DEFAULT_LANGUAGE]
    value = table.get(key) or TEXT[DEFAULT_LANGUAGE].get(key, key)
    return value.format(**kwargs) if kwargs else value


def age_text(lang: str, minutes: int) -> str:
    if minutes < 2:
        return t(lang, "age_just_now")
    if minutes < 60:
        return t(lang, "age_minutes", n=minutes)
    return t(lang, "age_hours", n=minutes // 60)
