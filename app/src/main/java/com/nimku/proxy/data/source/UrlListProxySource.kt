package com.nimku.proxy.data.source

import com.nimku.proxy.data.remote.HttpSupport
import com.nimku.proxy.domain.model.RawProxyEntry
import com.nimku.proxy.domain.model.SourceKind
import com.nimku.proxy.domain.parser.ProxyParser
import com.nimku.proxy.domain.source.ProxySource
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

