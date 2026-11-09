package pl.gieoerzet.teklapelletcan

/** Urządzenie, z którym rozmawia aplikacja: prawdziwe (HTTP w sieci) albo wirtualne (tryb demo, rdzeń firmware przez JNI). */
interface Backend {
    val key: String          // stabilny klucz do pamięci podręcznej
    val isDemo: Boolean
    /** Zwraca null, gdy urządzenie jest nieosiągalne (brak połączenia/limit czasu). */
    fun request(method: String, pathQuery: String, authorization: String, body: ByteArray): DemoHost.Reply?
}

class HttpBackend(private val base: String) : Backend {
    override val key = "d_" + base.replace(Regex("[^A-Za-z0-9]"), "_")
    override val isDemo = false

    override fun request(method: String, pathQuery: String, authorization: String, body: ByteArray): DemoHost.Reply? {
        var c: java.net.HttpURLConnection? = null
        return try {
            c = (java.net.URL(base.trimEnd('/') + pathQuery).openConnection() as java.net.HttpURLConnection).apply {
                connectTimeout = 2500; readTimeout = 6000; instanceFollowRedirects = false; useCaches = false
                requestMethod = method
                if (authorization.isNotEmpty()) setRequestProperty("Authorization", authorization)
                if (method == "POST" || method == "DELETE") {
                    doOutput = body.isNotEmpty()
                    setRequestProperty("Content-Type", "application/json")
                    if (body.isNotEmpty()) outputStream.use { it.write(body) }
                }
            }
            val st = c.responseCode
            val stream = if (st >= 400) c.errorStream else c.inputStream
            val data = stream?.use { it.readBytes() } ?: ByteArray(0)
            DemoHost.Reply(st, c.contentType ?: "application/json", c.getHeaderField("Content-Disposition") ?: "", data)
        } catch (e: Exception) {
            null
        } finally {
            c?.disconnect()
        }
    }
}

class DemoBackend(private val host: DemoHost) : Backend {
    override val key = "demo"
    override val isDemo = true
    override fun request(method: String, pathQuery: String, authorization: String, body: ByteArray): DemoHost.Reply? {
        val q = pathQuery.indexOf('?')
        return host.request(method, if (q < 0) pathQuery else pathQuery.substring(0, q), if (q < 0) "" else pathQuery.substring(q + 1), authorization, body)
    }
}
