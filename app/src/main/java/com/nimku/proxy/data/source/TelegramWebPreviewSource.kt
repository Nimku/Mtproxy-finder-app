package com.nimku.proxy.data.source

import com.nimku.proxy.data.remote.HttpSupport
import com.nimku.proxy.data.remote.TelegramBypass
import com.nimku.proxy.domain.model.RawProxyEntry
import com.nimku.proxy.domain.model.SourceKind
import com.nimku.proxy.domain.parser.ProxyParser
import com.nimku.proxy.domain.source.ProxySource
import okhttp3.OkHttpClient

/**
 * Один публичный TG-канал через **параллельный race** зеркал (не последовательный обход).
 * Для мега-скана предпочтительнее [TelegramMegaSource].
 */
class TelegramWebPreviewSource(
    private val channelUsername: String,
    override val displayName: String = "TG @$channelUsername",
    override val enabledByDefault: Boolean = false
) : ProxySource {

    override val id: String = "tg_$channelUsername"
    override val kind: SourceKind = SourceKind.TELEGRAM_CHANNEL

    override suspend fun fetch(client: OkHttpClient): List<RawProxyEntry> {
        val fast = HttpSupport.fastClient()
        val urls = TelegramBypass.channelFastUrls(channelUsername)
        val raced = HttpSupport.downloadRace(
            client = fast,
            urls = urls,
            headers = TelegramBypass.browserHeaders(),
            minUsefulBytes = 80,
            perUrlTimeoutMs = 6_500L,
            overallTimeoutMs = 10_000L
        ) ?: return emptyList()

        val body = TelegramMegaSource.normalizeBody(raced.first)
        val parsed = ProxyParser.parse(body, id, displayName)
        if (parsed.isNotEmpty()) return parsed
        return ProxyParser.parse(body, id, displayName)
    }
}

