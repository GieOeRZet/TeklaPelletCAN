#pragma once
// Router API urządzenia (REST) – czysty C++: ten sam kod działa na ESP (esp_http_server) i na hoście (testy, symulator).
#include <functional>
#include <map>
#include <string>
#include <vector>
#include "clients.h"
#include "engine.h"

namespace tpc {

struct HttpRequest {
    std::string method;                              // GET, POST, DELETE
    std::string path;                                // bez zapytania
    std::string query;                               // po '?'
    std::string body;
    std::map<std::string, std::string> headers;      // klucze małymi literami
};

struct HttpResponse {
    int status = 200;
    std::string ctype = "application/json";
    std::string body;
    std::map<std::string, std::string> headers;      // dodatkowe nagłówki (np. Content-Disposition)
};

// Dane z platformy (ESP / symulator) – Api zostaje czystym C++.
struct WifiNet { std::string ssid; int rssi = 0; bool secure = true; };
struct WifiSettings {
    std::string ssid, password;
    bool dhcp = true;
    std::string ip, gateway, mask, dns;
};
struct WifiStatus {
    std::string state;        // provisioning | connecting | online | fallback | trial
    std::string ssid, ip, ap_ssid;
    int rssi = 0;
    bool ap_active = false;
    std::string trial;        // "" | "ok" | "failed" (wynik ostatniego testu nowych danych)
};
struct DeviceConfig {
    bool mirror = true;       // domyślnie TYLKO ODCZYT (bezpiecznie po pierwszym wgraniu)
    bool write_enabled = true;
    bool demo = false;        // symulator kotła (bez CAN)
    bool two_circuits = false;
    bool external_antenna = false;   // XIAO ESP32-C6: antena zewnętrzna U.FL (GPIO3/GPIO14)
    bool web_open = true;            // panel WWW (strony urządzenia) bez hasła w sieci lokalnej; hasło służy do parowania HA/aplikacji
};
struct ApiHooks {
    std::function<std::vector<WifiNet>()> scan;
    std::function<void(const WifiSettings&)> wifi_apply;
    std::function<WifiStatus()> wifi_status;
    std::function<DeviceConfig()> config_get;
    std::function<void(const DeviceConfig&)> config_set;     // zapis do pamięci trwałej; zmiana wymaga restartu
    std::function<std::string(size_t)> log_get;              // ostatnie N bajtów dziennika (0 = całość)
    std::function<void()> log_clear;
    std::function<std::string()> diag_extra;                 // obiekt JSON z danymi platformy (heap, reset, Wi-Fi...)
    std::function<void()> factory_reset;
    std::function<std::string()> ota_rollback;               // zwraca "" gdy OK albo komunikat błędu (powrót do poprzedniej partycji)
};

struct ApiConfig {
    std::string prefix = "tekla";                    // prefiks entity_id wystawianych encji
    std::string node = "tekla_estyma";               // nazwa węzła w usługach karty
    std::string fw = "0.1.0";
    bool dev_key = false;
};

class Api {
public:
    using Clock = std::function<uint32_t()>;               // ms od startu
    using Random = std::function<std::string(size_t)>;     // losowe znaki hex (tokeny)
    using Hook = std::function<void()>;

    Api(Engine& engine, ClientStore& clients, ApiConfig cfg, Clock clock, Random rnd)
        : e_(engine), c_(clients), cfg_(std::move(cfg)), clock_(std::move(clock)), rnd_(std::move(rnd)) {}

    HttpResponse handle(const HttpRequest& r);
    void on_restart(Hook h) { restart_ = std::move(h); }
    void set_hooks(ApiHooks h) { hooks_ = std::move(h); }
    bool is_authorized(const HttpRequest& r) const { return authorized(r); }   // dla strumieniowego OTA
    const ApiConfig& config() const { return cfg_; }

private:
    bool authorized(const HttpRequest& r) const;      // token sparowanego klienta ALBO otwarty panel WWW (ten sam origin)
    bool web_open() const { return hooks_.config_get && hooks_.config_get().web_open; }
    HttpResponse err(int status, const std::string& code) const;
    HttpResponse call(const HttpRequest& r);
    HttpResponse pair(const HttpRequest& r);
    std::string find_entity(const std::string& domain, const std::string& id) const;

    Engine& e_;
    ClientStore& c_;
    ApiConfig cfg_;
    Clock clock_;
    Random rnd_;
    Hook restart_;
    ApiHooks hooks_;
    HttpResponse platform(const HttpRequest& r, bool& handled);
};

}  // namespace tpc
