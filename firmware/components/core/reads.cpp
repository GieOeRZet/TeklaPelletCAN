#include "reads.h"
#include <cstdlib>
#include <cstring>

namespace tpc {

double decode_value(Decode d, uint32_t raw) {
    const uint32_t low = raw & 0xFF;
    switch (d) {
        case Decode::S16:      return (int16_t)(raw & 0xFFFF);
        case Decode::S16_10:   return (int16_t)(raw & 0xFFFF) / 10.0;
        case Decode::U16:      return raw & 0xFFFF;
        case Decode::U16_10:   return (raw & 0xFFFF) / 10.0;
        case Decode::U8:       return raw & 0xFF;
        case Decode::U8_10:    return (raw & 0xFF) / 10.0;
        case Decode::LOW:      return low;
        case Decode::LOW_10:   return low / 10.0;
        case Decode::RAW:      return raw;
        case Decode::FLAG_LOW: return low != 0 ? 1 : 0;
        case Decode::B0_SET:     return (raw & 1) == 1 ? 1 : 0;
        case Decode::B0_CLEAR:   return (raw & 1) == 0 ? 1 : 0;
    }
    return 0;
}

const ReadPoint* find_read_by_id(const std::string& id) {
    for (unsigned i = 0; i < kReadCount; i++)
        if (id == kReads[i].id) return &kReads[i];
    return nullptr;
}

const ReadPoint* find_read_by_index(uint16_t index) {
    for (unsigned i = 0; i < kReadCount; i++)
        if (kReads[i].index == index) return &kReads[i];
    return nullptr;
}

bool enum_label(const char* options, int value, std::string& out) {
    const char* p = options;
    while (p && *p) {
        char* end;
        long v = strtol(p, &end, 10);
        if (*end != ':') return false;
        const char* label = end + 1;
        const char* comma = strchr(label, ',');
        size_t len = comma ? (size_t)(comma - label) : strlen(label);
        if (v == value) { out.assign(label, len); return true; }
        p = comma ? comma + 1 : nullptr;
    }
    return false;
}

}  // namespace tpc
