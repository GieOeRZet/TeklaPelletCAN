package pl.gieoerzet.teklapelletcan

import java.net.HttpURLConnection
import java.net.URL

/** Proste zapytania HTTP do urządzenia w sieci lokalnej (status, pobieranie plików). */
object Http {
    class Result(val status: Int, val body: ByteArray, val disposition: String, val ctype: String)

    fun get(url: String, timeoutMs: Int = 2500): Result? {
        var c: HttpURLConnection? = null
        return try {
            c = (URL(url).openConnection() as HttpURLConnection).apply {
                connectTimeout = timeoutMs
                readTimeout = timeoutMs
                instanceFollowRedirects = false
                useCaches = false
            }
            val st = c.responseCode
            val stream = if (st >= 400) c.errorStream else c.inputStream
            val data = stream?.use { it.readBytes() } ?: ByteArray(0)
            Result(st, data, c.getHeaderField("Content-Disposition") ?: "", c.contentType ?: "")
        } catch (e: Exception) {
            null
        } finally {
            c?.disconnect()
        }
    }
}
