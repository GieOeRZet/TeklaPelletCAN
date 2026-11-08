#pragma once
#include <cstdint>

namespace tpc {

// Ramka CAN 2.0A (11-bitowy identyfikator).
struct CanFrame {
    uint16_t id = 0;
    uint8_t dlc = 0;
    uint8_t data[8] = {0, 0, 0, 0, 0, 0, 0, 0};
};

}  // namespace tpc
