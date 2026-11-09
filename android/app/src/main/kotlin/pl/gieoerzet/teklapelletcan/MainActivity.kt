package pl.gieoerzet.teklapelletcan

import android.app.Activity
import android.app.AlertDialog
import android.content.ContentValues
import android.content.Context
import android.content.Intent
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import android.net.NetworkRequest
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.os.Handler
import android.os.Looper
import android.provider.MediaStore
import android.util.TypedValue
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.view.WindowInsets
import android.webkit.ConsoleMessage
import android.webkit.JavascriptInterface
import android.webkit.JsPromptResult
import android.webkit.JsResult
import android.webkit.URLUtil
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import org.json.JSONObject
import java.io.ByteArrayInputStream
import java.util.concurrent.Executors

/**
 * Aplikacja = powłoka (lista urządzeń, wyszukiwanie, tryb demo) + widok urządzenia.
 * Widok urządzenia to ta sama strona, którą serwuje urządzenie (pełna karta, ustawienia, aktualizacja),
 * więc aplikacja zawsze pokazuje to, co wersja firmware w danym urządzeniu.
 * Tryb demo serwuje te same strony z paczki aplikacji, a API obsługuje wirtualne urządzenie z rdzenia firmware (JNI).
 */
class MainActivity : Activity() {
    companion object {
        const val SHELL_HOST = "app.tpc"
        const val DEMO_HOST = "demo.tpc"
        const val SETUP_URL = "http://10.77.77.1/"
        const val REQ_FILE = 71
    }

    private lateinit var shell: WebView
    private lateinit var device: WebView
    private lateinit var deviceBox: LinearLayout
    private lateinit var titleView: TextView
    private lateinit var demoBadge: TextView
    private lateinit var root: FrameLayout
    private val ui = Handler(Looper.getMainLooper())
    private val io = Executors.newCachedThreadPool()
    private lateinit var store: Store
    private var discovery: Discovery? = null
    private var demo: DemoHost? = null
    private var fileCallback: ValueCallback<Array<Uri>>? = null
    private var clearHistoryAfterBlank = false
    private var demoFetchJs: String = ""
    private var netCallback: ConnectivityManager.NetworkCallback? = null
    private var currentBase = ""

    // ------------------------------------------------------------------ cykl życia

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        store = Store(this)
        demoFetchJs = try { assets.open("app/demo-fetch.js").bufferedReader().use { it.readText() } } catch (e: Exception) { "" }

        shell = makeWebView(local = true)
        shell.addJavascriptInterface(ShellBridge(), "TPC")

        device = makeWebView(local = false)
        device.addJavascriptInterface(DemoBridge(), "TPCDemo")
        device.addJavascriptInterface(AppBridge(), "TPCApp")

        titleView = TextView(this).apply {
            setTextColor(0xFFE8EAF0.toInt()); textSize = 16f; maxLines = 1
            layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
        }
        demoBadge = TextView(this).apply {
            text = "DEMO"; setTextColor(0xFF1A1208.toInt()); setBackgroundColor(0xFFFF7A1A.toInt()); textSize = 11f
            setPadding(dp(6), dp(2), dp(6), dp(2)); visibility = View.GONE
        }
        val bar = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL
            setBackgroundColor(0xFF1C1F27.toInt()); setPadding(dp(4), 0, dp(4), 0)
            addView(barButton("←") { goBack(force = true) })
            addView(titleView)
            addView(demoBadge)
            addView(barButton("⚙") { device.loadUrl(currentBase + "settings.html") })
            addView(barButton("⟳") { device.reload() })
        }
        deviceBox = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL; visibility = View.GONE
            addView(bar, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(48)))
            addView(device, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f))
        }
        root = FrameLayout(this).apply {
            setBackgroundColor(0xFF111318.toInt())
            addView(shell, FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
            addView(deviceBox, FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
            setOnApplyWindowInsetsListener { v, ins -> applyInsets(v, ins); ins }
        }
        setContentView(root)
        shell.loadUrl("https://$SHELL_HOST/")
        bindToWifi()
    }

    override fun onDestroy() {
        discovery?.stop()
        demo?.close(); demo = null
        netCallback?.let { try { (getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager).unregisterNetworkCallback(it) } catch (e: Exception) { /* ignoruj */ } }
        io.shutdownNow()
        super.onDestroy()
    }

    override fun onPause() { super.onPause(); discovery?.stop() }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() { goBack(force = false) }

    @Deprecated("Deprecated in Java")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        if (requestCode == REQ_FILE) {
            fileCallback?.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(resultCode, data))
            fileCallback = null
        } else {
            @Suppress("DEPRECATION")
            super.onActivityResult(requestCode, resultCode, data)
        }
    }

    // ------------------------------------------------------------------ pomocnicze UI

    private fun dp(v: Int) = TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, v.toFloat(), resources.displayMetrics).toInt()

    private fun barButton(label: String, action: () -> Unit) = TextView(this).apply {
        text = label; setTextColor(0xFFE8EAF0.toInt()); textSize = 20f; gravity = Gravity.CENTER
        minWidth = dp(44); minHeight = dp(44)
        layoutParams = LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.MATCH_PARENT)
        setOnClickListener { action() }
    }

    private fun applyInsets(v: View, ins: WindowInsets) {
        if (Build.VERSION.SDK_INT >= 30) {
            val s = ins.getInsets(WindowInsets.Type.systemBars())
            val k = ins.getInsets(WindowInsets.Type.ime())
            v.setPadding(s.left, s.top, s.right, maxOf(s.bottom, k.bottom))
        } else {
            @Suppress("DEPRECATION")
            v.setPadding(ins.systemWindowInsetLeft, ins.systemWindowInsetTop, ins.systemWindowInsetRight, ins.systemWindowInsetBottom)
        }
    }

    private fun toast(t: String) = ui.post { Toast.makeText(this, t, Toast.LENGTH_LONG).show() }

    private fun goBack(force: Boolean) {
        if (deviceBox.visibility == View.VISIBLE) {
            if (!force && device.canGoBack() && device.url != "about:blank") { device.goBack(); return }
            closeDevice()
        } else if (shell.canGoBack()) {
            shell.goBack()
        } else {
            finish()
        }
    }

    private fun closeDevice() {
        deviceBox.visibility = View.GONE
        shell.visibility = View.VISIBLE
        clearHistoryAfterBlank = true
        device.loadUrl("about:blank")                 // zatrzymuje odpytywanie i animacje strony
        demo?.close(); demo = null
        shell.evaluateJavascript("window.tpcReturned&&window.tpcReturned()", null)
    }

    private fun showDevice(base: String, name: String, isDemo: Boolean) {
        currentBase = base
        titleView.text = name
        demoBadge.visibility = if (isDemo) View.VISIBLE else View.GONE
        if (isDemo && demo == null) {
            val v = try { packageManager.getPackageInfo(packageName, 0).versionName ?: "demo" } catch (e: Exception) { "demo" }
            demo = DemoHost("$v-demo")
        }
        shell.visibility = View.GONE
        deviceBox.visibility = View.VISIBLE
        device.loadUrl(base)
    }

    // ------------------------------------------------------------------ sieć

    /** Przy włączonym Wi‑Fi cały ruch aplikacji idzie przez nie – także gdy Wi‑Fi nie ma internetu (np. punkt dostępu urządzenia). */
    private fun bindToWifi() {
        val cm = getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val cb = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) { try { cm.bindProcessToNetwork(network) } catch (e: Exception) { /* ignoruj */ } }
            override fun onLost(network: Network) { try { cm.bindProcessToNetwork(null) } catch (e: Exception) { /* ignoruj */ } }
        }
        netCallback = cb
        try {
            cm.registerNetworkCallback(NetworkRequest.Builder().addTransportType(NetworkCapabilities.TRANSPORT_WIFI).build(), cb)
        } catch (e: Exception) { netCallback = null }
    }

    // ------------------------------------------------------------------ WebView

    private fun makeWebView(local: Boolean): WebView {
        val wv = WebView(this)
        wv.setBackgroundColor(0xFF111318.toInt())
        wv.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            allowFileAccess = false
            allowContentAccess = false
            mediaPlaybackRequiresUserGesture = true
            cacheMode = WebSettings.LOAD_NO_CACHE
            mixedContentMode = WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE
            setSupportZoom(false)
        }
        wv.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(view: WebView, request: WebResourceRequest): WebResourceResponse? {
                val host = request.url.host ?: return null
                if (host == SHELL_HOST || host == DEMO_HOST) return serveLocal(request, host, local)
                return null
            }

            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                val u = request.url
                val host = u.host ?: return false
                if (local && host != SHELL_HOST) { openExternal(u.toString()); return true }   // powłoka nie wychodzi poza własne strony
                return false
            }

            override fun onPageFinished(view: WebView, url: String) {
                if (!local && clearHistoryAfterBlank && url == "about:blank") { clearHistoryAfterBlank = false; view.clearHistory() }
            }

            @Suppress("OVERRIDE_DEPRECATION")
            override fun onReceivedError(view: WebView, request: WebResourceRequest, error: android.webkit.WebResourceError) {
                if (!local && request.isForMainFrame) {
                    view.loadDataWithBaseURL(null, errorPage(request.url.toString()), "text/html", "utf-8", null)
                }
            }
        }
        wv.webChromeClient = object : WebChromeClient() {
            override fun onJsAlert(view: WebView, url: String, message: String, result: JsResult): Boolean {
                AlertDialog.Builder(this@MainActivity).setMessage(message).setCancelable(false)
                    .setPositiveButton("OK") { _, _ -> result.confirm() }.show()
                return true
            }

            override fun onJsConfirm(view: WebView, url: String, message: String, result: JsResult): Boolean {
                AlertDialog.Builder(this@MainActivity).setMessage(message).setCancelable(false)
                    .setPositiveButton("OK") { _, _ -> result.confirm() }
                    .setNegativeButton("Anuluj") { _, _ -> result.cancel() }.show()
                return true
            }

            override fun onJsPrompt(view: WebView, url: String, message: String, defaultValue: String?, result: JsPromptResult): Boolean {
                val input = EditText(this@MainActivity)
                input.setText(defaultValue ?: "")
                if (message.contains("asło", ignoreCase = true)) input.inputType = android.text.InputType.TYPE_CLASS_TEXT or android.text.InputType.TYPE_TEXT_VARIATION_PASSWORD
                AlertDialog.Builder(this@MainActivity).setMessage(message).setView(input).setCancelable(false)
                    .setPositiveButton("OK") { _, _ -> result.confirm(input.text.toString()) }
                    .setNegativeButton("Anuluj") { _, _ -> result.cancel() }.show()
                return true
            }

            override fun onShowFileChooser(view: WebView, callback: ValueCallback<Array<Uri>>, params: FileChooserParams): Boolean {
                fileCallback?.onReceiveValue(null)
                fileCallback = callback
                return try {
                    @Suppress("DEPRECATION")
                    startActivityForResult(params.createIntent(), REQ_FILE)
                    true
                } catch (e: Exception) {
                    fileCallback = null
                    false
                }
            }

            override fun onConsoleMessage(m: ConsoleMessage): Boolean = true
        }
        if (!local) {
            wv.setDownloadListener { url, _, disposition, mime, _ -> download(url, disposition, mime) }
        }
        return wv
    }

    private fun errorPage(url: String): String =
        "<html><body style='background:#111318;color:#e8eaf0;font-family:sans-serif;padding:24px'>" +
        "<h2>Brak połączenia z urządzeniem</h2><p style='color:#9aa1b2'>Nie udało się otworzyć:<br>" +
        android.text.TextUtils.htmlEncode(url) + "</p><p style='color:#9aa1b2'>Sprawdź, czy telefon jest w tej samej sieci Wi‑Fi " +
        "co urządzenie i czy urządzenie ma zasilanie. Stuknij ⟳, żeby spróbować ponownie.</p></body></html>"

    private fun mimeOf(path: String): String = when (path.substringAfterLast('.', "").lowercase()) {
        "html" -> "text/html"
        "js", "mjs" -> "text/javascript"
        "css" -> "text/css"
        "png" -> "image/png"
        "webp" -> "image/webp"
        "svg" -> "image/svg+xml"
        "json" -> "application/json"
        else -> "application/octet-stream"
    }

    private fun reply(status: Int, mime: String, body: ByteArray, extra: Map<String, String> = emptyMap()): WebResourceResponse {
        val enc = if (mime.startsWith("text/") || mime.contains("json") || mime.contains("javascript") || mime.contains("svg")) "utf-8" else null
        val headers = HashMap<String, String>(extra)
        headers["Cache-Control"] = "no-store"
        headers["Access-Control-Allow-Origin"] = "*"
        val reason = when (status) { 200 -> "OK"; 404 -> "Not Found"; 401 -> "Unauthorized"; 403 -> "Forbidden"; 422 -> "Unprocessable Entity"; else -> "Status" }
        return WebResourceResponse(mime.substringBefore(';'), enc, status, reason, headers, ByteArrayInputStream(body))
    }

    private fun serveLocal(request: WebResourceRequest, host: String, local: Boolean): WebResourceResponse {
        val path = request.url.path ?: "/"
        // Ta powłoka serwuje tylko swój host, widok urządzenia – tylko host demo.
        if ((host == SHELL_HOST) != local) return reply(404, "text/plain", "nie ma".toByteArray())
        if (host == DEMO_HOST && path.startsWith("/api/")) {
            val d = demo ?: return reply(503, "application/json", "{\"error\":\"demo_off\"}".toByteArray())
            val r = d.request(request.method ?: "GET", path, request.url.query ?: "", request.requestHeaders["Authorization"] ?: "", ByteArray(0))
            val extra = if (r.disposition.isNotEmpty()) mapOf("Content-Disposition" to r.disposition) else emptyMap()
            return reply(r.status, r.ctype, r.body, extra)
        }
        val base = if (host == SHELL_HOST) "app" else "web"
        var p = path
        if (p == "/" || p.isEmpty()) p = if (host == SHELL_HOST) "/app.html" else "/index.html"
        if (p.contains("..")) return reply(404, "text/plain", "nie ma".toByteArray())
        return try {
            var data = assets.open(base + p).use { it.readBytes() }
            val mime = mimeOf(p)
            if (host == DEMO_HOST && mime == "text/html" && demoFetchJs.isNotEmpty()) {
                // most fetch -> wirtualne urządzenie wstrzykiwany przed skryptami strony
                val html = String(data, Charsets.UTF_8)
                val tag = "<script>$demoFetchJs</script>"
                val i = html.indexOf("<head>")
                data = (if (i >= 0) html.substring(0, i + 6) + tag + html.substring(i + 6) else tag + html).toByteArray(Charsets.UTF_8)
            }
            reply(200, mime, data)
        } catch (e: Exception) {
            reply(404, "text/plain", "nie ma".toByteArray())
        }
    }

    // ------------------------------------------------------------------ pobieranie plików (dziennik, raport)

    private fun download(url: String, disposition: String, mime: String) {
        io.execute {
            try {
                val u = Uri.parse(url)
                val bytes: ByteArray
                var type = mime
                var cd = disposition
                if (u.host == DEMO_HOST) {
                    val d = demo ?: return@execute
                    val r = d.request("GET", u.path ?: "/", u.query ?: "", "", ByteArray(0))
                    bytes = r.body; type = r.ctype; if (cd.isEmpty()) cd = r.disposition
                } else {
                    val r = Http.get(url, 8000)
                    if (r == null || r.status !in 200..299) { toast("Nie udało się pobrać pliku (status ${r?.status ?: "brak połączenia"})"); return@execute }
                    bytes = r.body; if (cd.isEmpty()) cd = r.disposition
                }
                saveFile(URLUtil.guessFileName(url, cd, type), type.ifEmpty { "application/octet-stream" }, bytes)
            } catch (e: Exception) {
                toast("Błąd pobierania: ${e.message}")
            }
        }
    }

    private fun saveFile(name: String, mime: String, bytes: ByteArray) {
        val cv = ContentValues().apply {
            put(MediaStore.Downloads.DISPLAY_NAME, name)
            put(MediaStore.Downloads.MIME_TYPE, mime.substringBefore(';'))
            put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS)
        }
        val uri = contentResolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv)
        if (uri == null) { toast("Nie można zapisać pliku"); return }
        contentResolver.openOutputStream(uri)?.use { it.write(bytes) }
        toast("Zapisano w Pobranych: $name")
        ui.post {
            val send = Intent(Intent.ACTION_SEND).apply {
                type = mime.substringBefore(';'); putExtra(Intent.EXTRA_STREAM, uri); addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            try { startActivity(Intent.createChooser(send, "Wyślij plik")) } catch (e: Exception) { /* brak aplikacji do udostępniania */ }
        }
    }

    private fun openExternal(url: String) {
        try { startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url))) } catch (e: Exception) { toast("Nie można otworzyć: $url") }
    }

    // ------------------------------------------------------------------ mosty JavaScript

    /** Dla strony powłoki (app.html): lista urządzeń, wyszukiwanie, otwieranie. */
    inner class ShellBridge {
        @JavascriptInterface fun getDevices(): String = store.devices()

        @JavascriptInterface fun saveDevices(json: String) { store.setDevices(json) }

        @JavascriptInterface fun appInfo(): String {
            val v = try { packageManager.getPackageInfo(packageName, 0).versionName ?: "?" } catch (e: Exception) { "?" }
            return JSONObject().put("version", v).put("sdk", Build.VERSION.SDK_INT).toString()
        }

        @JavascriptInterface fun startDiscovery() {
            ui.post {
                if (discovery == null) discovery = Discovery(this@MainActivity) { json ->
                    ui.post { shell.evaluateJavascript("window.tpcDiscovered&&window.tpcDiscovered($json)", null) }
                }
                discovery?.start()
            }
        }

        @JavascriptInterface fun stopDiscovery() { ui.post { discovery?.stop() } }

        /** Status urządzenia (GET /api/v1/info); wynik wraca do window.tpcPing(id, info|null). */
        @JavascriptInterface fun ping(id: String, base: String) {
            io.execute {
                val r = Http.get(base.trimEnd('/') + "/api/v1/info", 2500)
                val out = if (r != null && r.status == 200) String(r.body, Charsets.UTF_8) else "null"
                val safe = if (out.startsWith("{")) out else "null"
                ui.post { shell.evaluateJavascript("window.tpcPing&&window.tpcPing(${JSONObject.quote(id)},$safe)", null) }
            }
        }

        @JavascriptInterface fun open(base: String, name: String) {
            ui.post {
                if (base == "demo") showDevice("https://$DEMO_HOST/", "Demo – wirtualny kocioł", true)
                else if (base.startsWith("http://") || base.startsWith("https://")) showDevice(base.trimEnd('/') + "/", name, false)
            }
        }

        @JavascriptInterface fun openSetup() { ui.post { showDevice(SETUP_URL, "Konfiguracja nowego urządzenia", false) } }

        @JavascriptInterface fun openExternalUrl(url: String) {
            if (url.startsWith("https://")) ui.post { openExternal(url) }
        }
    }

    /** Dla widoku urządzenia (strony urządzenia lub demo): zapis plików. */
    inner class AppBridge {
        @JavascriptInterface fun isApp(): Boolean = true

        @JavascriptInterface fun saveText(name: String, mime: String, text: String) {
            io.execute { try { saveFile(name, mime.ifEmpty { "text/plain" }, text.toByteArray(Charsets.UTF_8)) } catch (e: Exception) { toast("Błąd zapisu: ${e.message}") } }
        }
    }

    /** Most „fetch → wirtualne urządzenie” dla trybu demo (wstrzykiwany przez demo-fetch.js). */
    inner class DemoBridge {
        @JavascriptInterface fun request(method: String, path: String, query: String, authorization: String, body: String): String {
            val d = demo ?: return JSONObject().put("status", 503).put("ctype", "application/json").put("body", "{\"error\":\"demo_off\"}").toString()
            val r = d.request(method, path, query, authorization, body.toByteArray(Charsets.UTF_8))
            return JSONObject().put("status", r.status).put("ctype", r.ctype).put("body", String(r.body, Charsets.UTF_8)).toString()
        }
    }
}
