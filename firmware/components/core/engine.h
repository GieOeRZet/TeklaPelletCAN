#pragma once
// Silnik urządzenia (odpowiednik logiki ESPHome PelletCAN): odczyt cykliczny, stan punktów, warstwa obliczana
// (moc, paliwo, alarmy, harmonogramy, test wyjść, PDO), zapis z poziomami PIN i usługi (akcje) dla karty/HA.
// Bez zależności od ESP-IDF – ramki CAN wchodzą/wychodzą przez interfejs, czas podawany z zewnątrz (ms).
#include <cstdint>
#include <functional>
#include <map>
#include <memory>
#include <string>
#include <vector>
#include "access.h"
#include "can_frame.h"
#include "entities.h"
#include "reads.h"
#include "sdo_queue.h"

namespace tpc {

struct EngineConfig {
    uint8_t node = 4;                  // węzeł kotła
    bool two_circuits = false;         // false = pomijamy rejestry CO2
    uint32_t boot_delay_ms = 3000;     // po starcie czekamy, zanim zaczniemy czytać nastawy
    uint32_t boot_guard_ms = 30000;    // tyle po starcie nie wysyłamy zapisów do kotła
    uint32_t live_period_ms = 250;     // odstęp między odczytami cyklicznymi
    AccessConfig access;               // PIN-y, autoblokada, mirror, write_enabled
    // wyłączniki zapisu jak w ESPHome (*_write)
    bool power_write = true, mode_write = true, schedule_write = true, setpoint_write = true;
    bool feeder_write = true, blower_write = true, alarm_confirm = true, output_test_write = true;
    uint32_t feeder_on_s = 30, blower_on_s = 20, test_revert_s = 120;
    double burner_eff_kw = 0.90, burner_eff_fuel = 0.85;
    std::string fw = "0.1.0";
};

using Args = std::map<std::string, double>;

enum class WriteStatus : uint8_t { Ok, UnknownPoint, NotWritable, Mirror, Level, Range, Rejected };

enum class Svc : uint8_t {
    Ok, UnknownAction, BadArgs, Mirror, Disabled, Level, Range, Rejected, Blocked, Unsupported,
};

struct InfoExtras {                    // dane spoza silnika, dokładane do /info
    std::string fw;
    uint32_t uptime_s = 0;
    uint32_t clients = 0;
    bool dev_key = false;
    bool password_set = false;
    int64_t time_s = 0;                // zegar urządzenia (epoch s) albo 0, gdy nie ustawiony
};

class Engine {
public:
    using SendFn = std::function<bool(const CanFrame&)>;

    Engine(const EngineConfig& cfg, SendFn send, const uint8_t device_id[6]);

    void on_frame(const CanFrame& f, uint32_t now_ms);
    void tick(uint32_t now_ms);

    // Dziennik zdarzeń (zapisy, PIN-y, utrata/odzyskanie CAN) – wstrzykiwany przez platformę.
    void set_logger(std::function<void(const std::string&)> fn) { log_ = std::move(fn); }
    std::string diag_json(uint32_t now_ms) const;

    // Poziomy dostępu menu (PIN): 0 użytkownik, 1 klucz 1, 2 klucz 2.
    uint8_t unlock(uint16_t pin, uint32_t now_ms);
    uint8_t level() const { return access_.level(); }

    // Zapis nastawy po id punktu (liczba w karcie/HA) albo po kluczu `set_param`.
    WriteStatus write(const std::string& id, double value, uint32_t now_ms);
    WriteStatus write_key(int key, double value, uint32_t now_ms);

    // Usługi (akcje ESPHome) i encje sterujące.
    Svc call(const std::string& action, const Args& args, uint32_t now_ms);
    Svc press(const std::string& entity_yaml_id, uint32_t now_ms);
    Svc set_switch(const std::string& entity_yaml_id, bool on, uint32_t now_ms);
    Svc select(const std::string& entity_yaml_id, const std::string& option, uint32_t now_ms);

    bool can_ok(uint32_t now_ms) const { return rx_seen_ && now_ms - last_rx_ms_ < 5000; }
    std::string device_id_hex() const;

    // JSON dla API.
    std::string info_json(const InfoExtras& x, uint32_t now_ms) const;
    std::string points_json() const;
    std::string state_json(uint32_t now_ms) const;
    std::string states_json(const std::string& prefix, uint32_t now_ms) const;   // format HA (karta, integracja)

    // Dostęp do wartości (testy/diagnostyka).
    bool raw_of(const std::string& id, uint32_t& raw) const;
    std::string text_of(const std::string& entity_yaml_id) const;   // stan encji jako tekst ("" = unknown)

private:
    struct PointState { bool valid = false; uint32_t raw = 0; double value = 0; };
    struct Timer { uint32_t when; std::function<void()> fn; };

    // zadania SDO: tag = indeks | flagi
    static constexpr uint32_t F_WRITE = 0x10000, F_TYPE = 0x20000, F_DIAG = 0x40000;
    void read_index(uint16_t index, uint32_t flags = 0);
    void write_index(uint16_t index, uint32_t value, uint8_t size);
    void on_done(const SdoResult& r);
    void on_read(uint16_t index, uint32_t raw);
    void on_scan_done(const SdoResult& r);

    void queue_params(Poll p);
    void queue_all_params();
    void queue_schedules();
    void queue_alarm_history();
    bool skipped(const ReadPoint& p) const;
    void recompute(uint32_t now_ms);
    void set_text(const std::string& id, const std::string& v) { computed_[id] = v; }
    double value_of(const char* id, bool* ok = nullptr) const;
    std::string alarm_text(uint32_t raw) const;
    void after(uint32_t delay_ms, std::function<void()> fn) { timers_.push_back({now_ + delay_ms, std::move(fn)}); }

    // zapisy typowane (rejestry, których typ poznajemy sami: 0x2005, 0x2259, 0x2283)
    struct Typed { int type = 0; bool alt = false; uint32_t last_raw = 0; };
    Svc typed_write(uint16_t index, Typed& t, uint32_t value);
    Svc set_power(bool on);
    Svc set_feeder(int mode);
    Svc set_blower(int mode);
    Svc mode_send(uint16_t index, int mode);
    Svc set_output(int out, int mode);
    Svc test_reset();
    bool writes_blocked(bool flag, Svc& why) const;

    EngineConfig cfg_;
    SendFn send_;
    uint8_t dev_[6];
    SdoQueue queue_;
    std::unique_ptr<SdoQueue> scan_q_;
    Access access_;
    std::vector<PointState> st_;
    std::map<uint16_t, int> read_of_idx_;
    std::vector<int> ent_read_;
    std::map<std::string, std::string> computed_;   // encje obliczane: yaml id -> stan
    std::map<uint16_t, uint32_t> xraw_;             // surowe wartości dowolnych rejestrów
    std::vector<unsigned> live_;
    std::vector<uint16_t> par_q_;                   // kolejka odczytu (indeksy)
    std::vector<uint16_t> bg_;                      // tło: harmonogramy, konfiguracja, statystyki, test wyjść
    std::vector<uint16_t> xpoll_;                   // sdo_poll_add
    size_t live_pos_ = 0, bg_pos_ = 0;
    uint32_t last_live_ms_ = 0, last_bg_ms_ = 0, last_rx_ms_ = 0, last_recompute_ = 0;
    uint32_t now_ = 0;
    bool rx_seen_ = false, booted_ = false;
    std::vector<Timer> timers_;

    // PDO modułu 86
    bool pdo_feeder_ = false, pdo_blower_ = false, pdo_feeder2_ = false;
    bool pdo_seen_feeder_ = false, pdo_seen_blower_ = false, pdo_seen_feeder2_ = false;
    // typy rejestrów sterujących
    Typed power_, feeder_, blower_;
    // alarmy
    int alarm_pos_ = -1, last_slot_ = -1, alarm_slot_ = -1;
    uint32_t alarm_raw_ = 0, alarm_t0_ = 0, alarm_code_ = 0;
    bool alarm_flag_active_ = false, ah_boot_ = false;
    std::vector<uint32_t> ah_raw_, ah_t0_, ah_t1_;
    std::vector<std::string> ah_txt_;
    // harmonogramy, test wyjść, konfiguracja, statystyki
    std::vector<int64_t> sch_cwu_, sch_co_, sch_boil_, test_vals_, conf_v_, stats_;
    uint32_t test_mask_ = 0, test_t_ = 0;
    // paliwo
    std::vector<int32_t> fuel_hist_;
    uint32_t fuel_t_ = 0, last_fuel_poll_ = 0;
    // diagnostyka
    std::string sdo_last_;
    bool scan_on_ = false;
    uint32_t scan_cur_ = 0, scan_end_ = 0, scan_last_ms_ = 0;
    uint8_t scan_sub_ = 1, scan_node_ = 4;
    uint32_t sdo_ok_ = 0, sdo_abort_ = 0, sdo_timeout_ = 0, rx_frames_ = 0, rx_sdo_ = 0, last_abort_code_ = 0;
    uint16_t last_abort_index_ = 0;
    // Rejestry, na które kocioł nie odpowiada (np. nieobsługiwane w tym modelu): po 3 kolejnych timeoutach, gdy reszta SDO działa,
    // odpytujemy je rzadko (5 min, potem co raz dłużej do 1 h) zamiast co cykl. Pierwsza poprawna odpowiedź przywraca normalne odpytywanie.
    struct Quiet { uint8_t fails = 0; uint32_t next_ms = 0; };
    std::map<uint16_t, Quiet> quiet_;
    uint32_t now_ms_ = 0, last_ok_ms_ = 0;
    std::map<uint16_t, uint32_t> timeouts_;       // rejestr -> liczba timeoutów (diagnostyka)
    bool was_can_ok_ = false;
    std::function<void(const std::string&)> log_;
    void logf(const char* fmt, ...) __attribute__((format(printf, 2, 3)));
};

}  // namespace tpc
