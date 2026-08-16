"""Every user-facing string, in each supported language.

Written for someone who has never used a proxy and may not know what one is.
The bot teaches by walking them through it rather than explaining first: pick a
language, see three numbered steps, press the one obvious button.

To add a language: copy a block, translate the values, keep the {placeholders}
and the HTML tags exactly as they are, and add one line to LANGUAGES. Nothing
else in the bot needs to change.
"""

LANGUAGES = {
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Русский",
    "fa": "🇮🇷 فارسی",
    "ar": "🇸🇦 العربية",
    "uk": "🇺🇦 Українська",
    "tr": "🇹🇷 Türkçe",
    "zh": "🇨🇳 中文",
}
DEFAULT_LANGUAGE = "en"

TEXT = {
    # ─────────────────────────── English ───────────────────────────
    "en": {
        "choose_language": "🌐 Choose your language:",
        "welcome": (
            "👋 <b>Nimku Proxy</b>\n\n"
            "I give you Telegram proxies that actually work.\n\n"
            "If Telegram is blocked or slow where you are, a proxy fixes it.\n\n"
            "<b>Three steps:</b>\n"
            "1️⃣ Press <b>📥 Get proxy list</b> — I send you a file\n"
            "2️⃣ Open that file with the <b>Nimku Proxy</b> app\n"
            "3️⃣ The app finds which ones work for you — tap one to connect\n\n"
            "Don't have the app? Press <b>📲 Get the app</b> first."
        ),
        "menu_get": "📥 Get proxy list",
        "menu_app": "📲 Get the app",
        "menu_help": "❓ How to use",
        "menu_language": "🌐 Language",
        "menu_back": "⬅️ Back to menu",
        "btn_again": "🔄 Get a fresh list",
        "btn_noapp": "📲 I don't have the app",
        "preparing": "Sending the list…",
        "not_ready": (
            "The list is still being built — it takes a few minutes. "
            "Please try again shortly."
        ),
        "file_caption": (
            "📥 <b>{count} proxies</b> · updated {age}\n\n"
            "<b>Now do this:</b>\n"
            "1️⃣ Tap the file above ☝️\n"
            "2️⃣ Choose <b>Open with → Nimku Proxy</b>\n"
            "3️⃣ Wait while the app tests them\n"
            "4️⃣ Tap a working proxy to connect"
        ),
        "file_caption_verified": (
            "📥 <b>{count} proxies</b> · updated {age}\n"
            "✅ {confirmed} confirmed working just now\n\n"
            "<b>Now do this:</b>\n"
            "1️⃣ Tap the file above ☝️\n"
            "2️⃣ Choose <b>Open with → Nimku Proxy</b>\n"
            "3️⃣ Wait while the app tests them\n"
            "4️⃣ Tap a working proxy to connect"
        ),
        "help": (
            "❓ <b>How to use this</b>\n\n"
            "<b>What is a proxy?</b>\n"
            "A computer in another country that carries your Telegram traffic, "
            "so Telegram connects even where it's blocked. It only affects "
            "Telegram — not your browser or other apps.\n\n"
            "<b>Step by step</b>\n"
            "1️⃣ Press <b>📥 Get proxy list</b> — a file arrives here\n"
            "2️⃣ Tap that file\n"
            "3️⃣ Choose <b>Open with → Nimku Proxy</b>\n"
            "4️⃣ The app tests every proxy and shows the working ones, "
            "fastest first\n"
            "5️⃣ Tap one — Telegram asks to enable it — confirm\n\n"
            "<b>If it stops working</b>\n"
            "Proxies die often, it's normal. Come back, get a fresh list, "
            "pick another one. I rebuild the list every hour.\n\n"
            "<b>If the file won't open</b>\n"
            "You need the app installed first — press <b>📲 Get the app</b>."
        ),
        "app": (
            "📲 <b>Nimku Proxy for Android</b>\n\n"
            "Free. No subscription, no ads, no tracking, no sign-up.\n\n"
            "<b>1.</b> Download: {url}\n"
            "<b>2.</b> Open the downloaded file\n"
            "<b>3.</b> Android will warn you — tap <b>Settings</b>, allow "
            "installing from this source, then <b>Install</b>\n\n"
            "Xiaomi, Huawei or Samsung need extra steps — they're listed here, "
            "along with how to check the file is safe before installing:\n{readme}"
        ),
        "age_just_now": "just now",
        "age_minutes": "{n} min ago",
        "age_hours": "{n} h ago",
    },

    # ─────────────────────────── Русский ───────────────────────────
    "ru": {
        "choose_language": "🌐 Выберите язык:",
        "welcome": (
            "👋 <b>Nimku Proxy</b>\n\n"
            "Я даю прокси для Телеграм, которые действительно работают.\n\n"
            "Если Телеграм заблокирован или тормозит — прокси это решает.\n\n"
            "<b>Три шага:</b>\n"
            "1️⃣ Нажмите <b>📥 Получить список</b> — пришлю файл\n"
            "2️⃣ Откройте этот файл приложением <b>Nimku Proxy</b>\n"
            "3️⃣ Приложение найдёт рабочие — нажмите на любой, чтобы подключиться\n\n"
            "Нет приложения? Сначала нажмите <b>📲 Скачать приложение</b>."
        ),
        "menu_get": "📥 Получить список",
        "menu_app": "📲 Скачать приложение",
        "menu_help": "❓ Как пользоваться",
        "menu_language": "🌐 Язык",
        "menu_back": "⬅️ В меню",
        "btn_again": "🔄 Свежий список",
        "btn_noapp": "📲 У меня нет приложения",
        "preparing": "Отправляю список…",
        "not_ready": (
            "Список ещё формируется — это займёт пару минут. "
            "Попробуйте чуть позже."
        ),
        "file_caption": (
            "📥 <b>{count} прокси</b> · обновлено {age}\n\n"
            "<b>Теперь сделайте так:</b>\n"
            "1️⃣ Нажмите на файл выше ☝️\n"
            "2️⃣ Выберите <b>Открыть с помощью → Nimku Proxy</b>\n"
            "3️⃣ Подождите, пока приложение их проверит\n"
            "4️⃣ Нажмите на рабочий прокси, чтобы подключиться"
        ),
        "file_caption_verified": (
            "📥 <b>{count} прокси</b> · обновлено {age}\n"
            "✅ {confirmed} только что проверены и работают\n\n"
            "<b>Теперь сделайте так:</b>\n"
            "1️⃣ Нажмите на файл выше ☝️\n"
            "2️⃣ Выберите <b>Открыть с помощью → Nimku Proxy</b>\n"
            "3️⃣ Подождите, пока приложение их проверит\n"
            "4️⃣ Нажмите на рабочий прокси, чтобы подключиться"
        ),
        "help": (
            "❓ <b>Как этим пользоваться</b>\n\n"
            "<b>Что такое прокси?</b>\n"
            "Компьютер в другой стране, который передаёт ваш трафик Телеграм, "
            "чтобы мессенджер работал даже там, где он заблокирован. Влияет "
            "только на Телеграм — браузер и другие приложения не затрагивает.\n\n"
            "<b>По шагам</b>\n"
            "1️⃣ Нажмите <b>📥 Получить список</b> — сюда придёт файл\n"
            "2️⃣ Нажмите на этот файл\n"
            "3️⃣ Выберите <b>Открыть с помощью → Nimku Proxy</b>\n"
            "4️⃣ Приложение проверит все прокси и покажет рабочие, "
            "самые быстрые сверху\n"
            "5️⃣ Нажмите на любой — Телеграм спросит подтверждение — согласитесь\n\n"
            "<b>Если перестал работать</b>\n"
            "Прокси часто умирают, это нормально. Вернитесь, возьмите свежий "
            "список, выберите другой. Я обновляю список каждый час.\n\n"
            "<b>Если файл не открывается</b>\n"
            "Сначала нужно установить приложение — нажмите "
            "<b>📲 Скачать приложение</b>."
        ),
        "app": (
            "📲 <b>Nimku Proxy для Android</b>\n\n"
            "Бесплатно. Без подписки, без рекламы, без слежки, без регистрации.\n\n"
            "<b>1.</b> Скачать: {url}\n"
            "<b>2.</b> Откройте скачанный файл\n"
            "<b>3.</b> Android предупредит — нажмите <b>Настройки</b>, разрешите "
            "установку из этого источника, затем <b>Установить</b>\n\n"
            "Для Xiaomi, Huawei и Samsung нужны дополнительные шаги — они "
            "описаны здесь, вместе с проверкой файла перед установкой:\n{readme}"
        ),
        "age_just_now": "только что",
        "age_minutes": "{n} мин назад",
        "age_hours": "{n} ч назад",
    },

    # ─────────────────────────── فارسی ───────────────────────────
    "fa": {
        "choose_language": "🌐 زبان خود را انتخاب کنید:",
        "welcome": (
            "👋 <b>Nimku Proxy</b>\n\n"
            "من پروکسی‌های تلگرام می‌دهم که واقعاً کار می‌کنند.\n\n"
            "اگر تلگرام فیلتر یا کند است، پروکسی آن را حل می‌کند.\n\n"
            "<b>سه مرحله:</b>\n"
            "1️⃣ روی <b>📥 دریافت فهرست</b> بزنید — یک فایل می‌فرستم\n"
            "2️⃣ آن فایل را با برنامهٔ <b>Nimku Proxy</b> باز کنید\n"
            "3️⃣ برنامه سالم‌ها را پیدا می‌کند — روی یکی بزنید تا وصل شوید\n\n"
            "برنامه را ندارید؟ اول <b>📲 دریافت برنامه</b> را بزنید."
        ),
        "menu_get": "📥 دریافت فهرست",
        "menu_app": "📲 دریافت برنامه",
        "menu_help": "❓ راهنما",
        "menu_language": "🌐 زبان",
        "menu_back": "⬅️ بازگشت به منو",
        "btn_again": "🔄 فهرست تازه",
        "btn_noapp": "📲 برنامه را ندارم",
        "preparing": "در حال ارسال فهرست…",
        "not_ready": (
            "فهرست هنوز در حال ساخته‌شدن است — چند دقیقه طول می‌کشد. "
            "کمی بعد دوباره تلاش کنید."
        ),
        "file_caption": (
            "📥 <b>{count} پروکسی</b> · بروزرسانی {age}\n\n"
            "<b>حالا این کار را بکنید:</b>\n"
            "1️⃣ روی فایل بالا بزنید ☝️\n"
            "2️⃣ گزینهٔ <b>باز کردن با ← Nimku Proxy</b> را بزنید\n"
            "3️⃣ صبر کنید تا برنامه آن‌ها را آزمایش کند\n"
            "4️⃣ روی یک پروکسی سالم بزنید تا وصل شوید"
        ),
        "file_caption_verified": (
            "📥 <b>{count} پروکسی</b> · بروزرسانی {age}\n"
            "✅ {confirmed} مورد همین حالا تأیید شد\n\n"
            "<b>حالا این کار را بکنید:</b>\n"
            "1️⃣ روی فایل بالا بزنید ☝️\n"
            "2️⃣ گزینهٔ <b>باز کردن با ← Nimku Proxy</b> را بزنید\n"
            "3️⃣ صبر کنید تا برنامه آن‌ها را آزمایش کند\n"
            "4️⃣ روی یک پروکسی سالم بزنید تا وصل شوید"
        ),
        "help": (
            "❓ <b>نحوهٔ استفاده</b>\n\n"
            "<b>پروکسی چیست؟</b>\n"
            "کامپیوتری در کشوری دیگر که ترافیک تلگرام شما را عبور می‌دهد تا "
            "تلگرام حتی در جایی که فیلتر است وصل شود. فقط روی تلگرام اثر "
            "دارد — مرورگر و بقیهٔ برنامه‌ها دست‌نخورده می‌مانند.\n\n"
            "<b>مرحله به مرحله</b>\n"
            "1️⃣ روی <b>📥 دریافت فهرست</b> بزنید — فایل همین‌جا می‌آید\n"
            "2️⃣ روی آن فایل بزنید\n"
            "3️⃣ گزینهٔ <b>باز کردن با ← Nimku Proxy</b> را بزنید\n"
            "4️⃣ برنامه همه را آزمایش می‌کند و سالم‌ها را، سریع‌ترین در بالا، "
            "نشان می‌دهد\n"
            "5️⃣ روی یکی بزنید — تلگرام تأیید می‌خواهد — قبول کنید\n\n"
            "<b>اگر از کار افتاد</b>\n"
            "پروکسی‌ها زیاد از کار می‌افتند، طبیعی است. برگردید، فهرست تازه "
            "بگیرید، یکی دیگر انتخاب کنید. من هر ساعت فهرست را نو می‌کنم.\n\n"
            "<b>اگر فایل باز نمی‌شود</b>\n"
            "اول باید برنامه نصب باشد — <b>📲 دریافت برنامه</b> را بزنید."
        ),
        "app": (
            "📲 <b>Nimku Proxy برای اندروید</b>\n\n"
            "رایگان. بدون اشتراک، بدون تبلیغات، بدون ردیابی، بدون ثبت‌نام.\n\n"
            "<b>۱.</b> دانلود: {url}\n"
            "<b>۲.</b> فایل دانلودشده را باز کنید\n"
            "<b>۳.</b> اندروید هشدار می‌دهد — روی <b>تنظیمات</b> بزنید، اجازهٔ "
            "نصب از این منبع را بدهید، بعد <b>نصب</b>\n\n"
            "شیائومی، هواوی و سامسونگ مرحله‌های اضافه دارند — اینجا آمده، همراه "
            "با روش بررسی سالم بودن فایل پیش از نصب:\n{readme}"
        ),
        "age_just_now": "هم‌اکنون",
        "age_minutes": "{n} دقیقه پیش",
        "age_hours": "{n} ساعت پیش",
    },

    # ─────────────────────────── العربية ───────────────────────────
    "ar": {
        "choose_language": "🌐 اختر لغتك:",
        "welcome": (
            "👋 <b>Nimku Proxy</b>\n\n"
            "أعطيك بروكسيات تيليجرام تعمل فعلاً.\n\n"
            "إذا كان تيليجرام محجوباً أو بطيئاً عندك، البروكسي يحل ذلك.\n\n"
            "<b>ثلاث خطوات:</b>\n"
            "1️⃣ اضغط <b>📥 احصل على القائمة</b> — سأرسل لك ملفاً\n"
            "2️⃣ افتح الملف بتطبيق <b>Nimku Proxy</b>\n"
            "3️⃣ التطبيق يجد ما يعمل عندك — اضغط على واحد للاتصال\n\n"
            "ليس لديك التطبيق؟ اضغط <b>📲 حمّل التطبيق</b> أولاً."
        ),
        "menu_get": "📥 احصل على القائمة",
        "menu_app": "📲 حمّل التطبيق",
        "menu_help": "❓ طريقة الاستخدام",
        "menu_language": "🌐 اللغة",
        "menu_back": "⬅️ رجوع للقائمة",
        "btn_again": "🔄 قائمة جديدة",
        "btn_noapp": "📲 ليس لدي التطبيق",
        "preparing": "جارٍ إرسال القائمة…",
        "not_ready": (
            "القائمة قيد الإعداد — تستغرق بضع دقائق. حاول بعد قليل."
        ),
        "file_caption": (
            "📥 <b>{count} بروكسي</b> · تم التحديث {age}\n\n"
            "<b>الآن افعل هذا:</b>\n"
            "1️⃣ اضغط على الملف أعلاه ☝️\n"
            "2️⃣ اختر <b>فتح بواسطة ← Nimku Proxy</b>\n"
            "3️⃣ انتظر حتى يفحصها التطبيق\n"
            "4️⃣ اضغط على بروكسي يعمل للاتصال"
        ),
        "file_caption_verified": (
            "📥 <b>{count} بروكسي</b> · تم التحديث {age}\n"
            "✅ {confirmed} تم التأكد من عملها الآن\n\n"
            "<b>الآن افعل هذا:</b>\n"
            "1️⃣ اضغط على الملف أعلاه ☝️\n"
            "2️⃣ اختر <b>فتح بواسطة ← Nimku Proxy</b>\n"
            "3️⃣ انتظر حتى يفحصها التطبيق\n"
            "4️⃣ اضغط على بروكسي يعمل للاتصال"
        ),
        "help": (
            "❓ <b>طريقة الاستخدام</b>\n\n"
            "<b>ما هو البروكسي؟</b>\n"
            "جهاز في بلد آخر ينقل بيانات تيليجرام الخاصة بك، فيتصل تيليجرام حتى "
            "حيث يكون محجوباً. يؤثر على تيليجرام فقط — لا على المتصفح أو باقي "
            "التطبيقات.\n\n"
            "<b>خطوة بخطوة</b>\n"
            "1️⃣ اضغط <b>📥 احصل على القائمة</b> — سيصل ملف هنا\n"
            "2️⃣ اضغط على الملف\n"
            "3️⃣ اختر <b>فتح بواسطة ← Nimku Proxy</b>\n"
            "4️⃣ التطبيق يفحص كل بروكسي ويعرض العاملة، الأسرع أولاً\n"
            "5️⃣ اضغط على واحد — تيليجرام سيطلب التأكيد — وافق\n\n"
            "<b>إذا توقف عن العمل</b>\n"
            "البروكسيات تتعطل كثيراً، هذا طبيعي. عد واحصل على قائمة جديدة "
            "واختر غيره. أحدّث القائمة كل ساعة.\n\n"
            "<b>إذا لم يُفتح الملف</b>\n"
            "تحتاج لتثبيت التطبيق أولاً — اضغط <b>📲 حمّل التطبيق</b>."
        ),
        "app": (
            "📲 <b>Nimku Proxy لأندرويد</b>\n\n"
            "مجاني. بلا اشتراك، بلا إعلانات، بلا تتبع، بلا تسجيل.\n\n"
            "<b>1.</b> التحميل: {url}\n"
            "<b>2.</b> افتح الملف بعد تحميله\n"
            "<b>3.</b> سيحذرك أندرويد — اضغط <b>الإعدادات</b>، اسمح بالتثبيت من "
            "هذا المصدر، ثم <b>تثبيت</b>\n\n"
            "أجهزة شاومي وهواوي وسامسونج تحتاج خطوات إضافية — مذكورة هنا مع "
            "طريقة التأكد من سلامة الملف قبل التثبيت:\n{readme}"
        ),
        "age_just_now": "الآن",
        "age_minutes": "قبل {n} دقيقة",
        "age_hours": "قبل {n} ساعة",
    },

    # ─────────────────────────── Українська ───────────────────────────
    "uk": {
        "choose_language": "🌐 Оберіть мову:",
        "welcome": (
            "👋 <b>Nimku Proxy</b>\n\n"
            "Я даю проксі для Телеграм, які справді працюють.\n\n"
            "Якщо Телеграм заблоковано або він гальмує — проксі це виправляє.\n\n"
            "<b>Три кроки:</b>\n"
            "1️⃣ Натисніть <b>📥 Отримати список</b> — надішлю файл\n"
            "2️⃣ Відкрийте цей файл застосунком <b>Nimku Proxy</b>\n"
            "3️⃣ Застосунок знайде робочі — натисніть на будь-який\n\n"
            "Немає застосунку? Спершу натисніть <b>📲 Завантажити застосунок</b>."
        ),
        "menu_get": "📥 Отримати список",
        "menu_app": "📲 Завантажити застосунок",
        "menu_help": "❓ Як користуватись",
        "menu_language": "🌐 Мова",
        "menu_back": "⬅️ До меню",
        "btn_again": "🔄 Свіжий список",
        "btn_noapp": "📲 У мене немає застосунку",
        "preparing": "Надсилаю список…",
        "not_ready": (
            "Список ще формується — це займе кілька хвилин. "
            "Спробуйте трохи пізніше."
        ),
        "file_caption": (
            "📥 <b>{count} проксі</b> · оновлено {age}\n\n"
            "<b>Тепер зробіть так:</b>\n"
            "1️⃣ Натисніть на файл вище ☝️\n"
            "2️⃣ Оберіть <b>Відкрити за допомогою → Nimku Proxy</b>\n"
            "3️⃣ Зачекайте, поки застосунок їх перевірить\n"
            "4️⃣ Натисніть на робочий проксі, щоб підключитись"
        ),
        "file_caption_verified": (
            "📥 <b>{count} проксі</b> · оновлено {age}\n"
            "✅ {confirmed} щойно перевірено — працюють\n\n"
            "<b>Тепер зробіть так:</b>\n"
            "1️⃣ Натисніть на файл вище ☝️\n"
            "2️⃣ Оберіть <b>Відкрити за допомогою → Nimku Proxy</b>\n"
            "3️⃣ Зачекайте, поки застосунок їх перевірить\n"
            "4️⃣ Натисніть на робочий проксі, щоб підключитись"
        ),
        "help": (
            "❓ <b>Як цим користуватись</b>\n\n"
            "<b>Що таке проксі?</b>\n"
            "Комп'ютер в іншій країні, який передає ваш трафік Телеграм, щоб "
            "месенджер працював навіть там, де його заблоковано. Впливає лише "
            "на Телеграм — браузер та інші застосунки не зачіпає.\n\n"
            "<b>Покроково</b>\n"
            "1️⃣ Натисніть <b>📥 Отримати список</b> — сюди прийде файл\n"
            "2️⃣ Натисніть на цей файл\n"
            "3️⃣ Оберіть <b>Відкрити за допомогою → Nimku Proxy</b>\n"
            "4️⃣ Застосунок перевірить усі та покаже робочі, найшвидші згори\n"
            "5️⃣ Натисніть на будь-який — Телеграм спитає підтвердження — "
            "погодьтесь\n\n"
            "<b>Якщо перестав працювати</b>\n"
            "Проксі часто вмирають, це нормально. Поверніться, візьміть свіжий "
            "список, оберіть інший. Я оновлюю список щогодини.\n\n"
            "<b>Якщо файл не відкривається</b>\n"
            "Спершу треба встановити застосунок — натисніть "
            "<b>📲 Завантажити застосунок</b>."
        ),
        "app": (
            "📲 <b>Nimku Proxy для Android</b>\n\n"
            "Безкоштовно. Без підписки, без реклами, без стеження, без реєстрації.\n\n"
            "<b>1.</b> Завантажити: {url}\n"
            "<b>2.</b> Відкрийте завантажений файл\n"
            "<b>3.</b> Android попередить — натисніть <b>Налаштування</b>, "
            "дозвольте встановлення з цього джерела, потім <b>Встановити</b>\n\n"
            "Для Xiaomi, Huawei та Samsung потрібні додаткові кроки — вони "
            "описані тут, разом із перевіркою файлу перед встановленням:\n{readme}"
        ),
        "age_just_now": "щойно",
        "age_minutes": "{n} хв тому",
        "age_hours": "{n} год тому",
    },

    # ─────────────────────────── Türkçe ───────────────────────────
    "tr": {
        "choose_language": "🌐 Dilinizi seçin:",
        "welcome": (
            "👋 <b>Nimku Proxy</b>\n\n"
            "Size gerçekten çalışan Telegram proxy'leri veriyorum.\n\n"
            "Telegram engelliyse veya yavaşsa, proxy bunu çözer.\n\n"
            "<b>Üç adım:</b>\n"
            "1️⃣ <b>📥 Proxy listesi al</b>'a basın — size bir dosya gönderirim\n"
            "2️⃣ Dosyayı <b>Nimku Proxy</b> uygulamasıyla açın\n"
            "3️⃣ Uygulama çalışanları bulur — birine dokunup bağlanın\n\n"
            "Uygulamanız yok mu? Önce <b>📲 Uygulamayı indir</b>'e basın."
        ),
        "menu_get": "📥 Proxy listesi al",
        "menu_app": "📲 Uygulamayı indir",
        "menu_help": "❓ Nasıl kullanılır",
        "menu_language": "🌐 Dil",
        "menu_back": "⬅️ Menüye dön",
        "btn_again": "🔄 Yeni liste al",
        "btn_noapp": "📲 Uygulamam yok",
        "preparing": "Liste gönderiliyor…",
        "not_ready": (
            "Liste hâlâ hazırlanıyor — birkaç dakika sürer. "
            "Lütfen biraz sonra tekrar deneyin."
        ),
        "file_caption": (
            "📥 <b>{count} proxy</b> · güncellendi {age}\n\n"
            "<b>Şimdi şunu yapın:</b>\n"
            "1️⃣ Yukarıdaki dosyaya dokunun ☝️\n"
            "2️⃣ <b>Birlikte aç → Nimku Proxy</b>'yi seçin\n"
            "3️⃣ Uygulama test ederken bekleyin\n"
            "4️⃣ Çalışan bir proxy'ye dokunup bağlanın"
        ),
        "file_caption_verified": (
            "📥 <b>{count} proxy</b> · güncellendi {age}\n"
            "✅ {confirmed} tanesi az önce doğrulandı\n\n"
            "<b>Şimdi şunu yapın:</b>\n"
            "1️⃣ Yukarıdaki dosyaya dokunun ☝️\n"
            "2️⃣ <b>Birlikte aç → Nimku Proxy</b>'yi seçin\n"
            "3️⃣ Uygulama test ederken bekleyin\n"
            "4️⃣ Çalışan bir proxy'ye dokunup bağlanın"
        ),
        "help": (
            "❓ <b>Nasıl kullanılır</b>\n\n"
            "<b>Proxy nedir?</b>\n"
            "Başka bir ülkedeki, Telegram trafiğinizi taşıyan bir bilgisayar; "
            "böylece Telegram engellenen yerlerde bile bağlanır. Sadece "
            "Telegram'ı etkiler — tarayıcınızı veya diğer uygulamaları değil.\n\n"
            "<b>Adım adım</b>\n"
            "1️⃣ <b>📥 Proxy listesi al</b>'a basın — buraya bir dosya gelir\n"
            "2️⃣ O dosyaya dokunun\n"
            "3️⃣ <b>Birlikte aç → Nimku Proxy</b>'yi seçin\n"
            "4️⃣ Uygulama hepsini test eder, çalışanları en hızlıdan başlayarak "
            "gösterir\n"
            "5️⃣ Birine dokunun — Telegram onay ister — kabul edin\n\n"
            "<b>Çalışmayı bırakırsa</b>\n"
            "Proxy'ler sık ölür, bu normaldir. Geri gelin, yeni liste alın, "
            "başka birini seçin. Listeyi her saat yeniliyorum.\n\n"
            "<b>Dosya açılmıyorsa</b>\n"
            "Önce uygulamayı kurmanız gerekir — <b>📲 Uygulamayı indir</b>'e basın."
        ),
        "app": (
            "📲 <b>Android için Nimku Proxy</b>\n\n"
            "Ücretsiz. Abonelik yok, reklam yok, takip yok, kayıt yok.\n\n"
            "<b>1.</b> İndir: {url}\n"
            "<b>2.</b> İndirilen dosyayı açın\n"
            "<b>3.</b> Android uyarı verir — <b>Ayarlar</b>'a dokunun, bu "
            "kaynaktan kuruluma izin verin, sonra <b>Yükle</b>\n\n"
            "Xiaomi, Huawei ve Samsung ek adımlar ister — kurulumdan önce "
            "dosyanın güvenli olduğunu doğrulama yöntemiyle birlikte "
            "burada:\n{readme}"
        ),
        "age_just_now": "az önce",
        "age_minutes": "{n} dk önce",
        "age_hours": "{n} sa önce",
    },

    # ─────────────────────────── 中文 ───────────────────────────
    "zh": {
        "choose_language": "🌐 选择您的语言：",
        "welcome": (
            "👋 <b>Nimku Proxy</b>\n\n"
            "我提供真正可用的 Telegram 代理。\n\n"
            "如果 Telegram 被封锁或很慢，代理可以解决。\n\n"
            "<b>三个步骤：</b>\n"
            "1️⃣ 点击 <b>📥 获取代理列表</b> — 我会发给您一个文件\n"
            "2️⃣ 用 <b>Nimku Proxy</b> 应用打开该文件\n"
            "3️⃣ 应用会找出可用的 — 点一个即可连接\n\n"
            "还没有应用？请先点 <b>📲 下载应用</b>。"
        ),
        "menu_get": "📥 获取代理列表",
        "menu_app": "📲 下载应用",
        "menu_help": "❓ 使用方法",
        "menu_language": "🌐 语言",
        "menu_back": "⬅️ 返回菜单",
        "btn_again": "🔄 获取新列表",
        "btn_noapp": "📲 我还没有应用",
        "preparing": "正在发送列表…",
        "not_ready": "列表仍在生成中 — 需要几分钟。请稍后再试。",
        "file_caption": (
            "📥 <b>{count} 个代理</b> · 更新于 {age}\n\n"
            "<b>现在这样做：</b>\n"
            "1️⃣ 点击上方文件 ☝️\n"
            "2️⃣ 选择 <b>打开方式 → Nimku Proxy</b>\n"
            "3️⃣ 等待应用测试它们\n"
            "4️⃣ 点击一个可用的代理连接"
        ),
        "file_caption_verified": (
            "📥 <b>{count} 个代理</b> · 更新于 {age}\n"
            "✅ 其中 {confirmed} 个刚刚验证可用\n\n"
            "<b>现在这样做：</b>\n"
            "1️⃣ 点击上方文件 ☝️\n"
            "2️⃣ 选择 <b>打开方式 → Nimku Proxy</b>\n"
            "3️⃣ 等待应用测试它们\n"
            "4️⃣ 点击一个可用的代理连接"
        ),
        "help": (
            "❓ <b>使用方法</b>\n\n"
            "<b>什么是代理？</b>\n"
            "位于其他国家的一台计算机，替您转发 Telegram 流量，"
            "让 Telegram 在被封锁的地方也能连接。只影响 Telegram — "
            "不影响浏览器和其他应用。\n\n"
            "<b>分步操作</b>\n"
            "1️⃣ 点击 <b>📥 获取代理列表</b> — 文件会发到这里\n"
            "2️⃣ 点击该文件\n"
            "3️⃣ 选择 <b>打开方式 → Nimku Proxy</b>\n"
            "4️⃣ 应用测试全部代理，按速度从快到慢显示可用的\n"
            "5️⃣ 点击一个 — Telegram 会请求确认 — 同意即可\n\n"
            "<b>如果不能用了</b>\n"
            "代理经常失效，这很正常。回来获取新列表，换一个即可。"
            "我每小时更新一次列表。\n\n"
            "<b>如果文件打不开</b>\n"
            "需要先安装应用 — 点击 <b>📲 下载应用</b>。"
        ),
        "app": (
            "📲 <b>Nimku Proxy 安卓版</b>\n\n"
            "免费。无订阅、无广告、无跟踪、无需注册。\n\n"
            "<b>1.</b> 下载：{url}\n"
            "<b>2.</b> 打开下载的文件\n"
            "<b>3.</b> 安卓会提示警告 — 点 <b>设置</b>，允许从此来源安装，"
            "然后点 <b>安装</b>\n\n"
            "小米、华为和三星需要额外步骤 — 详见此处，"
            "同时说明如何在安装前验证文件安全：\n{readme}"
        ),
        "age_just_now": "刚刚",
        "age_minutes": "{n} 分钟前",
        "age_hours": "{n} 小时前",
    },
}

APK_URL = "https://github.com/Nimku/Mtproxy-finder-app/releases/latest/download/NimkuProxy.apk"
README_URL = "https://github.com/Nimku/Mtproxy-finder-app#installing-the-apk"


def t(lang: str, key: str, **kwargs) -> str:
    """Falls back to English for any string a language hasn't translated yet, so
    adding a half-finished language never leaves a user staring at a raw key."""
    table = TEXT.get(lang) or TEXT[DEFAULT_LANGUAGE]
    value = table.get(key) or TEXT[DEFAULT_LANGUAGE].get(key, key)
    return value.format(**kwargs) if kwargs else value


def age_text(lang: str, minutes: int) -> str:
    if minutes < 2:
        return t(lang, "age_just_now")
    if minutes < 60:
        return t(lang, "age_minutes", n=minutes)
    return t(lang, "age_hours", n=minutes // 60)


def match_language(code: str | None) -> str | None:
    """Maps a Telegram language_code to one we support. Handles regional forms
    like zh-Hans / pt-BR by taking the base tag."""
    if not code:
        return None
    base = code.replace("_", "-").split("-")[0].lower()
    return base if base in LANGUAGES else None
