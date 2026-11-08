#pragma once
#include "mcp2515.h"
#include "driver/spi_master.h"

// Implementacja ISpi na spi_master ESP-IDF (CS sterowany sprzętowo przez sterownik).
class IdfSpi : public tpc::ISpi {
public:
    bool init(int sck, int miso, int mosi, int cs, int clock_hz);
    bool transfer(const uint8_t* tx, uint8_t* rx, size_t len) override;

private:
    spi_device_handle_t dev_ = nullptr;
};
