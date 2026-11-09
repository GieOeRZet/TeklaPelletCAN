package pl.gieoerzet.teklapelletcan

import android.content.Context

/** Zapamiętana lista urządzeń (JSON w SharedPreferences, pole zarządzane przez stronę powłoki). */
class Store(ctx: Context) {
    private val sp = ctx.getSharedPreferences("tpc", Context.MODE_PRIVATE)

    fun devices(): String = sp.getString("devices", "[]") ?: "[]"
    fun setDevices(json: String) { sp.edit().putString("devices", json).apply() }
}
