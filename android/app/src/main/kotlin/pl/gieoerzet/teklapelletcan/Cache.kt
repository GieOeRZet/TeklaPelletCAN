package pl.gieoerzet.teklapelletcan

import java.io.File

/** Pamięć ostatnich odczytów urządzenia (stany, informacje, opis punktów) – pokazywana, gdy urządzenie jest poza zasięgiem. */
class Cache(private val dir: File, private val clock: () -> Long = { System.currentTimeMillis() }) {
    class Entry(val body: String, val ctype: String, val at: Long)

    init { dir.mkdirs() }

    private fun key(device: String, path: String) = File(dir, (device + path).replace(Regex("[^A-Za-z0-9._-]"), "_"))

    fun put(device: String, path: String, body: String, ctype: String) {
        try { key(device, path).writeText("${clock()}\n$ctype\n$body") } catch (e: Exception) { /* brak miejsca – bez cache */ }
    }

    fun get(device: String, path: String): Entry? {
        val f = key(device, path)
        if (!f.exists()) return null
        return try {
            val t = f.readText()
            val a = t.indexOf('\n'); val b = t.indexOf('\n', a + 1)
            Entry(t.substring(b + 1), t.substring(a + 1, b), t.substring(0, a).toLong())
        } catch (e: Exception) { null }
    }

    fun clear() { dir.listFiles()?.forEach { it.delete() } }
}
