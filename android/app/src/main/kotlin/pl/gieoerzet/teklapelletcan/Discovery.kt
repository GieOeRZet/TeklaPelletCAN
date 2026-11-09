package pl.gieoerzet.teklapelletcan

import android.content.Context
import android.net.nsd.NsdManager
import android.net.nsd.NsdServiceInfo
import org.json.JSONObject

/** Wyszukiwanie urządzeń w sieci (mDNS/NSD, usługa _teklapelletcan._tcp). Wyniki trafiają do onFound jako JSON. */
class Discovery(ctx: Context, private val onFound: (String) -> Unit) {
    private val nsd = ctx.applicationContext.getSystemService(Context.NSD_SERVICE) as NsdManager
    private var listener: NsdManager.DiscoveryListener? = null
    private val queue = ArrayDeque<NsdServiceInfo>()
    private var resolving = false

    @Synchronized
    fun start() {
        if (listener != null) return
        val l = object : NsdManager.DiscoveryListener {
            override fun onDiscoveryStarted(serviceType: String) {}
            override fun onDiscoveryStopped(serviceType: String) {}
            override fun onStartDiscoveryFailed(serviceType: String, errorCode: Int) { synchronized(this@Discovery) { listener = null } }
            override fun onStopDiscoveryFailed(serviceType: String, errorCode: Int) {}
            override fun onServiceLost(info: NsdServiceInfo) {}
            override fun onServiceFound(info: NsdServiceInfo) {
                synchronized(this@Discovery) { queue.addLast(info) }
                resolveNext()
            }
        }
        listener = l
        try {
            nsd.discoverServices("_teklapelletcan._tcp", NsdManager.PROTOCOL_DNS_SD, l)
        } catch (e: Exception) {
            listener = null
        }
    }

    @Synchronized
    fun stop() {
        val l = listener ?: return
        listener = null
        queue.clear()
        resolving = false
        try { nsd.stopServiceDiscovery(l) } catch (e: Exception) { /* już zatrzymane */ }
    }

    @Suppress("DEPRECATION")
    private fun resolveNext() {
        val info: NsdServiceInfo = synchronized(this) {
            if (resolving || queue.isEmpty()) null else { resolving = true; queue.removeFirst() }
        } ?: return
        try {
            nsd.resolveService(info, object : NsdManager.ResolveListener {
                override fun onResolveFailed(i: NsdServiceInfo, errorCode: Int) { done() }
                override fun onServiceResolved(i: NsdServiceInfo) {
                    val host = i.host?.hostAddress
                    if (host != null && !host.contains(':')) {
                        val o = JSONObject()
                        o.put("name", i.serviceName)
                        o.put("host", host)
                        o.put("port", i.port)
                        val id = i.attributes?.get("id")
                        if (id != null) o.put("id", String(id, Charsets.UTF_8))
                        val fw = i.attributes?.get("fw")
                        if (fw != null) o.put("fw", String(fw, Charsets.UTF_8))
                        onFound(o.toString())
                    }
                    done()
                }
            })
        } catch (e: Exception) {
            done()
        }
    }

    private fun done() {
        synchronized(this) { resolving = false }
        resolveNext()
    }
}
