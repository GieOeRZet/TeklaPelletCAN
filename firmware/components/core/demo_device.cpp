#include "demo_device.h"
#include <algorithm>
#include <cmath>
#include <cstring>
#include <cstdio>
#include "json_parse.h"

namespace tpc {

DemoDevice::DemoDevice(const std::string& fw) : t0_(std::chrono::steady_clock::now()), rng_(20260101) {
    populate_demo(boiler_);
    boiler_.reg[0x404C] = 256 + 1;                       // ostatni wpis: slot 0 (zakończony) – bez aktywnego alarmu
    boiler_.reg[0x4010] = 2; boiler_.reg[0x4011] = 140;  // historia: przegrzanie, brak ognia (oba zakończone)
    boiler_.reg[0x4025] = 1794150000; boiler_.reg[0x4039] = 1794153600;
    const uint8_t dev[6] = {0xDE, 0x30, 0xDE, 0x30, 0x00, 0x01};
    memcpy(dev_, dev, 6);
    EngineConfig cfg;
    cfg.boot_delay_ms = 300;
    cfg.boot_guard_ms = 0;
    cfg.fw = fw;
    cfg.live_period_ms = 60;            // wirtualny kocioł odpowiada natychmiast, więc odczyty odświeżają się szybciej niż na prawdziwym urządzeniu
    engine_.reset(new Engine(cfg, [this](const CanFrame& f) { return boiler_.on_can(f); }, dev_));
    clients_.set_password("demo");
    ApiConfig acfg; acfg.fw = fw; acfg.dev_key = true;
    api_.reset(new Api(*engine_, clients_, acfg, [this] { return now_ms(); }, [this](size_t n) {
        static const char* hex = "0123456789abcdef"; std::string s;
        for (size_t i = 0; i < n; i++) s += hex[rng_() & 15];
        return s;
    }));
    api_->on_restart([this] { ring_->append("Restart (demo)"); });

    ring_.reset(new LogRing(ring_mem_, sizeof ring_mem_));
    engine_->set_logger([this](const std::string& l) {
        char b[32]; snprintf(b, sizeof b, "[%7.1f] ", now_ms() / 1000.0); ring_->append(std::string(b) + l);
    });
    ring_->append("[    0.0] START (tryb demo – wirtualny kociol)");
    devcfg_.mirror = false;
    devcfg_.demo = true;
    wst_.state = "online"; wst_.ssid = "Siec-Demo"; wst_.ip = "192.168.0.50"; wst_.ap_ssid = "TeklaPelletCAN-DEMO";
    wst_.rssi = -55; wst_.antenna = "wewnetrzna";

    ApiHooks hk;
    hk.scan = [] { return std::vector<WifiNet>{{"Dom-2.4G", -48, true}, {"Sasiad", -77, true}, {"Otwarta", -85, false}}; };
    hk.wifi_apply = [this](const WifiSettings& w) {
        ring_->append("Wi-Fi (demo): proba polaczenia z '" + w.ssid + "'");
        trial_pending_ = true; trial_at_ = now_ms() + 1500; trial_ssid_ = w.ssid; wst_.trial = "";
        if (w.password == "zle") trial_ssid_ = "!";
    };
    hk.wifi_status = [this] {
        if (trial_pending_ && now_ms() >= trial_at_) {
            trial_pending_ = false;
            if (trial_ssid_ == "!") wst_.trial = "failed"; else { wst_.trial = "ok"; wst_.ssid = trial_ssid_; }
        }
        return wst_;
    };
    hk.config_get = [this] { return devcfg_; };
    hk.config_set = [this](const DeviceConfig& c) { devcfg_ = c; devcfg_.demo = true; ring_->append("Konfiguracja zapisana (demo)"); };
    hk.log_get = [this](size_t n) { return n ? ring_->tail(n) : ring_->dump(); };
    hk.log_clear = [this] { ring_->clear(); };
    hk.set_time = [this](int64_t t) { time_off_ = t - (int64_t)(now_ms() / 1000); time_set_ = true; ring_->append("Czas ustawiony przez klienta (demo)"); };
    hk.get_time = [this]() -> int64_t { return time_set_ ? time_off_ + (int64_t)(now_ms() / 1000) : 0; };
    hk.ota_rollback = [] { return std::string("w trybie demo nie ma poprzedniej wersji"); };
    hk.diag_extra = [] { return std::string("{\"heap_free\":210000,\"reset_reason\":\"demo\",\"wifi_rssi\":-55,\"partition\":\"demo\"}"); };
    hk.factory_reset = [this] { ring_->append("Reset fabryczny (demo)"); };
    api_->set_hooks(hk);

    // „sparowany klient demo”: token wstrzykiwany do żądań bez Authorization
    HttpRequest pr; pr.method = "POST"; pr.path = "/api/v1/pair";
    pr.body = "{\"password\":\"demo\",\"client_id\":\"app-demo\",\"name\":\"Aplikacja (demo)\"}";
    Json j;
    if (json_parse(api_->handle(pr).body, j)) token_ = j.str("token");

    // Rozgrzewka: silnik „przeżywa” pierwsze 70 s w przyspieszonym czasie, więc karta od razu pokazuje komplet odczytów.
    while (skew_ < 70000) { skew_ += 2; tick_nolock(); }
    ring_->clear();
    ring_->append("[    0.0] START (tryb demo - wirtualny kociol)");
}

DemoDevice::~DemoDevice() = default;

uint32_t DemoDevice::now_ms() const {
    return skew_ + (uint32_t)std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - t0_).count();
}

// „Żywa” fizyka kotła: temperatury kołyszą się wokół wartości zadanej, modulacja palnika i dmuchawa za nimi,
// paliwo powoli ubywa. Zapisy użytkownika (zadana, tryby, harmonogramy) zostają – zmieniane są tylko wartości mierzone.
void DemoDevice::physics(uint32_t t) {
    if (t - last_phys_ < 1000) return;
    const double dt = (t - last_phys_) / 1000.0;
    last_phys_ = t;
    const double s = t / 1000.0;
    auto reg = [this](uint16_t i, uint32_t def) { auto it = boiler_.reg.find(i); return it == boiler_.reg.end() ? def : it->second; };
    const double set = (double)(reg(0x2003, 70) & 0xFFFF);
    const double on = (reg(0x2005, 257) & 0xFF) ? 1.0 : 0.0;
    const double target = on ? set + 3.0 * std::sin(s / 70.0) + 1.2 * std::sin(s / 13.0) : 38.0 + 2.0 * std::sin(s / 200.0);
    double cur = (double)(int16_t)(reg(0x2001, 700) & 0xFFFF) / 10.0;
    cur += (target - cur) * std::min(1.0, 0.08 * dt);
    boiler_.reg[0x2001] = (uint32_t)(int16_t)std::lround(cur * 10.0) & 0xFFFF;
    const double co = std::max(25.0, cur - 20.0 + 3.0 * std::sin(s / 55.0));
    boiler_.reg[0x4001] = (uint32_t)std::lround(co * 10.0);
    boiler_.reg[0x2110] = (uint32_t)std::lround((co + 3.0) * 10.0);
    boiler_.reg[0x4000] = (uint32_t)std::lround((cur - 12.0 + 0.8 * std::sin(s / 40.0)) * 10.0);
    boiler_.reg[0x215F] = (uint32_t)(int16_t)std::lround((3.8 + 1.5 * std::sin(s / 900.0)) * 10.0) & 0xFFFF;   // temperatura zewnętrzna
    const int state = on ? (cur > set + 2.5 ? 8 : 5) : 0;                   // 5 = modulacja, 8 = pauza (za gorąco), 0 = wyłączony
    boiler_.reg[0x2007] = 256 + (uint32_t)state;
    const double err = set - cur;                                            // modulacja: im zimniej względem zadanej, tym mocniej
    const int mod = state == 5 ? (int)std::lround(std::max(10.0, std::min(100.0, 45.0 + err * 14.0))) : 0;
    boiler_.reg[0x4005] = (uint32_t)mod;
    boiler_.reg[0x226C] = (uint32_t)(state == 5 ? 2400 + mod * 12 + (int)(40 * std::sin(s / 5.0)) : (on ? 1400 : 600));   // temperatura palnika
    blower_on_ = state == 5; feeder_on_ = state == 5 && std::fmod(s, 12.0) < 2.0 + mod / 25.0;
    {   // zapis użytkownika (ilość paliwa) ma pierwszeństwo przed symulacją
        auto it = boiler_.reg.find(0x3601);
        if (it != boiler_.reg.end() && it->second != last_tank_) fuel_ = (double)it->second;
    }
    if (on) {
        fuel_ -= dt * 0.0022 * (0.4 + mod / 100.0);                          // ~ kilka kg na godzinę
        const uint32_t reserve = reg(0x3604, 20) & 0xFFFF;
        if (fuel_ < reserve - 5) fuel_ = 300;                                // „dosypano” opał
        boiler_.reg[0x3601] = (uint32_t)std::lround(fuel_);
    }
    { auto it = boiler_.reg.find(0x3601); if (it != boiler_.reg.end()) last_tank_ = it->second; }
}

void DemoDevice::tick() {
    std::lock_guard<std::mutex> g(mu_);
    tick_nolock();
}

void DemoDevice::tick_nolock() {
    const uint32_t t = now_ms();
    physics(t);
    if (t - last_pdo_ >= 400) {                          // PDO modułu wejść/wyjść (węzeł 86): podajnik i dmuchawa
        last_pdo_ = t;
        CanFrame f1; f1.id = 0x456; f1.dlc = 1; f1.data[0] = feeder_on_ ? 1 : 0; boiler_.to_engine.push_back(f1);
        CanFrame f2; f2.id = 0x356; f2.dlc = 3; f2.data[0] = blower_on_ ? 1 : 0; f2.data[2] = feeder_on_ ? 1 : 0; boiler_.to_engine.push_back(f2);
    }
    engine_->tick(t);
    auto frames = boiler_.to_engine; boiler_.to_engine.clear();
    for (auto& f : frames) engine_->on_frame(f, t);
}

HttpResponse DemoDevice::handle(const HttpRequest& in) {
    std::lock_guard<std::mutex> g(mu_);
    HttpRequest req = in;
    if (!req.headers.count("authorization") && !req.headers.count("x-token") && !token_.empty())
        req.headers["authorization"] = "Bearer " + token_;
    if (req.path == "/api/v1/ota" && req.method == "POST") {
        HttpResponse r; r.status = 400;
        r.body = "{\"ok\":false,\"error\":\"demo\"}";
        return r;
    }
    return api_->handle(req);
}

}  // namespace tpc
