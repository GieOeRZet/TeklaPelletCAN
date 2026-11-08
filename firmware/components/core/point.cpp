#include "point.h"

namespace tpc {

const Point* find_point_by_key(uint8_t key) {
    for (unsigned i = 0; i < kPointCount; i++)
        if (kPoints[i].key == key) return &kPoints[i];
    return nullptr;
}

const Point* find_point_by_index(uint16_t index) {
    for (unsigned i = 0; i < kPointCount; i++)
        if (kPoints[i].index == index) return &kPoints[i];
    return nullptr;
}

}  // namespace tpc
