#pragma once
// CANopen SDO (expedited) – budowanie zapytań i parsowanie odpowiedzi.
// Bez zależności od ESP-IDF, testowane na hoście.
#include <cstdint>
#include "can_frame.h"

namespace tpc {

constexpr uint16_t COB_SDO_REQ = 0x600;   // klient -> serwer: 0x600 + węzeł
constexpr uint16_t COB_SDO_RESP = 0x580;  // serwer -> klient: 0x580 + węzeł

enum class SdoStatus : uint8_t {
    Ok,        // odpowiedź poprawna
    Abort,     // serwer przerwał (kod w abort_code)
    BadFrame,  // to nie jest odpowiedź SDO tego węzła / zły format
};

struct SdoReply {
    SdoStatus status = SdoStatus::BadFrame;
    bool is_write_ack = false;  // true = potwierdzenie zapisu (0x60)
    uint16_t index = 0;
    uint8_t sub = 0;
    uint8_t size = 0;           // bajty wartości (odczyt), 0 gdy nieznane
    uint32_t value = 0;         // wartość (little-endian), dla odczytu
    uint32_t abort_code = 0;
};

// Zapytanie odczytu (initiate upload).
CanFrame sdo_read_request(uint8_t node, uint16_t index, uint8_t sub);

// Zapis expedited, size = 1, 2 lub 4 (inna wartość -> zwraca ramkę o id 0).
CanFrame sdo_write_request(uint8_t node, uint16_t index, uint8_t sub, uint32_t value, uint8_t size);

// Parsuje odpowiedź węzła `node`. Dla innych węzłów/ramek zwraca BadFrame.
SdoReply sdo_parse_reply(uint8_t node, const CanFrame& f);

}  // namespace tpc
