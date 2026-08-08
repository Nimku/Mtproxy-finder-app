package com.nimku.proxy

import java.io.Serializable

enum class ProxyStatus : Serializable {
    /** Как в Telegram: прокси реально отвечает MTProto */
    AVAILABLE,
    /** TCP есть, но MTProto/secret не прошёл */
    UNAVAILABLE
}

data class ProxyWithPing(
    val url: String,
    val pingMs: Int,
    val profileLabel: String = "",
    val status: ProxyStatus = ProxyStatus.AVAILABLE,
    val statusText: String = "Доступен",
    /**
     * Position among the priority-source pre-pass (0 = first checked), or [Int.MAX_VALUE] for a
     * regular result. Priority results always sort above regular ones and keep their relative
     * order; regular results are sorted by ping as before. See ProxyManager.checkPriorityDubblebyte.
     */
    val priorityRank: Int = Int.MAX_VALUE
) : Serializable

data class ProxyInfo(
    val server: String,
    val port: String
)

data class FetchResult(
    val proxies: List<String>,
    val sourceHits: Map<String, Int>,
    val usedMirrors: List<String>,
    val fromCache: Boolean = false,
    val fromSeed: Boolean = false
)

