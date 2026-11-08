#pragma once
// Silnik urządzenia: odczyt cykliczny, stan punktów, poziomy (podstawowy/pełny), zapis, JSON dla API.
// Bez zależności od ESP-IDF – ramki CAN wchodzą/wychodzą przez interfejs, czas podawany z zewnątrz.
#include <cstdint>
#include <functional>
#include <string>
#include <vector>
#include "access.h"
#include "can_frame.h"
#include "license.h"
#include "reads.h"
#include "sdo_queue.h"

namespace tpc {

struct EngineConfig {
    uint8_t node = 4;                  // węzeł kotła
    bool two_circuits = false;         // false = pomijamy rejestry CO2
    uint32_t boot_delay_ms = 3000;     // po starcie czekamy, zanim zaczniemy czytać nastawy
    uint32_t live_period_ms = 250;     // odstęp między odczytami cyklicznymi
    AccessConfig access;
};

enum class WriteStatus : uint8_t {
    Ok, UnknownPoint, NotWritable, Mirror, Level, Range, Rejected,
};

struct InfoExtras {                    // dane spoza silnika, dokładane do /info
    std::string fw;
    uint32_t uptime_s = 0;
    uint32_t clients = 0;
    bool dev_key = false;
};

class Engine {
public:
    using SendFn = std::function<bool(const CanFrame&)>;

    Engine(const EngineConfig& cfg, SendFn send, const uint8_t device_id[6]);

    void on_frame(const CanFrame& f, uint32_t now_ms);
    void tick(uint32_t now_ms);

    // Poziomy dostępu menu (PIN): 0 użytkownik, 1 klucz 1, 2 klucz 2.
    uint8_t unlock(uint16_t pin, uint32_t now_ms);
    uint8_t level() const { return access_.level(); }

    WriteStatus write(const std::string& id, double value, uint32_t now_ms);

    bool can_ok(uint32_t now_ms) const { return rx_seen_ && now_ms - last_rx_ms_ < 5000; }
    std::string device_id_hex() const;

    // JSON dla API (filtrowane wg poziomu funkcji).
    std::string info_json(const InfoExtras& x, uint32_t now_ms) const;
    std::string points_json() const;
    std::string state_json(uint32_t now_ms) const;

    // Ostatnia wartość surowa (do testów/diagnostyki); false gdy brak.
    bool raw_of(const std::string& id, uint32_t& raw) const;

private:
    struct PointState { bool valid = false; uint32_t raw = 0; double value = 0; uint32_t t_ms = 0; };

    void on_done(const SdoResult& r);
    void queue_params(Poll p, uint32_t now_ms);
    void queue_all_params(uint32_t now_ms);
    bool skipped(const ReadPoint& p) const;

    EngineConfig cfg_;
    SendFn send_;
    uint8_t dev_[6];
    SdoQueue queue_;
    Access access_;
    std::vector<PointState> st_;
    std::vector<unsigned> live_;      // indeksy w kReads
    std::vector<unsigned> par_q_;     // kolejka odczytu nastaw
    size_t live_pos_ = 0;
    uint32_t last_live_ms_ = 0;
    uint32_t last_rx_ms_ = 0;
    bool rx_seen_ = false;
    bool booted_ = false;
    uint32_t now_ = 0;
};

}  // namespace tpc
