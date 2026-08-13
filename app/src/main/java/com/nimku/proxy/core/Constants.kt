package com.nimku.proxy.core

object Constants {
    const val TELEGRAM_CHANNEL_USERNAME = "SetProxy"

    /**
     * The channel's companion bot (no leading @). The app is free and never asks it for a
     * licence — the bot's job is to hand out freshly scraped proxy list files for regions where
     * GitHub itself is unreachable (see ImportProxyFile in README.md).
     */
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

