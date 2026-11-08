#include "wifi_mgr.h"
#include <algorithm>
#include <cstring>
#include "driver/gpio.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_mac.h"
#include "esp_netif.h"
#include "esp_timer.h"
#include "esp_wifi.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "lwip/inet.h"
#include "lwip/sockets.h"
#include "dns.h"
#include "logging.h"

static const char* TAG = "wifi";
WifiMgr g_wifi;
static esp_netif_t *g_sta = nullptr, *g_ap = nullptr;
static const char* kApIpStr = "10.77.77.1";   // podsieć AP inna niż typowe sieci domowe (192.168.x.x)
static const char* kApPassword = "qwerty123";     // domyślne hasło AP (decyzja właściciela; AP działa tylko do skonfigurowania sieci)

static uint32_t now_ms() { return (uint32_t)(esp_timer_get_time() / 1000); }

struct Lock {
    SemaphoreHandle_t m;
    explicit Lock(void* mu) : m((SemaphoreHandle_t)mu) { xSemaphoreTake(m, portMAX_DELAY); }
    ~Lock() { xSemaphoreGive(m); }
};

void WifiMgr::on_event(void* arg, const char* base, int32_t id, void* data) {
    WifiMgr* w = (WifiMgr*)arg;
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_CONNECTED) {
        Lock l(w->mu_);
        w->assoc_ = true;
        if (!w->static_ip_.empty()) {      // stały IP: GOT_IP bywa zgłaszany jeszcze przed skojarzeniem, więc „online" ustalamy tutaj
            w->connected_ = true;
            w->ip_str_ = w->static_ip_;
            w->fsm_.on_sta_connected(now_ms());
            log_add("Wi-Fi: polaczono, IP " + w->static_ip_ + " (stale)");
        }
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        Lock l(w->mu_);
        w->assoc_ = false;
        if (w->connected_) log_add("Wi-Fi: rozlaczono z siecia");
        w->connected_ = false;
        w->ip_str_.clear();
        w->fsm_.on_sta_disconnected(now_ms());
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        auto* ev = (ip_event_got_ip_t*)data;
        char b[16];
        esp_ip4addr_ntoa(&ev->ip_info.ip, b, sizeof b);
        Lock l(w->mu_);
        if (!w->assoc_ || !w->static_ip_.empty()) return;   // tylko po prawdziwym skojarzeniu (DHCP); przy stałym IP obsłużone wyżej
        w->connected_ = true;
        w->ip_str_ = b;
        w->fsm_.on_sta_connected(now_ms());
        log_add(std::string("Wi-Fi: polaczono, IP ") + b);
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_AP_STACONNECTED) {
        log_add("AP: klient polaczony z punktem dostepu");
    }
}

// XIAO ESP32-C6: GPIO3 = zasilanie przełącznika RF (niski = aktywny), GPIO14 = wybór anteny (wysoki = zewnętrzna U.FL, niski = wewnętrzna)
void WifiMgr::set_antenna_hw(bool external) {
    gpio_config_t ac = {};
    ac.pin_bit_mask = (1ULL << 3) | (1ULL << 14); ac.mode = GPIO_MODE_OUTPUT;
    gpio_config(&ac);
    gpio_set_level(GPIO_NUM_3, 0);
    vTaskDelay(pdMS_TO_TICKS(100));
    gpio_set_level(GPIO_NUM_14, external ? 1 : 0);
}

void WifiMgr::start(const Settings& s, NvsStore& store) {
    store_ = store_ ? store_ : &store;
    cur_ = s;
    mu_ = xSemaphoreCreateMutex();
    ant_ = tpc::AntennaFailover(s.cfg.external_antenna);
    if (s.cfg.external_antenna) { set_antenna_hw(true); log_add("Antena: zewnetrzna (U.FL)"); }
    uint8_t mac[6];
    esp_read_mac(mac, ESP_MAC_WIFI_STA);
    char b[16];
    snprintf(b, sizeof b, "%02X%02X%02X%02X%02X%02X", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
    mac_hex_ = b;
    snprintf(b, sizeof b, "%02X%02X", mac[4], mac[5]);
    ap_ssid_ = std::string("TeklaPelletCAN-") + b;
    snprintf(b, sizeof b, "%02x%02x%02x", mac[3], mac[4], mac[5]);
    hostname_ = std::string("teklapelletcan-") + b;

    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    g_sta = esp_netif_create_default_wifi_sta();
    g_ap = esp_netif_create_default_wifi_ap();
    {   // AP w podsieci 10.77.77.0/24 (domyślne 192.168.4.x kolidowało z siecią IoT użytkownika)
        esp_netif_dhcps_stop(g_ap);
        esp_netif_ip_info_t ii = {};
        ii.ip.addr = esp_ip4addr_aton(kApIpStr); ii.gw.addr = ii.ip.addr; ii.netmask.addr = esp_ip4addr_aton("255.255.255.0");
        esp_netif_set_ip_info(g_ap, &ii);
        esp_netif_dns_info_t d = {};
        d.ip.type = ESP_IPADDR_TYPE_V4; d.ip.u_addr.ip4.addr = ii.ip.addr;
        esp_netif_set_dns_info(g_ap, ESP_NETIF_DNS_MAIN, &d);
        uint8_t offer = 1;
        esp_netif_dhcps_option(g_ap, ESP_NETIF_OP_SET, ESP_NETIF_DOMAIN_NAME_SERVER, &offer, sizeof offer);
        esp_netif_dhcps_start(g_ap);
    }
    esp_netif_set_hostname(g_sta, hostname_.c_str());
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    esp_wifi_set_storage(WIFI_STORAGE_RAM);          // dane sieci trzymamy w NVS aplikacji, nie w sterowniku
    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &WifiMgr::on_event, this));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, &WifiMgr::on_event, this));
    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, WIFI_EVENT_STA_CONNECTED, &WifiMgr::on_event, this));

    wifi_config_t ap = {};
    strncpy((char*)ap.ap.ssid, ap_ssid_.c_str(), sizeof ap.ap.ssid - 1);
    ap.ap.ssid_len = (uint8_t)ap_ssid_.size();
    strncpy((char*)ap.ap.password, kApPassword, sizeof ap.ap.password - 1);
    ap.ap.channel = 1;
    ap.ap.max_connection = 4;
    ap.ap.authmode = WIFI_AUTH_WPA2_PSK;
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_APSTA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &ap));
    ESP_ERROR_CHECK(esp_wifi_start());
    esp_wifi_set_ps(WIFI_PS_NONE);                   // bez oszczędzania energii: stabilny serwer HTTP/mDNS
    ap_active_ = true;

    fsm_.begin(!cur_.ssid.empty(), now_ms());
    if (!cur_.ssid.empty()) connect_sta(cur_);
    log_add("Wi-Fi: start, AP '" + ap_ssid_ + "', sieci zapisanej: " + (cur_.ssid.empty() ? "brak" : cur_.ssid));
    started_ = true;
    xTaskCreate(&WifiMgr::task_entry, "wifi_mgr", 6144, this, 5, nullptr);
}

void WifiMgr::task_entry(void* arg) { ((WifiMgr*)arg)->run(); }

void WifiMgr::set_mode(bool ap_on) {
    if (ap_on == ap_active_) return;
    ap_active_ = ap_on;
    esp_wifi_set_mode(ap_on ? WIFI_MODE_APSTA : WIFI_MODE_STA);
    log_add(ap_on ? "AP: wlaczony punkt dostepu (portal konfiguracji)" : "AP: wylaczony (siec dziala)");
}

void WifiMgr::connect_sta(const Settings& s) {
    if (s.ssid.empty()) return;
    static_ip_ = (!s.dhcp && !s.ip.empty()) ? s.ip : "";
    assoc_ = false;
    wifi_config_t sta = {};
    strncpy((char*)sta.sta.ssid, s.ssid.c_str(), sizeof sta.sta.ssid - 1);
    strncpy((char*)sta.sta.password, s.pass.c_str(), sizeof sta.sta.password - 1);
    sta.sta.threshold.authmode = s.pass.empty() ? WIFI_AUTH_OPEN : WIFI_AUTH_WPA_PSK;   // akceptuj WPA/WPA2/WPA3
    sta.sta.pmf_cfg.capable = true;
    if (!s.dhcp && !s.ip.empty()) {
        esp_netif_dhcpc_stop(g_sta);
        esp_netif_ip_info_t ii = {};
        ii.ip.addr = esp_ip4addr_aton(s.ip.c_str());
        ii.gw.addr = esp_ip4addr_aton(s.gw.c_str());
        ii.netmask.addr = esp_ip4addr_aton(s.mask.empty() ? "255.255.255.0" : s.mask.c_str());
        esp_netif_set_ip_info(g_sta, &ii);
        esp_netif_dns_info_t d = {};
        d.ip.type = ESP_IPADDR_TYPE_V4;
        d.ip.u_addr.ip4.addr = esp_ip4addr_aton(s.dns.empty() ? (s.gw.empty() ? "8.8.8.8" : s.gw.c_str()) : s.dns.c_str());
        esp_netif_set_dns_info(g_sta, ESP_NETIF_DNS_MAIN, &d);
    } else {
        esp_netif_dhcpc_start(g_sta);
    }
    esp_wifi_disconnect();
    esp_wifi_set_config(WIFI_IF_STA, &sta);
    esp_wifi_connect();
    last_try_ms_ = now_ms();
    log_add("Wi-Fi: lacze z '" + s.ssid + "'" + (s.dhcp ? " (DHCP)" : " (stale IP " + s.ip + ")"));
}

void WifiMgr::run() {
    // serwer DNS portalu (UDP 53): w trybie AP kieruje każdą nazwę na 10.77.77.1
    int dns = socket(AF_INET, SOCK_DGRAM, 0);
    sockaddr_in a = {};
    a.sin_family = AF_INET; a.sin_port = htons(53); a.sin_addr.s_addr = htonl(INADDR_ANY);
    bool dns_ok = dns >= 0 && bind(dns, (sockaddr*)&a, sizeof a) == 0;
    if (dns_ok) { timeval tv{0, 200000}; setsockopt(dns, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof tv); }
    else ESP_LOGW(TAG, "DNS portalu: nie udalo sie otworzyc gniazda");

    uint8_t qbuf[300];
    uint32_t last_fsm = 0;
    for (;;) {
        if (dns_ok) {
            sockaddr_in from; socklen_t fl = sizeof from;
            int n = recvfrom(dns, qbuf, sizeof qbuf, 0, (sockaddr*)&from, &fl);
            if (n > 0 && ap_active_) {
                auto resp = tpc::dns_captive_response(qbuf, (size_t)n, (10u << 24) | (77u << 16) | (77u << 8) | 1u);
                if (!resp.empty()) sendto(dns, resp.data(), resp.size(), 0, (sockaddr*)&from, fl);
            }
        } else {
            vTaskDelay(pdMS_TO_TICKS(200));
        }
        const uint32_t t = now_ms();
        if (t - last_fsm < 500) continue;
        last_fsm = t;

        if (connect_pending_ && t >= connect_at_) {
            Settings s;
            { Lock l(mu_); s = pending_; connect_pending_ = false; }
            connect_sta(s);
        }
        tpc::NetOutput o;
        {
            Lock l(mu_);
            o = fsm_.tick(t);
            if (o.trial_ok && has_pending_) {           // nowe dane zadziałały – zapisz na stałe
                cur_ = pending_; has_pending_ = false; trial_ = "ok";
                if (store_) store_->save_wifi(cur_);
                log_add("Wi-Fi: nowe dane sieci zapisane");
            }
            if (o.trial_failed) {
                trial_ = "failed"; has_pending_ = false;
                log_add("Wi-Fi: proba z nowymi danymi nieudana");
            }
        }
        if (o.trial_failed && o.use_previous_credentials) connect_sta(prev_);
        {   // antena zewnętrzna bez efektu (brak połączenia po całym czasie oczekiwania): przełącz na wewnętrzną i połącz ponownie
            tpc::NetState st; { Lock l(mu_); st = fsm_.state(); }
            tpc::AntennaOut ao = ant_.tick(st);
            if (ao.changed) {
                set_antenna_hw(false);
                log_add("Antena: zewnetrzna nie polaczyla z siecia - przelaczam na wewnetrzna (awaryjnie, do restartu). Sprawdz antene/kabel U.FL");
                Settings s; { Lock l(mu_); s = cur_; }
                if (!s.ssid.empty()) connect_sta(s);
            }
        }
        set_mode(o.ap_on);
        if (connected_) {
            wifi_ap_record_t ap;
            if (esp_wifi_sta_get_ap_info(&ap) == ESP_OK) rssi_ = ap.rssi;
        }
        // ponawianie połączenia co 8 s, gdy STA ma działać, ale nie jest połączone
        if (o.sta_on && !connected_ && !cur_.ssid.empty() && t - last_try_ms_ > 8000) {
            last_try_ms_ = t;
            esp_wifi_connect();
        }
    }
}

std::vector<tpc::WifiNet> WifiMgr::scan() {
    std::vector<tpc::WifiNet> out;
    wifi_scan_config_t sc = {};
    if (esp_wifi_scan_start(&sc, true) != ESP_OK) return out;
    uint16_t n = 20;
    wifi_ap_record_t recs[20];
    if (esp_wifi_scan_get_ap_records(&n, recs) != ESP_OK) return out;
    for (uint16_t i = 0; i < n; i++) {
        std::string ssid((const char*)recs[i].ssid);
        if (ssid.empty()) continue;
        bool dup = false;
        for (auto& e : out) if (e.ssid == ssid) { dup = true; if (recs[i].rssi > e.rssi) e.rssi = recs[i].rssi; }
        if (!dup) out.push_back({ssid, recs[i].rssi, recs[i].authmode != WIFI_AUTH_OPEN});
    }
    return out;
}

void WifiMgr::apply(const tpc::WifiSettings& w) {
    Lock l(mu_);
    prev_ = cur_;
    pending_ = cur_;
    pending_.ssid = w.ssid; pending_.pass = w.password; pending_.dhcp = w.dhcp;
    pending_.ip = w.ip; pending_.gw = w.gateway; pending_.mask = w.mask; pending_.dns = w.dns;
    has_pending_ = true;
    trial_.clear();
    fsm_.on_new_credentials(!prev_.ssid.empty(), now_ms());
    connect_pending_ = true;                 // połączymy za ~1,5 s: najpierw musi wyjść odpowiedź HTTP, bo zmiana sieci zrywa łączność
    connect_at_ = now_ms() + 1500;
    log_add("Wi-Fi: nowe dane przyjete, laczenie za chwile");
}

tpc::WifiStatus WifiMgr::status() {
    Lock l(mu_);
    tpc::WifiStatus s;
    switch (fsm_.state()) {
        case tpc::NetState::Provisioning: s.state = "provisioning"; break;
        case tpc::NetState::Connecting: s.state = "connecting"; break;
        case tpc::NetState::Online: s.state = "online"; break;
        case tpc::NetState::Fallback: s.state = "fallback"; break;
        case tpc::NetState::Trial: s.state = "trial"; break;
    }
    s.ssid = has_pending_ ? pending_.ssid : cur_.ssid;
    s.ip = ip_str_;
    s.ap_ssid = ap_ssid_;
    s.rssi = rssi_;
    s.ap_active = ap_active_;
    s.trial = trial_;
    s.antenna = ant_.using_external() ? "zewnetrzna" : (ant_.auto_fallback() ? "wewnetrzna (awaryjnie)" : "wewnetrzna");
    return s;
}

std::string WifiMgr::ip() { Lock l(mu_); return ip_str_; }
bool WifiMgr::online() { Lock l(mu_); return connected_; }
