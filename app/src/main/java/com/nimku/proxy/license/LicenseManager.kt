package com.nimku.proxy.license

import android.content.Context
import com.nimku.proxy.core.Constants
import com.nimku.proxy.data.remote.HttpSupport
import java.security.MessageDigest
import java.time.Instant
import java.time.format.DateTimeParseException
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import org.json.JSONObject

/**
 * Subscription gate. The app never talks to the bot or the VPS directly — the bot writes
 * license/status.json into this GitHub repo after a Telegram Stars payment, and this object
 * only ever reads that file (through the same GitHub/CDN mirrors the proxy sources use, so it
 * keeps working where raw.githubusercontent.com itself is blocked). See bot/bot.py and
 * README.md for the full flow.
 */
object LicenseManager {

    enum class State { NOT_LINKED, ACTIVE, EXPIRED, OFFLINE_GRACE }

    data class Result(
        val state: State,
        val expiresAt: Instant?,
        /** True if the app should let the user keep using proxy scanning right now. */
        val usable: Boolean,
    )

    private const val PREFS_NAME = "mtpf_license"
    private const val KEY_TELEGRAM_ID = "telegram_id"
    private const val KEY_LAST_ACTIVE_AT = "last_active_at_ms"
    private const val KEY_LAST_EXPIRY = "last_expiry_iso"

    private val client: OkHttpClient by lazy { HttpSupport.fastClient() }

    private fun prefs(context: Context) =
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun savedTelegramId(context: Context): String? =
        prefs(context).getString(KEY_TELEGRAM_ID, null)?.takeIf { it.isNotBlank() }

    fun isValidTelegramId(id: String): Boolean = id.trim().let { it.length in 5..15 && it.all(Char::isDigit) }

    /** Links a new Telegram ID locally. Any previous cached expiry is cleared — must re-check. */
    fun linkTelegramId(context: Context, id: String) {
        val trimmed = id.trim()
        require(isValidTelegramId(trimmed)) { "Invalid Telegram user ID" }
        prefs(context)
            .edit()
            .putString(KEY_TELEGRAM_ID, trimmed)
            .remove(KEY_LAST_ACTIVE_AT)
            .remove(KEY_LAST_EXPIRY)
            .apply()
    }

    fun unlink(context: Context) {
        prefs(context).edit().clear().apply()
    }

    /** SHA-256(salt + telegramId), hex-encoded. Must match bot/bot.py's hash_user_id(). */
    fun hashTelegramId(id: String): String {
        val digest = MessageDigest.getInstance("SHA-256")
        val bytes = digest.digest((Constants.LICENSE_HASH_SALT + id.trim()).toByteArray(Charsets.UTF_8))
        return bytes.joinToString("") { "%02x".format(it) }
    }

    /**
     * Fast, local, no network. Used to decide instantly whether to show the app or the paywall
     * while [refresh] runs in the background to catch an expiry that happened since last check.
     */
    fun cachedResult(context: Context): Result {
        val id = savedTelegramId(context) ?: return Result(State.NOT_LINKED, null, usable = false)
        val p = prefs(context)
        val lastActiveAt = p.getLong(KEY_LAST_ACTIVE_AT, 0L)
        val lastExpiry = p.getString(KEY_LAST_EXPIRY, null)?.let(::parseInstantOrNull)
        val now = Instant.now()

        if (lastExpiry != null && now.isBefore(lastExpiry)) {
            return Result(State.ACTIVE, lastExpiry, usable = true)
        }
        if (lastActiveAt > 0) {
            val graceUntil = Instant.ofEpochMilli(lastActiveAt)
                .plusSeconds(Constants.LICENSE_OFFLINE_GRACE_DAYS * 24L * 3600L)
            if (now.isBefore(graceUntil)) {
                return Result(State.OFFLINE_GRACE, lastExpiry, usable = true)
            }
        }
        return Result(State.EXPIRED, lastExpiry, usable = false)
    }

    /**
     * Authoritative check: fetches license/status.json, looks up this device's hashed Telegram
     * ID, and persists the outcome. A network failure never downgrades a still-in-grace cached
     * result to EXPIRED — only a successful fetch that explicitly finds no active entry does.
     */
    suspend fun refresh(context: Context): Result = withContext(Dispatchers.IO) {
        val id = savedTelegramId(context) ?: return@withContext Result(State.NOT_LINKED, null, usable = false)
        val hash = hashTelegramId(id)

        val urls = HttpSupport.freshnessCriticalUrls(
            Constants.LICENSE_REPO_OWNER,
            Constants.LICENSE_REPO_NAME,
            Constants.LICENSE_REPO_REF,
            Constants.LICENSE_STATUS_PATH,
        )
        val downloaded = try {
            HttpSupport.downloadWithRetry(
                client,
                urls,
                minUsefulBytes = 2,
                headers = mapOf("Cache-Control" to "no-cache", "Pragma" to "no-cache"),
            )
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (_: Exception) {
            null
        }

        if (downloaded == null) {
            // Couldn't reach any mirror — keep whatever cachedResult() already reflects.
            return@withContext cachedResult(context)
        }

        val expiry = try {
            val root = JSONObject(downloaded.first)
            val subscriptions = root.optJSONObject("subscriptions")
            val personal = subscriptions?.optString(hash, null)?.let(::parseInstantOrNull)
            val freeForAll = subscriptions
                ?.optString(Constants.LICENSE_FREE_FOR_ALL_KEY, null)
                ?.let(::parseInstantOrNull)
            listOfNotNull(personal, freeForAll).maxOrNull()
        } catch (_: Exception) {
            null
        }

        val now = Instant.now()
        val p = prefs(context)
        if (expiry != null && now.isBefore(expiry)) {
            p.edit()
                .putLong(KEY_LAST_ACTIVE_AT, now.toEpochMilli())
                .putString(KEY_LAST_EXPIRY, expiry.toString())
                .apply()
            return@withContext Result(State.ACTIVE, expiry, usable = true)
        }

        // Authoritative "not active" — clear grace eligibility.
        p.edit().remove(KEY_LAST_ACTIVE_AT).apply()
        Result(State.EXPIRED, expiry, usable = false)
    }

    private fun parseInstantOrNull(raw: String): Instant? = try {
        Instant.parse(raw)
    } catch (_: DateTimeParseException) {
        null
    }
}
