#pragma once
// Katalog odczytów (rejestr -> encja), wygenerowany z rejestry/odczyty.csv.
#include <cstdint>
#include <string>
#include "license.h"  // Tier

namespace tpc {

enum class Decode : uint8_t {
    S16, S16_10, U16, U16_10, U8, U8_10, LOW, LOW_10, RAW, FLAG_LOW, BIT0, NBIT0,
};
enum class Kind : uint8_t { Sensor, Binary, Enum };
enum class Poll : uint8_t { Live, L0, L1, L2 };  // Live = cyklicznie; L0/L1/L2 = nastawy wg poziomu

struct ReadPoint {
    const char* id;
    uint16_t index;
    Decode decode;
    Kind kind;
    const char* unit;
    const char* dclass;    // device_class HA ("" = brak)
    const char* name;
    const char* options;   // dla Enum: "0:Wylaczony,1:Rozpalanie,..."
    Tier tier;             // Basic = widoczny w podglądzie, Full = tylko po odblokowaniu
    Poll poll;
    int16_t write_key;     // klucz nastawy (points_table) lub -1 gdy tylko odczyt
};

extern const ReadPoint kReads[];
extern const unsigned kReadCount;

// Dekoduje surową wartość rejestru do wartości fizycznej (dla Binary: 0/1).
double decode_value(Decode d, uint32_t raw);

const ReadPoint* find_read_by_id(const std::string& id);
const ReadPoint* find_read_by_index(uint16_t index);

// Tekst opcji enuma dla wartości (nullptr gdy brak); bufor zwracany w `buf`.
bool enum_label(const char* options, int value, std::string& out);

}  // namespace tpc
