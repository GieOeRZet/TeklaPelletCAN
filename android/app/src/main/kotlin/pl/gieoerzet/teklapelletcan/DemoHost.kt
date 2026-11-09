package pl.gieoerzet.teklapelletcan

/** Tryb DEMO: wirtualne urządzenie TeklaPelletCAN działające w procesie aplikacji (bez sieci i bez kotła). */
class DemoHost(fw: String) {
    class Reply(val status: Int, val ctype: String, val disposition: String, val body: ByteArray)

    private val handle: Long = Native.create(fw)
    @Volatile private var running = true
    private val ticker = Thread({
        while (running) {
            Native.tick(handle)
            try { Thread.sleep(5) } catch (e: InterruptedException) { break }
        }
    }, "tpc-demo-tick").apply { isDaemon = true; start() }

    fun request(method: String, path: String, query: String, authorization: String, body: ByteArray): Reply {
        val raw = Native.handle(handle, method, path, query, authorization, body)
        // nagłówek: trzy linie tekstu, dalej ciało (dowolne bajty)
        var pos = 0
        val lines = ArrayList<String>(3)
        for (i in 0 until 3) {
            var end = pos
            while (end < raw.size && raw[end] != '\n'.code.toByte()) end++
            lines.add(String(raw, pos, end - pos, Charsets.UTF_8))
            pos = end + 1
        }
        val status = lines[0].toIntOrNull() ?: 500
        val bodyBytes = if (pos <= raw.size) raw.copyOfRange(minOf(pos, raw.size), raw.size) else ByteArray(0)
        return Reply(status, lines[1], lines[2], bodyBytes)
    }

    fun close() {
        running = false
        ticker.interrupt()
        try { ticker.join(500) } catch (e: InterruptedException) { /* ignoruj */ }
        Native.destroy(handle)
    }
}
