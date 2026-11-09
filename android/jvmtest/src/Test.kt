package pl.gieoerzet.teklapelletcan

import java.io.File

var failures = 0
fun check(name: String, cond: Boolean, extra: String = "") {
    println((if (cond) "OK   " else "FAIL ") + name + (if (cond) "" else " $extra"))
    if (!cond) failures++
}

class FakeBackend : Backend {
    override val key = "fake"
    override val isDemo = false
    var online = true
    val seen = ArrayList<String>()
    override fun request(method: String, pathQuery: String, authorization: String, body: ByteArray): DemoHost.Reply? {
        seen.add("$method $pathQuery auth=$authorization body=${String(body)}")
        if (!online) return null
        val resp = when {
            pathQuery.startsWith("/api/v1/states") -> "{\"states\":[{\"entity_id\":\"sensor.x\",\"state\":\"71.6\"}]}"
            pathQuery.startsWith("/api/v1/pair") -> "{\"ok\":true,\"token\":\"tok123\"}"
            else -> "{\"ok\":true}"
        }
        return DemoHost.Reply(200, "application/json", "", resp.toByteArray())
    }
}

fun main() {
    // ---- WriteGate
    var t = 1_000_000L
    val gate = WriteGate({ t }, 300_000)
    check("gate: domyślnie zablokowana", !gate.isUnlocked())
    check("gate: GET wolny przy blokadzie", WriteGate.allowedWhenLocked("GET", "/api/v1/states", ""))
    check("gate: zapis zablokowany", !WriteGate.allowedWhenLocked("POST", "/api/v1/write", "{}"))
    check("gate: unlock (PIN poziomu) zablokowany", !WriteGate.allowedWhenLocked("POST", "/api/v1/call", "{\"service\":\"tekla_estyma_unlock\"}"))
    check("gate: set_param zablokowany", !WriteGate.allowedWhenLocked("POST", "/api/v1/call", "{\"domain\":\"x\",\"service\":\"tekla_estyma_set_param\"}"))
    check("gate: odświeżenie parametrów wolne", WriteGate.allowedWhenLocked("POST", "/api/v1/call", "{\"service\":\"tekla_estyma_param_refresh\"}"))
    check("gate: parowanie wolne", WriteGate.allowedWhenLocked("POST", "/api/v1/pair", "{}"))
    check("gate: brak usługi = zablokowane", !WriteGate.allowedWhenLocked("POST", "/api/v1/call", "{}"))
    check("gate: konfiguracja urządzenia zablokowana", !WriteGate.allowedWhenLocked("POST", "/api/v1/config", "{}"))
    gate.unlock()
    check("gate: odblokowana po unlock", gate.isUnlocked())
    t += 200_000; gate.touch()
    t += 200_000
    check("gate: aktywność przedłuża odblokowanie", gate.isUnlocked())
    t += 301_000
    check("gate: wygasa po 5 min bezczynności", !gate.isUnlocked())
    gate.unlock(); gate.lock()
    check("gate: lock() blokuje od razu", !gate.isUnlocked())
    gate.touch()
    check("gate: touch nie odblokowuje", !gate.isUnlocked())
    gate.unlock(); check("gate: pozostały czas ~5 min", gate.remainingMs() in 299_000..300_000)

    // ---- SecurityStore
    val kv = MemoryKV()
    var now = 5_000_000L
    val sec = SecurityStore(kv, { now })
    check("pin: brak na starcie", !sec.hasPin())
    check("pin: za krótki odrzucony", sec.setPin("12") != null)
    check("pin: litery odrzucone", sec.setPin("12ab") != null)
    check("pin: poprawny przyjęty", sec.setPin("2468") == null && sec.hasPin())
    check("pin: nie zapisany jawnie", kv.getString("pin_hash") != null && !kv.getString("pin_hash")!!.contains("2468") && kv.getString("pin_salt") != null)
    check("pin: poprawny weryfikuje", sec.verify("2468") is SecurityStore.Check.Ok)
    val w = sec.verify("0000")
    check("pin: zły – zostaje 4 próby", w is SecurityStore.Check.Wrong && w.attemptsLeft == 4)
    for (i in 1..3) sec.verify("1111")
    val last = sec.verify("1111")
    check("pin: po 5 błędach blokada 30 s", last is SecurityStore.Check.Locked && last.untilMs - now == 30_000L, last.toString())
    check("pin: w blokadzie nawet dobry PIN odrzucony", sec.verify("2468") is SecurityStore.Check.Locked)
    now += 31_000
    check("pin: po upływie blokady dobry PIN działa", sec.verify("2468") is SecurityStore.Check.Ok)
    sec.verify("1"); sec.verify("1"); sec.verify("1"); sec.verify("1"); sec.verify("1")
    check("pin: poprawny zeruje licznik", sec.verify("2468").let { it is SecurityStore.Check.Locked || it is SecurityStore.Check.Ok })
    check("bio: domyślnie wyłączona", !sec.biometricEnabled && !sec.biometricAsked)
    sec.biometricEnabled = true; sec.biometricAsked = true
    check("bio: zapamiętana", sec.biometricEnabled && sec.biometricAsked)

    // ---- Cache + Proxy
    val dir = File.createTempFile("tpc", "d").let { it.delete(); it.mkdirs(); it }
    val cache = Cache(dir, { t })
    val be = FakeBackend()
    val tokens = MemoryKV()
    val gate2 = WriteGate({ t }, 300_000)
    val px = Proxy(be, gate2, cache, tokens, { t })
    val tSave = t

    val ro = px.handle("POST", "/api/v1/write", "{\"id\":\"boiler_set_manual\",\"value\":70}")
    check("proxy: zapis zablokowany (403 app_locked)", ro.status == 403 && ro.body.contains("app_locked"))
    check("proxy: zablokowany zapis nie dotarł do urządzenia", be.seen.none { it.contains("/api/v1/write") })
    check("proxy: odczyt przechodzi", px.handle("GET", "/api/v1/states", "").status == 200)
    gate2.unlock()
    check("proxy: po odblokowaniu zapis dociera", px.handle("POST", "/api/v1/write", "{\"id\":\"x\"}").status == 200 && be.seen.any { it.contains("/api/v1/write") })
    px.handle("POST", "/api/v1/pair", "{\"password\":\"p\"}")
    px.handle("GET", "/api/v1/info", "")
    check("proxy: token urządzenia doklejany po parowaniu", be.seen.last().contains("auth=Bearer tok123"), be.seen.last())
    t += 5000
    be.online = false
    val off = px.handle("GET", "/api/v1/states", "")
    check("proxy: offline – ostatnie dane z cache", off.status == 200 && off.cachedAt > 0 && off.body.contains("71.6"), "${off.status} ${off.cachedAt}")
    check("proxy: godzina zapisu zachowana", off.cachedAt == tSave, off.cachedAt.toString())
    check("proxy: offline bez cache -> 503", px.handle("GET", "/api/v1/points", "").status == 503)
    check("proxy: offline zapis -> 503 (nic nie czeka w kolejce)", px.handle("POST", "/api/v1/write", "{}").status == 503)
    be.online = true; be.seen.clear()
    px.dropBoilerLevel()
    check("proxy: blokada zdejmuje poziom kotła (unlock pin 0)", be.seen.any { it.contains("unlock") && it.contains("\"pin\":0") })
    dir.deleteRecursively()

    println(if (failures == 0) "\nWSZYSTKO OK" else "\nNIEPOWODZENIA: $failures")
    kotlin.system.exitProcess(if (failures == 0) 0 else 1)
}
