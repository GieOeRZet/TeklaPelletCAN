package pl.gieoerzet.teklapelletcan.newapp

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import kotlin.math.roundToInt

data class PelletDevice(
    val id: String,
    var name: String,
    var baseUrl: String,
    var firmware: String = "",
    var bleAddress: String = "",
    var online: Boolean = false
)

data class PelletState(
    val values: Map<String, String> = emptyMap(),
    val attrs: Map<String, Map<String, String>> = emptyMap(),
    val raw: JSONObject = JSONObject()
) {
    fun v(id: String): String? = values[id] ?: attrs.values.firstNotNullOfOrNull { it[id] }
    fun num(id: String): Double? = v(id)?.replace(',', '.')?.toDoubleOrNull()
    fun fuzzy(vararg parts: String): String? {
        val k = values.keys.firstOrNull { key -> parts.all { key.contains(it, true) } }
        return k?.let { values[it] }
    }
}

object PelletApi {
    data class Result(val status: Int, val body: String)
    fun request(base: String, method: String, path: String, body: String? = null): Result? {
        return try {
            val c = (URL(base.trimEnd('/') + path).openConnection() as HttpURLConnection).apply {
                connectTimeout = 2500
                readTimeout = 4500
                requestMethod = method
                useCaches = false
                instanceFollowRedirects = false
                setRequestProperty("Accept", "application/json")
                if (body != null) {
                    doOutput = true
                    setRequestProperty("Content-Type", "application/json")
                    outputStream.use { it.write(body.toByteArray()) }
                }
            }
            val code = c.responseCode
            val stream = if (code >= 400) c.errorStream else c.inputStream
            val text = stream?.bufferedReader()?.use { it.readText() } ?: ""
            c.disconnect()
            Result(code, text)
        } catch (_: Throwable) { null }
    }

    fun info(base: String): JSONObject? = request(base, "GET", "/api/v1/info")?.let {
        if (it.status in 200..299) runCatching { JSONObject(it.body) }.getOrNull() else null
    }

    fun states(base: String): PelletState? {
        val r = request(base, "GET", "/api/v1/states") ?: return null
        if (r.status !in 200..299) return null
        return runCatching {
            val root = JSONObject(r.body)
            val arr = root.optJSONArray("states") ?: JSONArray()
            val values = mutableMapOf<String, String>()
            val attrs = mutableMapOf<String, Map<String, String>>()
            for (i in 0 until arr.length()) {
                val s = arr.optJSONObject(i) ?: continue
                val id = s.optString("entity_id")
                if (id.isBlank()) continue
                values[id] = s.optString("state")
                val a = s.optJSONObject("attributes")
                if (a != null) {
                    val m = mutableMapOf<String, String>()
                    a.keys().forEach { k -> m[k] = a.optString(k) }
                    attrs[id] = m
                }
            }
            PelletState(values, attrs, root)
        }.getOrNull()
    }

    fun points(base: String): JSONObject? = request(base, "GET", "/api/v1/points")?.let {
        if (it.status in 200..299) runCatching { JSONObject(it.body) }.getOrNull() else null
    }

    fun call(base: String, service: String, data: JSONObject = JSONObject()): Boolean {
        val body = JSONObject()
            .put("domain", "teklapelletcan")
            .put("service", service)
            .put("data", data)
        val r = request(base, "POST", "/api/v1/call", body.toString())
        return r?.status in 200..299
    }
}

class DeviceStore(ctx: Context) {
    private val prefs = ctx.getSharedPreferences("new_app_devices", Context.MODE_PRIVATE)
    fun load(): MutableList<PelletDevice> = runCatching {
        val a = JSONArray(prefs.getString("devices", "[]"))
        MutableList(a.length()) { i ->
            val o = a.getJSONObject(i)
            PelletDevice(o.optString("id"), o.optString("name"), o.optString("baseUrl"),
                o.optString("firmware"), o.optString("bleAddress"))
        }
    }.getOrElse { mutableListOf() }

    fun save(devices: List<PelletDevice>) {
        val a = JSONArray()
        devices.forEach { d ->
            a.put(JSONObject().put("id", d.id).put("name", d.name).put("baseUrl", d.baseUrl)
                .put("firmware", d.firmware).put("bleAddress", d.bleAddress))
        }
        prefs.edit().putString("devices", a.toString()).apply()
    }
}
