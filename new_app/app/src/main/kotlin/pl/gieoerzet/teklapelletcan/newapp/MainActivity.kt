package pl.gieoerzet.teklapelletcan.newapp

import android.annotation.SuppressLint
import android.app.Activity
import android.os.Bundle
import android.webkit.JavascriptInterface
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import kotlin.concurrent.thread

class MainActivity : Activity() {
    private lateinit var web: WebView
    private val prefs by lazy { getSharedPreferences("newapp", MODE_PRIVATE) }
    private var selectedBase: String? = prefs.getString("base", null)
    private var selectedName: String? = prefs.getString("name", null)

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        web = WebView(this).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.allowFileAccess = true
            settings.allowContentAccess = true
            webViewClient = object : WebViewClient() {
                override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest) = false
                override fun onPageFinished(view: WebView, url: String) {
                    if (!prefs.getBoolean("real_module", false)) {
                        view.evaluateJavascript("window.TPC_DEMO=true; location.hash='#/d/pulpit';", null)
                    }
                }
            }
            addJavascriptInterface(Bridge(), "TPCNative")
        }
        setContentView(web)
        web.loadUrl("file:///android_asset/index.html")
    }

    override fun onBackPressed() {
        web.evaluateJavascript("window.__tpcBack ? window.__tpcBack() : false") { value ->
            if (value != "true") super@MainActivity.onBackPressed()
        }
    }

    inner class Bridge {
        private fun result(id: String, status: Int, body: String) {
            val p = JSONObject().apply {
                put("status", status); put("body", body); put("cachedAt", 0); put("ctype", "application/json")
            }
            web.post { web.evaluateJavascript("window.__tpcResp(" + JSONObject.quote(id) + "," + JSONObject.quote(p.toString()) + ")", null) }
        }

        @JavascriptInterface fun state(): String = JSONObject().apply {
            val real = prefs.getBoolean("real_module", false)
            put("version", "0.3.0"); put("demo", !real)
            put("deviceName", selectedName ?: if (real) "" else "DEMO")
            put("web", false); put("bioAvailable", false); put("locked", false)
        }.toString()
        @JavascriptInterface fun getDevices() = "[]"
        @JavascriptInterface fun saveDevices(json: String) {}
        @JavascriptInterface fun startDiscovery() {}
        @JavascriptInterface fun stopDiscovery() {}
        @JavascriptInterface fun deselect() { selectedBase = null; selectedName = null }
        @JavascriptInterface fun selectDevice(base: String, name: String) {
            selectedBase = base; selectedName = name
            prefs.edit().putBoolean("real_module", base != "demo://").putString("base", base).putString("name", name).apply()
        }
        @JavascriptInterface fun ping(id: String, base: String) = true
        @JavascriptInterface fun setupPin(pin: String) = JSONObject().put("ok", true).toString()
        @JavascriptInterface fun changePin(a: String, b: String) = JSONObject().put("ok", true).toString()
        @JavascriptInterface fun unlockPin(pin: String) = JSONObject().put("ok", true).toString()
        @JavascriptInterface fun unlockBio() = false
        @JavascriptInterface fun lock() {}
        @JavascriptInterface fun setBio(on: Boolean) {}
        @JavascriptInterface fun setLockOnStart(on: Boolean) {}
        @JavascriptInterface fun clearCache() {}
        @JavascriptInterface fun resetSecurity() {}
        @JavascriptInterface fun openOriginal() {}
        @JavascriptInterface fun openDeviceSettings(dev: Boolean = false) {}
        @JavascriptInterface fun openSetup() {}
        @JavascriptInterface fun openExternalUrl(url: String) {}
        @JavascriptInterface fun deviceSummary(base: String) = "{}"

        @JavascriptInterface fun request(id: String, method: String, path: String, body: String) {
            val base = selectedBase
            if (base != null && base != "demo://" && path.startsWith("/api/")) {
                thread { requestReal(id, method, path, body, base) }
            } else result(id, 200, demoResponse(path).toString())
        }

        private fun requestReal(id: String, method: String, path: String, body: String, base: String) {
            try {
                val c = URL(base.trimEnd('/') + path).openConnection() as HttpURLConnection
                c.requestMethod = method; c.connectTimeout = 2500; c.readTimeout = 3500
                c.setRequestProperty("Content-Type", "application/json")
                if (method != "GET") { c.doOutput = true; c.outputStream.use { it.write(body.toByteArray()) } }
                val code = c.responseCode
                val text = (if (code in 200..399) c.inputStream else c.errorStream)?.bufferedReader()?.readText() ?: "{}"
                result(id, code, text)
            } catch (_: Exception) { result(id, 0, "{}") }
        }

        private fun state(id: String, value: String, unit: String = "") = JSONObject().apply {
            put("entity_id", id); put("state", value); put("id", id.substringAfter("tekla_"))
            put("attributes", JSONObject().apply { if (unit.isNotEmpty()) put("unit_of_measurement", unit) })
        }

        private fun demoResponse(path: String): JSONObject {
            if (path.contains("/api/v1/info")) return JSONObject().apply { put("fw", "DEMO"); put("model", "TeklaPelletCAN"); put("features", JSONArray(listOf("time"))) }
            if (path.contains("/api/v1/config")) return JSONObject().put("boiler_image", 11)
            if (path.contains("/api/v1/points")) return JSONObject().put("points", JSONArray())
            if (path.contains("/api/v1/states")) {
                val a = JSONArray()
                fun s(id:String,v:String,u:String="") { a.put(state(id,v,u)) }
                s("sensor.tekla_kociol_temperatura","64.8","°C"); s("sensor.tekla_kociol_zadana_wynikowa","60","°C")
                s("sensor.tekla_temperatura_powrotu","41.9","°C"); s("sensor.tekla_temperatura_zewnetrzna","-3.0","°C")
                s("sensor.tekla_palnik_stan","Wyłączony"); s("sensor.tekla_moc_palnika","0","%"); s("sensor.tekla_palnik_moc","0","kW"); s("sensor.tekla_temperatura_palnika","47","°C")
                s("sensor.tekla_cwu_temperatura","53.9","°C"); s("sensor.tekla_cwu_zadana_wynikowa","55","°C")
                s("sensor.tekla_co_temperatura","49.8","°C"); s("sensor.tekla_co_zadana_wynikowa","45","°C")
                s("sensor.tekla_zbiornik_paliwo","28","kg"); s("sensor.tekla_zbiornik_pojemnosc","135","kg"); s("sensor.tekla_zbiornik_zapelnienie","21","%"); s("sensor.tekla_paliwo_prognoza","3","dni")
                s("binary_sensor.tekla_kociol_wlaczony","on"); s("binary_sensor.tekla_cwu_pompa","on"); s("binary_sensor.tekla_co_pompa","on"); s("binary_sensor.tekla_can_ok","on")
                s("binary_sensor.tekla_dmuchawa_pracuje","off"); s("binary_sensor.tekla_podajnik_pracuje","off"); s("binary_sensor.tekla_podajnik_palnika_pracuje","off"); s("binary_sensor.tekla_alarm_aktywny","off")
                s("sensor.tekla_ostatni_alarm","Brak"); s("sensor.tekla_kociol_tryb_pracy","Auto"); s("sensor.tekla_mieszacz_co1_stan","0"); s("sensor.tekla_poziom_dostepu","0")
                return JSONObject().put("states", a)
            }
            return JSONObject()
        }
    }
}
