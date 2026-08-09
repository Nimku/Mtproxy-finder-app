package com.nimku.proxy.core.util

import java.io.IOException
import okio.BufferedSource

/**
 * Reads a stream in full, rejecting responses larger than [maxBytes].
 *
 * IMPORTANT: okio's `readByteArray(byteCount)` is an EXACT read — it throws `EOFException` when
 * the stream holds fewer than `byteCount` bytes. Using it as a "limit" breaks every normal
 * (small) response: a 3 KB release JSON against a 512 KB limit used to fail with EOFException,
 * which is exactly why update checks stopped working in earlier builds.
 *
 * So the limit is tested with [BufferedSource.request], which returns `false` when fewer bytes
 * are available, and only then is the whole response read.
 */
@Throws(IOException::class)
fun BufferedSource.readAllBounded(maxBytes: Long): ByteArray {
    require(maxBytes > 0) { "maxBytes must be positive" }
    // request() returns true only when STRICTLY more than the limit is available — too large.
    if (request(maxBytes + 1)) throw IOException("Response is too large (> $maxBytes bytes)")
    return readByteArray()
}

/** Same, but returns the result directly as a UTF-8 string. */
@Throws(IOException::class)
fun BufferedSource.readUtf8Bounded(maxBytes: Long): String =
    readAllBounded(maxBytes).toString(Charsets.UTF_8)
