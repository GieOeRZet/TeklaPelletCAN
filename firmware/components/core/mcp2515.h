#pragma once
// Sterownik MCP2515 (CAN po SPI) niezależny od platformy: magistrala SPI
// jest wstrzykiwana przez interfejs ISpi (w ESP-IDF: spi_master, w testach: atrapa).
#include <cstddef>
#include <cstdint>
#include "can_frame.h"

namespace tpc {

class ISpi {
public:
    virtual ~ISpi() = default;
    // Jedna transakcja przy aktywnym CS: wysyła tx[len], zapisuje odebrane bajty do rx[len].
    virtual bool transfer(const uint8_t* tx, uint8_t* rx, size_t len) = 0;
};

enum class CanSpeed : uint8_t { K125 };      // 125 kbit/s (kocioł)
enum class CanClock : uint8_t { MHz16, MHz8 };
enum class CanMode : uint8_t { Normal, ListenOnly };

class Mcp2515 {
public:
    explicit Mcp2515(ISpi& spi) : spi_(spi) {}

    // Reset, ustawienie prędkości i filtrów (przyjmuje wszystko), tryb pracy.
    bool begin(CanSpeed speed, CanClock clock, CanMode mode);

    // Wysyła ramkę (bufor TXB0). false gdy bufor zajęty lub błąd SPI.
    bool send(const CanFrame& f);

    // Odbiera jedną ramkę z RXB0/RXB1, jeśli jest. false gdy brak.
    bool receive(CanFrame& f);

    // Flagi błędów EFLG (0x2D); 0 = brak błędów.
    uint8_t error_flags();
    void clear_error_flags();          // zeruje flagi przepełnienia (RX0OVR/RX1OVR) – są „lepkie”, bez tego pokazują stary błąd

    // Niskopoziomowe (publiczne dla testów).
    bool write_reg(uint8_t addr, uint8_t value);
    bool read_reg(uint8_t addr, uint8_t& value);
    bool bit_modify(uint8_t addr, uint8_t mask, uint8_t value);

private:
    ISpi& spi_;
};

}  // namespace tpc
