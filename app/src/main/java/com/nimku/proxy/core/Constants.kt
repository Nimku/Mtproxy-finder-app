package com.nimku.proxy.core

object Constants {
    const val TELEGRAM_CHANNEL_USERNAME = "SetProxy"

    /** Your subscription bot, e.g. "NimkuBot" (no leading @). Used for the paywall deep link. */
    const val TELEGRAM_BOT_USERNAME = "Nimkuproxybot"
    const val TELEGRAM_CHANNEL_URL = "https://t.me/$TELEGRAM_CHANNEL_USERNAME"
    const val TELEGRAM_CHANNEL_DEEP_LINK = "tg://resolve?domain=$TELEGRAM_CHANNEL_USERNAME"
    const val TELEGRAM_CHANNEL_PREVIEW = "https://t.me/s/$TELEGRAM_CHANNEL_USERNAME"

    /** Параллелизм источников в мега-скане. */
    const val AGGREGATOR_PARALLELISM = 6
    /** Таймаут на один источник (tg_mega сам режет внутренние таймауты). */
    const val SOURCE_TIMEOUT_MS = 45_000L
    const val CHECK_PARALLELISM = 20

    /**
     * Source whose first [PRIORITY_SOURCE_COUNT] entries get checked and shown first, ahead of
     * every other result, in their original relative order (failures are skipped, not shown).
     */
    const val PRIORITY_SOURCE_ID = "dubblebyte"
    const val PRIORITY_SOURCE_COUNT = 20

    // --- Subscription / license gate (see license/LicenseManager.kt) ---

    /** Repo + path the license status file is mirrored to by bot/bot.py. */
    const val LICENSE_REPO_OWNER = "nimku"
    const val LICENSE_REPO_NAME = "mtproxy-finder-app"
    const val LICENSE_REPO_REF = "main"
    const val LICENSE_STATUS_PATH = "license/status.json"

    /**
     * Reserved subscriptions{} key the bot writes when the admin turns on "free mode" from the
     * in-Telegram admin panel. If this key is present and unexpired, every user is treated as
     * subscribed regardless of their own hash — no app update needed to go free (or back to paid).
     */
    const val LICENSE_FREE_FOR_ALL_KEY = "__free_for_all__"

    /**
     * Salt mixed into the locally-entered Telegram user ID before hashing (see
     * LicenseManager.hashTelegramId). MUST exactly match HASH_SALT in bot/bot.py, or every
     * check will report "not subscribed" even for a paying user. Not a secret: it only makes
     * the public license/status.json harder to casually reverse into a raw user-ID list, it does
     * not gate write access (that's the bot's private GitHub token, which never ships here).
     * TODO: change this to your own random string before release, and keep it in sync with the bot.
     */
    const val LICENSE_HASH_SALT = "mtpf-v1-change-this-salt"

    /** Subscription length granted per successful payment; must match bot/bot.py. */
    const val LICENSE_PERIOD_DAYS = 30

    /**
     * How long the app keeps treating a subscription as active after the last successful
     * "you're active" check, if it can't reach GitHub/CDN mirrors at all (e.g. mid-flight,
     * temporary block). Does NOT apply once a check succeeds and reports expired/missing.
     */
    const val LICENSE_OFFLINE_GRACE_DAYS = 3

    val GITHUB_CDN_TEMPLATES = listOf(
        "https://cdn.jsdelivr.net/gh/{owner}/{repo}@{ref}/{path}",
        "https://fastly.jsdelivr.net/gh/{owner}/{repo}@{ref}/{path}",
        "https://gcore.jsdelivr.net/gh/{owner}/{repo}@{ref}/{path}",
        "https://raw.githack.com/{owner}/{repo}/{ref}/{path}",
        "https://rawcdn.githack.com/{owner}/{repo}/{ref}/{path}",
        "https://ghproxy.net/https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}",
        "https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}"
    )
}

