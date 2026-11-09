package pl.gieoerzet.teklapelletcan

import java.security.SecureRandom
import javax.crypto.SecretKeyFactory
import javax.crypto.spec.PBEKeySpec

/** Minimalny magazyn klucz-wartość (SharedPreferences na telefonie, mapa w testach). */
interface KV {
    fun getString(k: String): String?
    fun putString(k: String, v: String?)
    fun getLong(k: String, d: Long): Long
    fun putLong(k: String, v: Long)
}

class MemoryKV : KV {
    private val m = HashMap<String, Any?>()
    override fun getString(k: String) = m[k] as String?
    override fun putString(k: String, v: String?) { m[k] = v }
    override fun getLong(k: String, d: Long) = (m[k] as Long?) ?: d
    override fun putLong(k: String, v: Long) { m[k] = v }
}

/** PIN aplikacji: zapis jako skrót PBKDF2 z solą, rosnąca blokada po błędnych próbach. */
class SecurityStore(private val kv: KV, private val clock: () -> Long = { System.currentTimeMillis() }) {
    sealed class Check {
        object Ok : Check()
        class Wrong(val attemptsLeft: Int) : Check()
        class Locked(val untilMs: Long) : Check()
    }

    companion object {
        const val MIN_LEN = 4
        const val MAX_LEN = 12
        private const val ITER = 120_000
        const val MAX_FREE_ATTEMPTS = 5
    }

    private fun derive(pin: String, salt: ByteArray): ByteArray {
        val f = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")
        return f.generateSecret(PBEKeySpec(pin.toCharArray(), salt, ITER, 256)).encoded
    }

    private fun hex(b: ByteArray) = b.joinToString("") { "%02x".format(it) }
    private fun unhex(s: String) = ByteArray(s.length / 2) { s.substring(it * 2, it * 2 + 2).toInt(16).toByte() }

    fun hasPin(): Boolean = kv.getString("pin_hash") != null

    /** Zwraca null przy sukcesie albo komunikat błędu (zły format). */
    fun setPin(pin: String): String? {
        if (pin.length < MIN_LEN || pin.length > MAX_LEN || !pin.all { it.isDigit() }) return "PIN: ${MIN_LEN}–$MAX_LEN cyfr"
        val salt = ByteArray(16).also { SecureRandom().nextBytes(it) }
        kv.putString("pin_salt", hex(salt))
        kv.putString("pin_hash", hex(derive(pin, salt)))
        kv.putLong("pin_fails", 0); kv.putLong("pin_lock_until", 0)
        return null
    }

    fun verify(pin: String): Check {
        val now = clock()
        val until = kv.getLong("pin_lock_until", 0)
        if (until > now) return Check.Locked(until)
        val h = kv.getString("pin_hash") ?: return Check.Wrong(0)
        val salt = unhex(kv.getString("pin_salt") ?: return Check.Wrong(0))
        val ok = java.security.MessageDigest.isEqual(unhex(h), derive(pin, salt))
        if (ok) { kv.putLong("pin_fails", 0); return Check.Ok }
        val fails = kv.getLong("pin_fails", 0) + 1
        kv.putLong("pin_fails", fails)
        if (fails >= MAX_FREE_ATTEMPTS) {
            // 5 prób bez kary, potem 30 s, 60 s, 120 s … (max 1 h)
            val step = minOf(3_600_000L, 30_000L shl minOf(10L, fails - MAX_FREE_ATTEMPTS).toInt())
            val lockUntil = now + step
            kv.putLong("pin_lock_until", lockUntil)
            return Check.Locked(lockUntil)
        }
        return Check.Wrong((MAX_FREE_ATTEMPTS - fails).toInt())
    }

    var biometricEnabled: Boolean
        get() = kv.getString("bio") == "1"
        set(v) { kv.putString("bio", if (v) "1" else "0") }

    /** Czy pytanie o biometrię już zadano (pierwsze uruchomienie). */
    var biometricAsked: Boolean
        get() = kv.getString("bio_asked") == "1"
        set(v) { kv.putString("bio_asked", if (v) "1" else "0") }

    var lockOnStart: Boolean
        get() = kv.getString("lock_start") == "1"
        set(v) { kv.putString("lock_start", if (v) "1" else "0") }

    fun reset() { for (k in listOf("pin_hash", "pin_salt", "pin_fails", "pin_lock_until", "bio", "bio_asked")) kv.putString(k, null) }
}

/**
 * Bramka zapisu: aplikacja jest domyślnie w trybie podglądu. Odblokowanie (PIN/odcisk) działa timeoutMs od ostatniej aktywności;
 * wyłączenie ekranu lub wyjście z aplikacji blokuje od razu. Bramka decyduje, które żądania do urządzenia wolno wysłać.
 */
class WriteGate(private val clock: () -> Long = { System.currentTimeMillis() }, private val timeoutMs: Long = 300_000) {
    private var lastActive = 0L
    private var open = false

    @Synchronized fun unlock() { open = true; lastActive = clock() }
    @Synchronized fun lock() { open = false }
    @Synchronized fun touch() { if (isUnlockedLocked()) lastActive = clock() }
    @Synchronized fun isUnlocked(): Boolean = isUnlockedLocked()
    @Synchronized fun remainingMs(): Long = if (isUnlockedLocked()) maxOf(0, timeoutMs - (clock() - lastActive)) else 0

    private fun isUnlockedLocked(): Boolean {
        if (open && clock() - lastActive >= timeoutMs) open = false
        return open
    }

    /** true = zmiana stanu z odblokowanego na zablokowany od ostatniego wywołania (do powiadomienia interfejsu). */
    @Synchronized fun pollExpired(wasOpen: Boolean): Boolean = wasOpen && !isUnlockedLocked()

    companion object {
        /** Wywołania usług, które tylko odświeżają/odczytują (wolne w trybie podglądu). */
        private val READ_ONLY_SERVICE = Regex("_(param_refresh|alarm_refresh|schedule_refresh|test_refresh|sdo_read|sdo_scan_stop)$")

        /** Czy żądanie wolno wysłać do urządzenia przy zablokowanej aplikacji. */
        fun allowedWhenLocked(method: String, path: String, body: String): Boolean {
            if (method == "GET") return true
            if (path == "/api/v1/pair") return true                    // parowanie z urządzeniem nie zmienia kotła
            if (path == "/api/v1/call") {
                val svc = Regex("\"service\"\\s*:\\s*\"([^\"]+)\"").find(body)?.groupValues?.get(1) ?: return false
                return READ_ONLY_SERVICE.containsMatchIn(svc)
            }
            return false
        }
    }
}
