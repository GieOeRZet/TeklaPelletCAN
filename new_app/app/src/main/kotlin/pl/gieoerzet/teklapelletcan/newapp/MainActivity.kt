package pl.gieoerzet.teklapelletcan.newapp

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
import java.util.concurrent.Executors

class MainActivity : Activity() {
    private lateinit var web: WebView
    private val io = Executors.newCachedThreadPool()
    private val prefs by lazy { getSharedPreferences("new_app", MODE_PRIVATE) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        web = WebView(this).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.allowFileAccess = false
            settings.allowContentAccess = false
            webViewClient = object : WebViewClient() {
                override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest) = false
            }
            addJavascriptInterface(Bridge(), "TPC")
        }
        setContentView(web)
        web.loadUrl("file:///android_asset/index.html")
    }

    override fun onDestroy() {
        io.shutdownNow()
        web.destroy()
        super.onDestroy()
    }

    inner class Bridge {
        @JavascriptInterface fun devices(): String = prefs.getString("devices", "[]") ?: "[]"

        @JavascriptInterface fun saveDevices(json: String) {
            try { JSONArray(json); prefs.edit().putString("devices", json).apply() } catch (_: Throwable) {}
        }

        @JavascriptInterface fun ping(id: String, base: String) {
            io.execute {
                val result = runCatching {
                    val c = (URL(base.trimEnd('/') + "/api/v1/info").openConnection() as HttpURLConnection).apply {
                        connectTimeout = 2500
                        readTimeout = 2500
                        requestMethod = "GET"
                    }
                    val body = c.inputStream.bufferedReader().use { it.readText() }
                    JSONObject().put("ok", c.responseCode in 200..299).put("status", c.responseCode).put("body", body)
                }.getOrElse {
                    JSONObject().put("ok", false).put("error", it.message ?: "connection error")
                }
                runOnUiThread {
                    val js = "window.nativePing && window.nativePing(" + JSONObject.quote(id) + ", " + result + ")"
                    web.evaluateJavascript(js, null)
                }
            }
        }

        @JavascriptInterface fun version(): String = "0.1.0-newapp"
    }
}
