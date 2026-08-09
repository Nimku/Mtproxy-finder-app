package com.nimku.proxy.updater

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.provider.Settings
import androidx.core.content.FileProvider
import com.nimku.proxy.BuildConfig
import com.nimku.proxy.core.util.readUtf8Bounded
import java.io.File
import java.io.FileOutputStream
import java.security.MessageDigest
import java.util.concurrent.TimeUnit
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request

/** Downloads an APK from this project's GitHub Releases and verifies it before install. */
class ApkDownloader(
    private val context: Context,
    private val client: OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(120, TimeUnit.SECONDS)
        .callTimeout(150, TimeUnit.SECONDS)
        .followRedirects(true)
        .build()
) {
    companion object {
        private const val MIN_APK_BYTES = 100_000L
        private const val MAX_APK_BYTES = 100L * 1024 * 1024
        private val SHA256_REGEX = Regex("(?i)(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")
    }

    suspend fun download(
        release: GitHubRelease,
        fileName: String = "NimkuProxy-update.apk",
        onProgress: (percent: Int) -> Unit = {}
    ): File = withContext(Dispatchers.IO) {
        validateRelease(release)
        val expectedDigest = release.sha256 ?: release.sha256Url?.let(::downloadDigest)
            ?: throw IllegalStateException("Release has no SHA-256 for the APK")

        val dir = File(context.cacheDir, "updates").apply { mkdirs() }
        dir.listFiles()?.forEach(File::delete)
        val outFile = File(dir, sanitizeFileName(fileName))

        try {
            val request = Request.Builder()
                .url(release.apkUrl)
                .header("User-Agent", "NimkuProxy-Android-Updater/${BuildConfig.VERSION_NAME}")
                .header("Accept", "application/vnd.android.package-archive,application/octet-stream")
                .build()

            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) error("Download failed: HTTP ${response.code}")
                val body = response.body ?: error("Empty response")
                val total = body.contentLength()
                require(total < 0 || total in MIN_APK_BYTES..MAX_APK_BYTES) { "Invalid APK size" }
                if (release.apkSize > 0 && total > 0) {
                    require(total == release.apkSize) { "APK size does not match the release" }
                }

                var read = 0L
                body.byteStream().use { input ->
                    FileOutputStream(outFile).use { output ->
                        val buffer = ByteArray(32 * 1024)
                        while (true) {
                            val count = input.read(buffer)
                            if (count < 0) break
                            read += count
                            require(read <= MAX_APK_BYTES) { "APK is too large" }
                            output.write(buffer, 0, count)
                            if (total > 0) {
                                val percent = ((read * 100) / total).toInt().coerceIn(0, 99)
                                withContext(Dispatchers.Main) { onProgress(percent) }
                            }
                        }
                    }
                }
            }

            require(outFile.length() in MIN_APK_BYTES..MAX_APK_BYTES) { "APK is corrupted or has the wrong size" }
            if (release.apkSize > 0) require(outFile.length() == release.apkSize) { "APK size changed during download" }
            require(sha256(outFile).equals(expectedDigest, ignoreCase = true)) { "APK SHA-256 does not match" }
            verifyPackageAndSigner(outFile, release.tagName)
            withContext(Dispatchers.Main) { onProgress(100) }
            outFile
        } catch (error: Exception) {
            outFile.delete()
            throw error
        }
    }

    /**
     * GitHub serves asset URLs using the repository's canonical casing (e.g.
     * "Nimku/Mtproxy-finder-app"), which won't necessarily match how GITHUB_REPO is written in
     * the build config. Host and repo path are case-insensitive for this purpose, so compare
     * that way — a case-sensitive check here rejects our own official release URL and makes every
     * in-app update fail before a single byte is requested. Must stay in sync with
     * UpdateChecker.isExpectedReleaseAssetUrl(), which already ignores case.
     */
    private fun isOfficialReleaseAssetUrl(url: String): Boolean =
        url.startsWith("https://github.com/${BuildConfig.GITHUB_REPO}/releases/download/", ignoreCase = true)

    private fun validateRelease(release: GitHubRelease) {
        require(isOfficialReleaseAssetUrl(release.apkUrl)) {
            "APK must come from the official GitHub Releases"
        }
        require(release.apkName.startsWith("NimkuProxy-", true) && release.apkName.endsWith(".apk", true)) {
            "Unexpected APK name"
        }
        require(release.apkSize < 0 || release.apkSize in MIN_APK_BYTES..MAX_APK_BYTES) { "Invalid APK size" }
    }

    private fun downloadDigest(url: String): String {
        require(isOfficialReleaseAssetUrl(url)) {
            "SHA-256 must come from the official release"
        }
        val request = Request.Builder().url(url).header("User-Agent", "NimkuProxy-Updater").build()
        return client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) error("Could not download SHA-256")
            val body = response.body ?: error("Empty SHA-256")
            require(body.contentLength() < 0 || body.contentLength() <= 1_024) { "SHA-256 file is too large" }
            val text = body.source().readUtf8Bounded(1_024)
            SHA256_REGEX.find(text)?.value ?: error("Invalid SHA-256")
        }
    }

    @Suppress("DEPRECATION")
    private fun verifyPackageAndSigner(file: File, expectedVersion: String) {
        val flags = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            PackageManager.GET_SIGNING_CERTIFICATES
        } else PackageManager.GET_SIGNATURES
        val archive = context.packageManager.getPackageArchiveInfo(file.absolutePath, flags)
            ?: error("File is not an APK")
        require(archive.packageName == context.packageName) { "Wrong package name" }
        val archiveVersion = archive.versionName.orEmpty().removePrefix("v")
        require(archiveVersion == expectedVersion.removePrefix("v")) { "APK version does not match the release" }

        val installed = context.packageManager.getPackageInfo(context.packageName, flags)
        val archiveCerts = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            archive.signingInfo?.apkContentsSigners?.map { sha256(it.toByteArray()) }.orEmpty()
        } else archive.signatures?.map { sha256(it.toByteArray()) }.orEmpty()
        val installedCerts = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            installed.signingInfo?.apkContentsSigners?.map { sha256(it.toByteArray()) }.orEmpty()
        } else installed.signatures?.map { sha256(it.toByteArray()) }.orEmpty()
        require(archiveCerts.isNotEmpty() && archiveCerts.any(installedCerts::contains)) {
            "APK is signed with a different certificate"
        }
    }

    private fun sanitizeFileName(value: String): String =
        value.replace(Regex("[^A-Za-z0-9._-]"), "_").take(120).ifBlank { "NimkuProxy-update.apk" }

    private fun sha256(file: File): String {
        val digest = MessageDigest.getInstance("SHA-256")
        file.inputStream().use { input ->
            val buffer = ByteArray(32 * 1024)
            while (true) {
                val read = input.read(buffer)
                if (read < 0) break
                digest.update(buffer, 0, read)
            }
        }
        return digest.digest().joinToString("") { "%02x".format(it) }
    }

    private fun sha256(bytes: ByteArray): String =
        MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }

    fun canInstallPackages(): Boolean =
        Build.VERSION.SDK_INT < Build.VERSION_CODES.O || context.packageManager.canRequestPackageInstalls()

    fun isVerifiedUpdateFile(apkFile: File?): Boolean =
        apkFile != null &&
            apkFile.isFile &&
            apkFile.canonicalFile.parentFile == File(context.cacheDir, "updates").canonicalFile &&
            apkFile.length() in MIN_APK_BYTES..MAX_APK_BYTES

    fun openInstallPermissionSettings(activity: Activity) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            activity.startActivity(
                Intent(
                    Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                    Uri.parse("package:${context.packageName}")
                )
            )
        }
    }

    fun installApk(activity: Activity, apkFile: File) {
        require(isVerifiedUpdateFile(apkFile)) { "Update APK is unavailable" }
        val uri = FileProvider.getUriForFile(context, "${context.packageName}.fileprovider", apkFile)
        activity.startActivity(
            Intent(Intent.ACTION_VIEW).apply {
                setDataAndType(uri, "application/vnd.android.package-archive")
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
        )
    }
}

