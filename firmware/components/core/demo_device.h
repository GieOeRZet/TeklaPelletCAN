#pragma once
// Wirtualne urządzenie do trybu DEMO (aplikacja Android, symulator na hoście): prawdziwy Engine + Api (ten sam kod co na ESP),
// atrapa kotła z „żywą” fizyką (temperatury, modulacja, paliwo) i atrapy hooków platformy (Wi‑Fi, konfiguracja, dziennik).
// Bez zależności od mbedTLS i od systemu operacyjnego – kompiluje się także w NDK.
#include <chrono>
#include <memory>
#include <mutex>
#include <random>
#include <string>
#include "api.h"
#include "logring.h"
#include "sim_boiler.h"

namespace tpc {

class DemoDevice {
public:
    explicit DemoDevice(const std::string& fw = "demo");
    ~DemoDevice();

    // Obsługa żądania REST (/api/v1/...). Bez nagłówka Authorization dokłada token sparowanego „klienta demo”,
    // więc w trybie demo wszystko działa bez parowania (PIN-y poziomów 0900/0999 nadal obowiązują).
    HttpResponse handle(const HttpRequest& req);
    void tick();                       // silnik + fizyka kotła; wołać co kilka ms (można rzadziej – nadrabia)
    uint32_t now_ms() const;

private:
    void physics(uint32_t t);
    void tick_nolock();

    std::mutex mu_;
    std::chrono::steady_clock::time_point t0_;
    SimBoiler boiler_;
    uint8_t dev_[6];
    std::unique_ptr<Engine> engine_;
    MemoryClientStore clients_;
    std::mt19937 rng_;
    std::unique_ptr<Api> api_;
    uint8_t ring_mem_[8192];
    std::unique_ptr<LogRing> ring_;
    DeviceConfig devcfg_;
    WifiStatus wst_;
    uint32_t trial_at_ = 0;
    bool trial_pending_ = false;
    std::string trial_ssid_;
    std::string token_;
    uint32_t last_phys_ = 0;
    double fuel_ = 180;
    uint32_t last_pdo_ = 0;
    uint32_t skew_ = 0;                // przesunięcie czasu wirtualnego (rozgrzewka)
    bool blower_on_ = true, feeder_on_ = false;
};

}  // namespace tpc
