#pragma once
#include <string>
#include <vector>
#include "api.h"
#include "antenna.h"
#include "net_fsm.h"
#include "store.h"

// Zarządca Wi-Fi: STA z zapisaną siecią, a przy braku/utracie sieci – własny punkt dostępu (AP) z portalem.
// Logika przełączania jest w tpc::NetFsm (testowana na hoście); tu tylko sterowanie esp_wifi.
class WifiMgr {
public:
    void start(const Settings& s, NvsStore& store);
    std::vector<tpc::WifiNet> scan();
    void apply(const tpc::WifiSettings& w);          // próbne połączenie z nowymi danymi (AP zostaje do końca testu)
    tpc::WifiStatus status();
    std::string ip();
    bool online();
    std::string ap_ssid() const { return ap_ssid_; }
    std::string hostname() const { return hostname_; }
    std::string mac_hex() const { return mac_hex_; }
    static void task_entry(void* arg);

private:
    void run();
    void set_mode(bool ap_on);
    void connect_sta(const Settings& s);
    static void on_event(void* arg, const char* base, int32_t id, void* data);

    NvsStore* store_ = nullptr;
    Settings cur_, pending_, prev_;
    bool has_pending_ = false;
    tpc::NetFsm fsm_;
    tpc::AntennaFailover ant_{false};
    static void set_antenna_hw(bool external);
    std::string ap_ssid_, hostname_, mac_hex_, ip_str_, trial_;
    bool connected_ = false, ap_active_ = false, started_ = false;
    bool assoc_ = false;                 // czy jest skojarzenie z AP routera (zdarzenie STA_CONNECTED)
    bool connect_pending_ = false;       // próba połączenia odroczona, żeby odpowiedź HTTP zdążyła wyjść
    uint32_t connect_at_ = 0;
    std::string static_ip_;              // niepusty = bieżąca próba ze stałym IP
    int rssi_ = 0;
    uint32_t last_try_ms_ = 0;
    void* mu_ = nullptr;
};

extern WifiMgr g_wifi;
