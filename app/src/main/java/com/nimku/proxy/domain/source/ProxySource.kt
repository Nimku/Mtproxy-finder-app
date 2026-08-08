package com.nimku.proxy.domain.source

import com.nimku.proxy.domain.model.RawProxyEntry
import com.nimku.proxy.domain.model.SourceKind
import okhttp3.OkHttpClient

interface ProxySource {
    val id: String
    val displayName: String
    val kind: SourceKind
    val enabledByDefault: Boolean
        get() = true

    suspend fun fetch(client: OkHttpClient): List<RawProxyEntry>
}

