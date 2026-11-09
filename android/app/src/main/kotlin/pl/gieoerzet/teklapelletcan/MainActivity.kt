package pl.gieoerzet.teklapelletcan

import android.app.Activity
import android.app.AlertDialog
import android.content.BroadcastReceiver
import android.content.ContentValues
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.SharedPreferences
import android.content.res.Configuration
import android.hardware.biometrics.BiometricManager
import android.hardware.biometrics.BiometricPrompt
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import android.net.NetworkRequest
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.CancellationSignal
import android.os.Environment
import android.os.Handler
import android.os.Looper
import android.provider.MediaStore
import android.util.TypedValue
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.view.ViewGroup
import android.view.WindowInsets
import android.view.WindowInsetsController
import android.view.WindowManager
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
import org.json.JSONArray
import org.json.JSONObject
import java.io.ByteArrayInputStream
import java.util.concurrent.Executors

/**
 * Samodzielna aplikacja: interfejs (android/ui) jest wbudowany w APK i rozmawia z urządzeniem wyłącznie przez natywny proxy
 * (blokada zapisu, cache ostatnich odczytów, token urządzenia). Oryginalna karta i konfiguracja urządzenia to osobne okno
 * (strony urządzenia lub z paczki w trybie demo), dostępne tylko przy odblokowanej aplikacji.
 */
class MainActivity : Activity() {
    companion object {
        const val UI_HOST = "ui.tpc"
        const val DEMO_HOST = "demo.tpc"
        const val SETUP_URL = "http://10.77.77.1/"
        const val REQ_FILE = 71
        const val IDLE_MS = 300_000L
    }

    private lateinit var ui: WebView
    private lateinit var device: WebView
    private lateinit var deviceBox: LinearLayout
    private lateinit var titleView: TextView
    private lateinit var root: FrameLayout
    private val main = Handler(Looper.getMainLooper())
    private val io = Executors.newCachedThreadPool()
    private lateinit var prefs: SharedPreferences
    private lateinit var kv: KV
    private lateinit var security: SecurityStore
    private lateinit var cache: Cache
    private val gate = WriteGate({ System.currentTimeMillis() }, IDLE_MS)
    private var discovery: Discovery? = null
    @Volatile private var demo: DemoHost? = null
    @Volatile private var backend: Backend? = null
    @Volatile private var proxy: Proxy? = null
    @Volatile private var deviceName = ""
    @Volatile private var deviceBase = ""        // http://ip (prawdziwe urządzenie) albo "demo"
    private var fileCallback: ValueCallback<Array<Uri>>? = null
    private var clearHistoryAfterBlank = false
    private var netCallback: ConnectivityManager.NetworkCallback? = null
    private var wasUnlocked = false
    private var screenReceiver: BroadcastReceiver? = null

    // ------------------------------------------------------------------ cykl życia

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        prefs = getSharedPreferences("tpc", Context.MODE_PRIVATE)
        kv = object : KV {
            override fun getString(k: String) = prefs.getString(k, null)
            override fun putString(k: String, v: String?) { prefs.edit().putString(k, v).apply() }
            override fun getLong(k: String, d: Long) = prefs.getLong(k, d)
            override fun putLong(k: String, v: Long) { prefs.edit().putLong(k, v).apply() }
        }
        security = SecurityStore(kv)
        cache = Cache(java.io.File(filesDir, "cache"))

        ui = makeWebView(trusted = true)
        ui.addJavascriptInterface(NativeBridge(), "TPCNative")

        device = makeWebView(trusted = false)
        device.addJavascriptInterface(DemoBridge(), "TPCDemo")
        device.addJavascriptInterface(AppBridge(), "TPCApp")

        titleView = TextView(this).apply {
            setTextColor(0xFFE8EAF0.toInt()); textSize = 16f; maxLines = 1
            layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
        }
        val bar = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL
            setBackgroundColor(0xFF1C1F27.toInt()); setPadding(dp(4), 0, dp(4), 0)
            addView(barButton("←") { closeDevice() })
            addView(titleView)
            addView(barButton("⟳") { device.reload() })
        }
        deviceBox = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL; visibility = View.GONE
            addView(bar, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(48)))
            addView(device, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f))
        }
        root = FrameLayout(this).apply {
            setBackgroundColor(0xFF111318.toInt())
            addView(ui, FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
            addView(deviceBox, FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
            setOnApplyWindowInsetsListener { v, ins -> applyInsets(v, ins); ins }
        }
        setContentView(root)
        if (Build.VERSION.SDK_INT >= 28) window.attributes.layoutInDisplayCutoutMode = WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
        applyOrientation(resources.configuration)
        ui.loadUrl("https://$UI_HOST/")
        bindToWifi()

        screenReceiver = object : BroadcastReceiver() {
            override fun onReceive(c: Context, i: Intent) { lockNow("screen_off") }
        }
        registerReceiver(screenReceiver, IntentFilter(Intent.ACTION_SCREEN_OFF))
        tick()
    }

    override fun onDestroy() {
        discovery?.stop()
        demo?.close(); demo = null
        screenReceiver?.let { try { unregisterReceiver(it) } catch (e: Exception) { /* ignoruj */ } }
        netCallback?.let { try { (getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager).unregisterNetworkCallback(it) } catch (e: Exception) { /* ignoruj */ } }
        main.removeCallbacksAndMessages(null)
        io.shutdownNow()
        super.onDestroy()
    }

    override fun onStop() { super.onStop(); discovery?.stop(); lockNow("background") }

    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        applyOrientation(newConfig)
    }

    /** Każde dotknięcie ekranu liczy się jako aktywność: przedłuża odblokowanie. */
    override fun dispatchTouchEvent(ev: MotionEvent): Boolean { gate.touch(); return super.dispatchTouchEvent(ev) }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (deviceBox.visibility == View.VISIBLE) {
            if (device.canGoBack() && device.url != "about:blank") device.goBack() else closeDevice()
        } else {
            ui.evaluateJavascript("(window.__tpcBack&&window.__tpcBack())||false") { r -> if (r != "true") finish() }
        }
    }

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

    // ------------------------------------------------------------------ blokada zapisu

    /** Co sekundę sprawdza wygaśnięcie odblokowania (5 min bezczynności). */
    private fun tick() {
        val open = gate.isUnlocked()
        if (wasUnlocked && !open) onLocked("idle")
        wasUnlocked = open
        main.postDelayed({ tick() }, 1000)
    }

    private fun lockNow(reason: String) {
        val was = gate.isUnlocked()
        gate.lock()
        wasUnlocked = false
        if (was) onLocked(reason)
    }

    private fun onLocked(reason: String) {
        val px = proxy
        if (px != null) io.execute { try { px.dropBoilerLevel() } catch (e: Exception) { /* urządzenie poza zasięgiem */ } }
        if (deviceBox.visibility == View.VISIBLE) closeDevice(silent = true)
        event(JSONObject().put("type", "locked").put("reason", reason))
    }

    private fun event(o: JSONObject) {
        main.post { ui.evaluateJavascript("window.__tpcEvent&&window.__tpcEvent(${o})", null) }
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
            val s = ins.getInsets(WindowInsets.Type.systemBars() or WindowInsets.Type.displayCutout())
            val k = ins.getInsets(WindowInsets.Type.ime())
            v.setPadding(s.left, s.top, s.right, maxOf(s.bottom, k.bottom))
        } else {
            @Suppress("DEPRECATION")
            v.setPadding(ins.systemWindowInsetLeft, ins.systemWindowInsetTop, ins.systemWindowInsetRight, ins.systemWindowInsetBottom)
        }
    }

    /** Poziomo: pełny ekran (paski systemowe ukryte); pionowo: paski widoczne. */
    @Suppress("DEPRECATION")
    private fun applyOrientation(cfg: Configuration) {
        val land = cfg.orientation == Configuration.ORIENTATION_LANDSCAPE
        if (Build.VERSION.SDK_INT >= 30) {
            val c = window.insetsController ?: return
            if (land) {
                c.hide(WindowInsets.Type.systemBars())
                c.systemBarsBehavior = WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
            } else {
                c.show(WindowInsets.Type.systemBars())
            }
        } else {
            window.decorView.systemUiVisibility = if (land)
                View.SYSTEM_UI_FLAG_FULLSCREEN or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION or View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY or View.SYSTEM_UI_FLAG_LAYOUT_STABLE
            else View.SYSTEM_UI_FLAG_VISIBLE
        }
        root.requestApplyInsets()
    }

    private fun toast(t: String) = main.post { Toast.makeText(this, t, Toast.LENGTH_LONG).show() }

    private fun closeDevice(silent: Boolean = false) {
        if (deviceBox.visibility != View.VISIBLE) return
        deviceBox.visibility = View.GONE
        ui.visibility = View.VISIBLE
        clearHistoryAfterBlank = true
        device.loadUrl("about:blank")
        if (!silent) event(JSONObject().put("type", "device_closed"))
    }

    /** Okno z oryginalną kartą lub konfiguracją urządzenia: wymaga odblokowanej aplikacji (zapisy idą wtedy poza proxy). */
    private fun openDeviceWindow(path: String, title: String) {
        if (!gate.isUnlocked()) { event(JSONObject().put("type", "needs_unlock")); return }
        val demoMode = backend?.isDemo == true
        val base = if (demoMode) "https://$DEMO_HOST/" else deviceBase.trimEnd('/') + "/"
        titleView.text = title
        ui.visibility = View.GONE
        deviceBox.visibility = View.VISIBLE
        device.loadUrl(base + path)
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

    private fun makeWebView(trusted: Boolean): WebView {
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
                if (host == UI_HOST || host == DEMO_HOST) return serveLocal(request, host, trusted)
                return null
            }

            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                val host = request.url.host ?: return false
                if (trusted && host != UI_HOST) { openExternal(request.url.toString()); return true }
                return false
            }

            override fun onPageFinished(view: WebView, url: String) {
                if (!trusted && clearHistoryAfterBlank && url == "about:blank") { clearHistoryAfterBlank = false; view.clearHistory() }
            }

            override fun onReceivedError(view: WebView, request: WebResourceRequest, error: android.webkit.WebResourceError) {
                if (!trusted && request.isForMainFrame) {
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
        if (!trusted) wv.setDownloadListener { url, _, disposition, mime, _ -> download(url, disposition, mime) }
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

    /** Interfejs aplikacji (host ui.tpc) tylko w zaufanym widoku; strony demo (host demo.tpc) tylko w widoku urządzenia. */
    private fun serveLocal(request: WebResourceRequest, host: String, trusted: Boolean): WebResourceResponse {
        val path = request.url.path ?: "/"
        if ((host == UI_HOST) != trusted) return reply(404, "text/plain", "nie ma".toByteArray())
        if (host == DEMO_HOST && path.startsWith("/api/")) {
            val d = demo ?: return reply(503, "application/json", "{\"error\":\"demo_off\"}".toByteArray())
            val r = d.request(request.method ?: "GET", path, request.url.query ?: "", request.requestHeaders["Authorization"] ?: "", ByteArray(0))
            val extra = if (r.disposition.isNotEmpty()) mapOf("Content-Disposition" to r.disposition) else emptyMap()
            return reply(r.status, r.ctype, r.body, extra)
        }
        val base = if (host == UI_HOST) "ui" else "web"
        var p = path
        if (p == "/" || p.isEmpty()) p = "/index.html"
        if (p.contains("..")) return reply(404, "text/plain", "nie ma".toByteArray())
        return try {
            var data = assets.open(base + p).use { it.readBytes() }
            val mime = mimeOf(p)
            if (host == DEMO_HOST && mime == "text/html") {
                val js = try { assets.open("ui/demo-fetch.js").bufferedReader().use { it.readText() } } catch (e: Exception) { "" }
                if (js.isNotEmpty()) {
                    val html = String(data, Charsets.UTF_8)
                    val tag = "<script>$js</script>"
                    val i = html.indexOf("<head>")
                    data = (if (i >= 0) html.substring(0, i + 6) + tag + html.substring(i + 6) else tag + html).toByteArray(Charsets.UTF_8)
                }
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
        main.post {
            val send = Intent(Intent.ACTION_SEND).apply {
                type = mime.substringBefore(';'); putExtra(Intent.EXTRA_STREAM, uri); addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            try { startActivity(Intent.createChooser(send, "Wyślij plik")) } catch (e: Exception) { /* brak aplikacji do udostępniania */ }
        }
    }

    private fun openExternal(url: String) {
        try { startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url))) } catch (e: Exception) { toast("Nie można otworzyć: $url") }
    }

    // ------------------------------------------------------------------ biometria

    private fun biometricAvailable(): Boolean {
        val bm = getSystemService(Context.BIOMETRIC_SERVICE) as? BiometricManager ?: return false
        return if (Build.VERSION.SDK_INT >= 30) bm.canAuthenticate(android.hardware.biometrics.BiometricManager.Authenticators.BIOMETRIC_STRONG) == BiometricManager.BIOMETRIC_SUCCESS
        else @Suppress("DEPRECATION") (bm.canAuthenticate() == BiometricManager.BIOMETRIC_SUCCESS)
    }

    private fun promptBiometric() {
        main.post {
            try {
                val prompt = BiometricPrompt.Builder(this)
                    .setTitle("Odblokuj sterowanie")
                    .setSubtitle("Zapis do kotła włączy się na 5 minut")
                    .setNegativeButton("Użyj PIN-u aplikacji", mainExecutor) { _, _ -> event(JSONObject().put("type", "bio").put("ok", false).put("cancel", true)) }
                    .build()
                prompt.authenticate(CancellationSignal(), mainExecutor, object : BiometricPrompt.AuthenticationCallback() {
                    override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                        gate.unlock(); wasUnlocked = true
                        event(JSONObject().put("type", "bio").put("ok", true))
                    }
                    override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                        event(JSONObject().put("type", "bio").put("ok", false).put("error", errString.toString()))
                    }
                })
            } catch (e: Exception) {
                event(JSONObject().put("type", "bio").put("ok", false).put("error", e.message ?: "biometria niedostępna"))
            }
        }
    }

    // ------------------------------------------------------------------ mosty JavaScript

    private fun stateJson(): String {
        val o = JSONObject()
        o.put("hasPin", security.hasPin())
        o.put("bio", security.biometricEnabled)
        o.put("bioAsked", security.biometricAsked)
        o.put("bioAvailable", biometricAvailable())
        o.put("lockOnStart", security.lockOnStart)
        o.put("unlocked", gate.isUnlocked())
        o.put("remainingMs", gate.remainingMs())
        o.put("deviceName", deviceName)
        o.put("demo", backend?.isDemo == true)
        o.put("version", try { packageManager.getPackageInfo(packageName, 0).versionName ?: "?" } catch (e: Exception) { "?" })
        o.put("sdk", Build.VERSION.SDK_INT)
        return o.toString()
    }

    /** Most dla interfejsu aplikacji (zaufane strony z paczki APK). */
    inner class NativeBridge {
        @JavascriptInterface fun state(): String = stateJson()

        // --- urządzenia
        @JavascriptInterface fun getDevices(): String = prefs.getString("devices", "[]") ?: "[]"
        @JavascriptInterface fun saveDevices(json: String) { prefs.edit().putString("devices", json).apply() }

        @JavascriptInterface fun startDiscovery() {
            main.post {
                if (discovery == null) discovery = Discovery(this@MainActivity) { json ->
                    main.post { ui.evaluateJavascript("window.tpcDiscovered&&window.tpcDiscovered($json)", null) }
                }
                discovery?.start()
            }
        }
        @JavascriptInterface fun stopDiscovery() { main.post { discovery?.stop() } }

        @JavascriptInterface fun ping(id: String, base: String) {
            io.execute {
                val r = Http.get(base.trimEnd('/') + "/api/v1/info", 2500)
                val out = if (r != null && r.status == 200) String(r.body, Charsets.UTF_8) else "null"
                val safe = if (out.startsWith("{")) out else "null"
                main.post { ui.evaluateJavascript("window.tpcPing&&window.tpcPing(${JSONObject.quote(id)},$safe)", null) }
            }
        }

        /** Wybiera urządzenie do pracy (adres http albo "demo"). Stan ustawiany od razu (interfejs czyta go zaraz po wywołaniu). */
        @JavascriptInterface @Synchronized fun selectDevice(base: String, name: String) {
            gate.lock(); wasUnlocked = false
            main.post { closeDevice(silent = true) }
            demo?.close(); demo = null
            deviceName = name; deviceBase = base
            val be: Backend = if (base == "demo") {
                val v = try { packageManager.getPackageInfo(packageName, 0).versionName ?: "demo" } catch (e: Exception) { "demo" }
                val h = DemoHost("$v-demo"); demo = h; DemoBackend(h)
            } else HttpBackend(base.trimEnd('/'))
            backend = be
            proxy = Proxy(be, gate, cache, kv)
        }

        @JavascriptInterface @Synchronized fun deselect() {
            gate.lock(); wasUnlocked = false
            main.post { closeDevice(silent = true) }
            demo?.close(); demo = null; backend = null; proxy = null; deviceName = ""
        }

        /** Ostatnie zapamiętane stany urządzenia (do podsumowania na liście). */
        @JavascriptInterface fun deviceSummary(base: String): String {
            val e = cache.get(HttpBackend(base.trimEnd('/')).key, "/api/v1/states") ?: return "{}"
            return JSONObject().put("at", e.at).put("body", e.body).toString()
        }

        /** Żądanie API do wybranego urządzenia (asynchroniczne; wynik: window.__tpcResp(id, {status, ctype, body, cachedAt})). */
        @JavascriptInterface fun request(id: String, method: String, pathQuery: String, body: String) {
            val px = proxy
            io.execute {
                val out = if (px == null) Proxy.Out(503, "application/json", "{\"ok\":false,\"error\":\"no_device\"}")
                else try { px.handle(method, pathQuery, body) } catch (e: Exception) { Proxy.Out(500, "application/json", "{\"ok\":false,\"error\":\"internal\"}") }
                val o = JSONObject().put("status", out.status).put("ctype", out.ctype).put("body", out.body).put("cachedAt", out.cachedAt)
                if (out.disposition.isNotEmpty()) o.put("disposition", out.disposition)
                main.post { ui.evaluateJavascript("window.__tpcResp&&window.__tpcResp(${JSONObject.quote(id)},$o)", null) }
            }
        }

        // --- bezpieczeństwo
        @JavascriptInterface fun setupPin(pin: String): String {
            val err = security.setPin(pin)
            return JSONObject().put("ok", err == null).put("error", err ?: "").toString()
        }

        @JavascriptInterface fun changePin(oldPin: String, newPin: String): String {
            val c = security.verify(oldPin)
            if (c !is SecurityStore.Check.Ok) return checkJson(c)
            val err = security.setPin(newPin)
            return JSONObject().put("ok", err == null).put("error", err ?: "").toString()
        }

        private fun checkJson(c: SecurityStore.Check): String = when (c) {
            is SecurityStore.Check.Ok -> JSONObject().put("ok", true)
            is SecurityStore.Check.Wrong -> JSONObject().put("ok", false).put("attemptsLeft", c.attemptsLeft)
            is SecurityStore.Check.Locked -> JSONObject().put("ok", false).put("lockedUntil", c.untilMs).put("waitMs", maxOf(0L, c.untilMs - System.currentTimeMillis()))
        }.toString()

        @JavascriptInterface fun unlockPin(pin: String): String {
            val c = security.verify(pin)
            if (c is SecurityStore.Check.Ok) { gate.unlock(); wasUnlocked = true }
            return checkJson(c)
        }

        @JavascriptInterface fun unlockBio() {
            if (security.biometricEnabled && biometricAvailable()) promptBiometric()
            else event(JSONObject().put("type", "bio").put("ok", false).put("error", "biometria wyłączona"))
        }

        @JavascriptInterface fun lock() { main.post { lockNow("user") } }
        @JavascriptInterface fun setBio(on: Boolean) { security.biometricEnabled = on; security.biometricAsked = true }
        @JavascriptInterface fun setLockOnStart(on: Boolean) { security.lockOnStart = on }
        @JavascriptInterface fun clearCache() { cache.clear() }

        /** Reset PIN (po wyczyszczeniu danych) – wymaga potwierdzenia w interfejsie; kasuje PIN i biometrię. */
        @JavascriptInterface fun resetSecurity() { security.reset(); gate.lock(); wasUnlocked = false }

        // --- okna urządzenia i narzędzia
        @JavascriptInterface fun openOriginal() { main.post { openDeviceWindow("index.html", "Panel kotła (oryginał)") } }
        @JavascriptInterface fun openDeviceSettings() { main.post { openDeviceWindow("settings.html", "Konfiguracja urządzenia") } }
        @JavascriptInterface fun openSetup() {
            main.post {
                backend = HttpBackend(SETUP_URL.trimEnd('/')); deviceBase = SETUP_URL; deviceName = "Nowe urządzenie"
                proxy = Proxy(backend!!, gate, cache, kv)
                titleView.text = "Konfiguracja nowego urządzenia"
                ui.visibility = View.GONE; deviceBox.visibility = View.VISIBLE
                device.loadUrl(SETUP_URL)
            }
        }
        @JavascriptInterface fun openExternalUrl(url: String) { if (url.startsWith("https://")) main.post { openExternal(url) } }
        @JavascriptInterface fun saveText(name: String, mime: String, text: String) {
            io.execute { try { saveFile(name, mime.ifEmpty { "text/plain" }, text.toByteArray(Charsets.UTF_8)) } catch (e: Exception) { toast("Błąd zapisu: ${e.message}") } }
        }
        @JavascriptInterface fun now(): Long = System.currentTimeMillis()
    }

    /** Dla widoku oryginalnej karty/konfiguracji: zapis plików. */
    inner class AppBridge {
        @JavascriptInterface fun isApp(): Boolean = true
        @JavascriptInterface fun saveText(name: String, mime: String, text: String) {
            io.execute { try { saveFile(name, mime.ifEmpty { "text/plain" }, text.toByteArray(Charsets.UTF_8)) } catch (e: Exception) { toast("Błąd zapisu: ${e.message}") } }
        }
    }

    /** Most „fetch → wirtualne urządzenie” dla oryginalnych stron w trybie demo (wstrzykiwany przez demo-fetch.js). */
    inner class DemoBridge {
        @JavascriptInterface fun request(method: String, path: String, query: String, authorization: String, body: String): String {
            val d = demo ?: return JSONObject().put("status", 503).put("ctype", "application/json").put("body", "{\"error\":\"demo_off\"}").toString()
            val r = d.request(method, path, query, authorization, body.toByteArray(Charsets.UTF_8))
            return JSONObject().put("status", r.status).put("ctype", r.ctype).put("body", String(r.body, Charsets.UTF_8)).toString()
        }
    }
}
