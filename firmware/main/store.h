#pragma once
// Pamięć trwała (NVS): ustawienia Wi-Fi, konfiguracja urządzenia, hasło (haszowane) i sparowani klienci.
#include <string>
#include <vector>
#include "api.h"
#include "clients.h"

struct Settings {
    std::string ssid, pass;
    bool dhcp = true;
    std::string ip, gw, mask, dns;
    tpc::DeviceConfig cfg;     // domyślnie: tylko odczyt
    bool firstboot_done = false;
};

class NvsStore : public tpc::ClientStore {
public:
    bool init();                       // nvs_flash_init (z kasowaniem przy uszkodzeniu)
    Settings load();
    void save(const Settings& s);
    void factory_reset();

    // ClientStore
    bool has_password() const override;
    bool set_password(const std::string& pw) override;
    bool check_password(const std::string& pw) const override;
    bool valid_token(const std::string& token) const override;
    std::vector<tpc::ClientInfo> list() const override;
    bool put(const tpc::ClientInfo& c) override;
    bool remove(const std::string& id) override;
};
