package pl.gieoerzet.teklapelletcan

import org.json.JSONObject

/**
 * Jedyna droga interfejsu do urządzenia. Egzekwuje blokadę zapisu, dokleja token urządzenia, a przy braku połączenia
 * oddaje ostatnie zapamiętane odczyty (z godziną), żeby interfejs mógł je pokazać z wyraźnym oznaczeniem.
 */
class Proxy(
    private val backend: Backend,
    private val gate: WriteGate,
    private val cache: Cache,
    private val tokens: KV,
    private val clock: () -> Long = { System.currentTimeMillis() },
) {
    class Out(val status: Int, val ctype: String, val body: String, val cachedAt: Long = 0, val disposition: String = "")

    private val cacheable = setOf("/api/v1/states", "/api/v1/info", "/api/v1/points", "/api/v1/config")
    private var lastStatesSave = 0L

    private fun tokenKey() = "token_" + backend.key

    fun handle(method: String, pathQuery: String, body: String): Out {
        val path = pathQuery.substringBefore('?')
        if (!gate.isUnlocked() && !WriteGate.allowedWhenLocked(method, path, body)) {
            return Out(403, "application/json", "{\"ok\":false,\"error\":\"app_locked\"}")
        }
        val tok = tokens.getString(tokenKey()) ?: ""
        val r = backend.request(method, pathQuery, if (tok.isNotEmpty()) "Bearer $tok" else "", body.toByteArray(Charsets.UTF_8))
        if (r == null) {
            if (method == "GET" && path in cacheable) {
                val c = cache.get(backend.key, path)
                if (c != null) return Out(200, c.ctype, c.body, c.at)
            }
            return Out(503, "application/json", "{\"ok\":false,\"error\":\"offline\"}")
        }
        val text = String(r.body, Charsets.UTF_8)
        if (method == "GET" && r.status == 200 && path in cacheable) {
            val now = clock()
            if (path != "/api/v1/states" || now - lastStatesSave > 3000) {
                if (path == "/api/v1/states") lastStatesSave = now
                cache.put(backend.key, path, text, r.ctype)
            }
        }
        if (path == "/api/v1/pair" && r.status == 200) {
            try { tokens.putString(tokenKey(), JSONObject(text).optString("token")) } catch (e: Exception) { /* ignoruj */ }
        }
        return Out(r.status, r.ctype, text, 0, r.disposition)
    }

    /** Zdejmuje poziom dostępu kotła (PIN 0 = zły PIN), gdy aplikacja się blokuje – poziom jest wspólny dla wszystkich klientów. */
    fun dropBoilerLevel() {
        val tok = tokens.getString(tokenKey()) ?: ""
        backend.request("POST", "/api/v1/call", if (tok.isNotEmpty()) "Bearer $tok" else "",
            "{\"domain\":\"teklapelletcan\",\"service\":\"tekla_estyma_unlock\",\"data\":{\"pin\":0}}".toByteArray())
    }
}
