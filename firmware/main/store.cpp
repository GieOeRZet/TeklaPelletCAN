#include "store.h"
#include <cstdio>
#include <cstring>
#include "esp_log.h"
#include "esp_random.h"
#include "mbedtls/sha256.h"
#include "nvs.h"
#include "nvs_flash.h"

static const char* TAG = "store";
static const char* NS = "tpc";
constexpr int kMaxClients = 8;

namespace {
std::string get_str(nvs_handle_t h, const char* key) {
    size_t n = 0;
    if (nvs_get_str(h, key, nullptr, &n) != ESP_OK || n == 0) return "";
    std::string s(n, '\0');
    if (nvs_get_str(h, key, &s[0], &n) != ESP_OK) return "";
    s.resize(n > 0 ? n - 1 : 0);
    return s;
}
uint8_t get_u8(nvs_handle_t h, const char* key, uint8_t def) { uint8_t v = def; nvs_get_u8(h, key, &v); return v; }

std::string sha_hex(const std::string& in) {
    uint8_t out[32];
    mbedtls_sha256((const unsigned char*)in.data(), in.size(), out, 0);
    char hex[65];
    for (int i = 0; i < 32; i++) snprintf(hex + 2 * i, 3, "%02x", out[i]);
    return hex;
}
std::string rand_hex(int bytes) {
    std::string s;
    for (int i = 0; i < bytes; i++) { char b[3]; snprintf(b, sizeof b, "%02x", (unsigned)(esp_random() & 0xFF)); s += b; }
    return s;
}
struct Nvs {
    nvs_handle_t h = 0;
    explicit Nvs(bool rw) { if (nvs_open(NS, rw ? NVS_READWRITE : NVS_READONLY, &h) != ESP_OK) h = 0; }
    ~Nvs() { if (h) nvs_close(h); }
    explicit operator bool() const { return h != 0; }
};
}  // namespace

bool NvsStore::init() {
    esp_err_t e = nvs_flash_init();
    if (e == ESP_ERR_NVS_NO_FREE_PAGES || e == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_LOGW(TAG, "NVS uszkodzony/inny format – kasuję i inicjuję od nowa");
        nvs_flash_erase();
        e = nvs_flash_init();
    }
    return e == ESP_OK;
}

Settings NvsStore::load() {
    Settings s;
    Nvs n(false);
    if (!n) return s;
    s.ssid = get_str(n.h, "ssid"); s.pass = get_str(n.h, "wpass");
    s.dhcp = get_u8(n.h, "dhcp", 1) != 0;
    s.ip = get_str(n.h, "ip"); s.gw = get_str(n.h, "gw"); s.mask = get_str(n.h, "mask"); s.dns = get_str(n.h, "dns");
    s.cfg.mirror = get_u8(n.h, "mirror", 1) != 0;        // domyślnie TYLKO ODCZYT
    s.cfg.write_enabled = get_u8(n.h, "write", 1) != 0;
    s.cfg.demo = get_u8(n.h, "demo", 0) != 0;
    s.cfg.two_circuits = get_u8(n.h, "two", 0) != 0;
    s.cfg.external_antenna = get_u8(n.h, "ant", 0) != 0;
    s.firstboot_done = get_u8(n.h, "fb_done", 0) != 0;
    nvs_get_u32(n.h, "fb_serial", &s.fb_serial);
    return s;
}

void NvsStore::save(const Settings& s) {
    Nvs n(true);
    if (!n) return;
    nvs_set_str(n.h, "ssid", s.ssid.c_str()); nvs_set_str(n.h, "wpass", s.pass.c_str());
    nvs_set_u8(n.h, "dhcp", s.dhcp); nvs_set_str(n.h, "ip", s.ip.c_str()); nvs_set_str(n.h, "gw", s.gw.c_str());
    nvs_set_str(n.h, "mask", s.mask.c_str()); nvs_set_str(n.h, "dns", s.dns.c_str());
    nvs_set_u8(n.h, "mirror", s.cfg.mirror); nvs_set_u8(n.h, "write", s.cfg.write_enabled);
    nvs_set_u8(n.h, "demo", s.cfg.demo); nvs_set_u8(n.h, "two", s.cfg.two_circuits); nvs_set_u8(n.h, "ant", s.cfg.external_antenna);
    nvs_set_u8(n.h, "fb_done", s.firstboot_done);
    nvs_commit(n.h);
}

void NvsStore::save_wifi(const Settings& s) {
    Nvs n(true);
    if (!n) return;
    nvs_set_str(n.h, "ssid", s.ssid.c_str()); nvs_set_str(n.h, "wpass", s.pass.c_str());
    nvs_set_u8(n.h, "dhcp", s.dhcp); nvs_set_str(n.h, "ip", s.ip.c_str()); nvs_set_str(n.h, "gw", s.gw.c_str());
    nvs_set_str(n.h, "mask", s.mask.c_str()); nvs_set_str(n.h, "dns", s.dns.c_str());
    nvs_commit(n.h);
}

void NvsStore::save_cfg(const tpc::DeviceConfig& c, bool firstboot_done) {
    Nvs n(true);
    if (!n) return;
    nvs_set_u8(n.h, "mirror", c.mirror); nvs_set_u8(n.h, "write", c.write_enabled);
    nvs_set_u8(n.h, "demo", c.demo); nvs_set_u8(n.h, "two", c.two_circuits); nvs_set_u8(n.h, "ant", c.external_antenna);
    nvs_set_u8(n.h, "fb_done", firstboot_done);
    nvs_commit(n.h);
}

void NvsStore::save_fb_serial(uint32_t serial) {
    Nvs n(true);
    if (!n) return;
    nvs_set_u32(n.h, "fb_serial", serial);
    nvs_commit(n.h);
}

void NvsStore::factory_reset() {
    Nvs n(true);
    if (n) { nvs_erase_all(n.h); nvs_commit(n.h); }
}

bool NvsStore::has_password() const { Nvs n(false); return n && !get_str(n.h, "pw_h").empty(); }

bool NvsStore::set_password(const std::string& pw) {
    Nvs n(true);
    if (!n) return false;
    const std::string salt = rand_hex(8);
    nvs_set_str(n.h, "pw_s", salt.c_str());
    nvs_set_str(n.h, "pw_h", sha_hex(salt + pw).c_str());
    return nvs_commit(n.h) == ESP_OK;
}

bool NvsStore::check_password(const std::string& pw) const {
    Nvs n(false);
    if (!n) return false;
    const std::string h = get_str(n.h, "pw_h");
    return !h.empty() && h == sha_hex(get_str(n.h, "pw_s") + pw);
}

std::vector<tpc::ClientInfo> NvsStore::list() const {
    std::vector<tpc::ClientInfo> v;
    Nvs n(false);
    if (!n) return v;
    for (int i = 0; i < kMaxClients; i++) {
        char k[16];
        snprintf(k, sizeof k, "c%di", i); std::string id = get_str(n.h, k);
        if (id.empty()) continue;
        tpc::ClientInfo c; c.id = id;
        snprintf(k, sizeof k, "c%dn", i); c.name = get_str(n.h, k);
        snprintf(k, sizeof k, "c%dt", i); c.token = get_str(n.h, k);
        v.push_back(c);
    }
    return v;
}

bool NvsStore::valid_token(const std::string& token) const {
    if (token.size() < 16) return false;
    for (auto& c : list()) if (c.token == token) return true;
    return false;
}

bool NvsStore::put(const tpc::ClientInfo& c) {
    Nvs n(true);
    if (!n) return false;
    int slot = -1, freeslot = -1;
    for (int i = 0; i < kMaxClients; i++) {
        char k[16]; snprintf(k, sizeof k, "c%di", i);
        std::string id = get_str(n.h, k);
        if (id == c.id) { slot = i; break; }
        if (id.empty() && freeslot < 0) freeslot = i;
    }
    if (slot < 0) slot = freeslot;
    if (slot < 0) { ESP_LOGW(TAG, "brak miejsca na kolejnego klienta (max %d)", kMaxClients); return false; }
    char k[16];
    snprintf(k, sizeof k, "c%di", slot); nvs_set_str(n.h, k, c.id.c_str());
    snprintf(k, sizeof k, "c%dn", slot); nvs_set_str(n.h, k, c.name.c_str());
    snprintf(k, sizeof k, "c%dt", slot); nvs_set_str(n.h, k, c.token.c_str());
    return nvs_commit(n.h) == ESP_OK;
}

bool NvsStore::remove(const std::string& id) {
    Nvs n(true);
    if (!n) return false;
    for (int i = 0; i < kMaxClients; i++) {
        char k[16]; snprintf(k, sizeof k, "c%di", i);
        if (get_str(n.h, k) == id) {
            nvs_erase_key(n.h, k);
            snprintf(k, sizeof k, "c%dn", i); nvs_erase_key(n.h, k);
            snprintf(k, sizeof k, "c%dt", i); nvs_erase_key(n.h, k);
            return nvs_commit(n.h) == ESP_OK;
        }
    }
    return false;
}
