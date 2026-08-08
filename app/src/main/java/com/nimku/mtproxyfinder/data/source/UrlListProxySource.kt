package com.nimku.mtproxyfinder.data.source

import com.nimku.mtproxyfinder.data.remote.HttpSupport
import com.nimku.mtproxyfinder.domain.model.RawProxyEntry
import com.nimku.mtproxyfinder.domain.model.SourceKind
import com.nimku.mtproxyfinder.domain.parser.ProxyParser
import com.nimku.mtproxyfinder.domain.source.ProxySource
import okhttp3.OkHttpClient

class UrlListProxySource(
    override val id: String,
    override val displayName: String,
    private val urls: List<String>,
    override val kind: SourceKind = SourceKind.GITHUB_RAW,
    override val enabledByDefault: Boolean = true
) : ProxySource {

    override suspend fun fetch(client: OkHttpClient): List<RawProxyEntry> {
        val downloaded = HttpSupport.downloadWithRetry(
            client = client,
            urls = urls,
            enforceSafeUrl = kind == SourceKind.USER_CUSTOM
        ) ?: return emptyList()
        return ProxyParser.parse(downloaded.first, id, displayName)
    }
}

