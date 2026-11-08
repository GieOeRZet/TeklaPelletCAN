#pragma once
#include <cstdint>
#include "codec.h"

namespace tpc {

// Punkt danych = jeden rejestr kotła (węzeł 4, sub 1) wraz z opisem.
struct Point {
    uint8_t key;        // numer nastawy (zgodny z `set_param` w PelletCAN)
    uint16_t index;     // indeks CANopen
    Encoding encoding;
    float min, max;     // zakres wartości fizycznej
    uint8_t level;      // wymagany poziom dostępu do zapisu (0, 1, 2)
    const char* name;
};

// Wygenerowane przez tools/gen_points.py z rejestry/punkty.csv.
extern const Point kPoints[];
extern const unsigned kPointCount;

const Point* find_point_by_key(uint8_t key);
const Point* find_point_by_index(uint16_t index);

}  // namespace tpc
