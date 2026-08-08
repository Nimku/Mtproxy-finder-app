package com.nimku.mtproxyfinder.domain.source

import com.nimku.mtproxyfinder.domain.model.RawProxyEntry
import com.nimku.mtproxyfinder.domain.model.SourceKind
import okhttp3.OkHttpClient

interface ProxySource {
    val id: String
    val displayName: String
    val kind: SourceKind
    val enabledByDefault: Boolean
        get() = true

    suspend fun fetch(client: OkHttpClient): List<RawProxyEntry>
}

