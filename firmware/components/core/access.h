#pragma once
// Poziomy dostępu (0 użytkownik, 1 klucz 1, 2 klucz 2), PIN, autoblokada i walidacja zapisu.
#include <cstdint>
#include "point.h"

namespace tpc {

struct AccessConfig {
    uint16_t pin1 = 900;            // klucz 1
    uint16_t pin2 = 999;            // klucz 2
    uint32_t autolock_ms = 300000;  // 0 = bez blokady
    bool mirror = false;            // true = zapisy zablokowane (tylko odczyt)
    bool write_enabled = true;
};

enum class WriteResult : uint8_t {
    Ok,
    Mirror,        // tryb tylko do odczytu / zapis wyłączony
    NoPoint,       // nieznany punkt
    Level,         // za niski poziom dostępu
    Range,         // wartość poza zakresem lub niekodowalna
};

class Access {
public:
    explicit Access(AccessConfig cfg = {}) : cfg_(cfg) {}

    // Zwraca nowy poziom (zły PIN -> 0).
    uint8_t unlock(uint16_t pin, uint32_t now_ms);
    void touch(uint32_t now_ms) { last_ms_ = now_ms; }
    // Autoblokada; zwraca aktualny poziom.
    uint8_t tick(uint32_t now_ms);
    uint8_t level() const { return level_; }
    const AccessConfig& config() const { return cfg_; }

    // Sprawdza zapis i koduje wartość; przy Ok ustawia raw.
    WriteResult check_write(const Point& p, double value, uint32_t now_ms, uint32_t& raw);

private:
    AccessConfig cfg_;
    uint8_t level_ = 0;
    uint32_t last_ms_ = 0;
};

}  // namespace tpc
