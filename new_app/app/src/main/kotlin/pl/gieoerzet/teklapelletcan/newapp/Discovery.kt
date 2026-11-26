package pl.gieoerzet.teklapelletcan.newapp

import android.Manifest
import android.annotation.SuppressLint
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.le.BluetoothLeScanner
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanResult
import android.bluetooth.le.ScanSettings
import android.content.Context
import android.content.pm.PackageManager
import android.net.nsd.NsdManager
import android.net.nsd.NsdServiceInfo
import androidx.core.content.ContextCompat
import org.json.JSONObject

data class BleFound(val name: String, val address: String, val rssi: Int)

class BleDiscovery(private val context: Context) {
    private val adapter: BluetoothAdapter? = BluetoothAdapter.getDefaultAdapter()
    private var scanner: BluetoothLeScanner? = null
    private var callback: ScanCallback? = null

    private fun allowed(): Boolean =
        ContextCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_SCAN) == PackageManager.PERMISSION_GRANTED &&
        ContextCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_CONNECT) == PackageManager.PERMISSION_GRANTED

    @SuppressLint("MissingPermission")
    fun start(onFound: (BleFound) -> Unit, onError: (String) -> Unit) {
        if (!allowed()) { onError("Brak uprawnień Bluetooth"); return }
        if (adapter?.isEnabled != true) { onError("Bluetooth jest wyłączony"); return }
        stop()
        scanner = adapter.bluetoothLeScanner
        callback = object : ScanCallback() {
            override fun onScanResult(type: Int, result: ScanResult) {
                val name = result.scanRecord?.deviceName ?: result.device.name ?: return
                if (!name.startsWith("TeklaPellet-", ignoreCase = true)) return
                onFound(BleFound(name, result.device.address, result.rssi))
            }
            override fun onScanFailed(errorCode: Int) { onError("BLE scan error: $errorCode") }
        }
        scanner?.startScan(
            emptyList(),
            ScanSettings.Builder().setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY).build(),
            callback
        )
    }

    @SuppressLint("MissingPermission")
    fun stop() {
        val s = scanner
        val c = callback
        if (s != null && c != null && allowed()) runCatching { s.stopScan(c) }
        scanner = null
        callback = null
    }
}

data class MdnsFound(val name: String, val host: String, val port: Int, val id: String, val firmware: String)

class MdnsDiscovery(context: Context) {
    private val nsd = context.getSystemService(Context.NSD_SERVICE) as NsdManager
    private var listener: NsdManager.DiscoveryListener? = null
    private val resolving = ArrayDeque<NsdServiceInfo>()
    private var busy = false

    fun start(onFound: (MdnsFound) -> Unit) {
        stop()
        val l = object : NsdManager.DiscoveryListener {
            override fun onDiscoveryStarted(serviceType: String) {}
            override fun onDiscoveryStopped(serviceType: String) {}
            override fun onStartDiscoveryFailed(serviceType: String, errorCode: Int) { listener = null }
            override fun onStopDiscoveryFailed(serviceType: String, errorCode: Int) {}
            override fun onServiceLost(serviceInfo: NsdServiceInfo) {}
            override fun onServiceFound(serviceInfo: NsdServiceInfo) {
                synchronized(resolving) { resolving.addLast(serviceInfo) }
                resolveNext(onFound)
            }
        }
        listener = l
        runCatching { nsd.discoverServices("_teklapelletcan._tcp", NsdManager.PROTOCOL_DNS_SD, l) }
            .onFailure { listener = null }
    }

    fun stop() {
        listener?.let { runCatching { nsd.stopServiceDiscovery(it) } }
        listener = null
        synchronized(resolving) { resolving.clear(); busy = false }
    }

    private fun resolveNext(onFound: (MdnsFound) -> Unit) {
        val item = synchronized(resolving) {
            if (busy || resolving.isEmpty()) null else { busy = true; resolving.removeFirst() }
        } ?: return
        runCatching {
            nsd.resolveService(item, object : NsdManager.ResolveListener {
                override fun onResolveFailed(serviceInfo: NsdServiceInfo, errorCode: Int) { done(onFound) }
                override fun onServiceResolved(info: NsdServiceInfo) {
                    val host = info.host?.hostAddress
                    if (host != null) {
                        val id = info.attributes?.get("id")?.toString(Charsets.UTF_8) ?: ""
                        val fw = info.attributes?.get("fw")?.toString(Charsets.UTF_8) ?: ""
                        onFound(MdnsFound(info.serviceName, host, info.port, id, fw))
                    }
                    done(onFound)
                }
            })
        }.onFailure { done(onFound) }
    }

    private fun done(onFound: (MdnsFound) -> Unit) {
        synchronized(resolving) { busy = false }
        resolveNext(onFound)
    }
}
