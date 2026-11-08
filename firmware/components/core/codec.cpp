#include "codec.h"
#include <cmath>

namespace tpc {

Decoded decode(Encoding enc, uint32_t raw) {
    Decoded d;
    switch (enc) {
        case Encoding::Plain:
        case Encoding::Mask24:
        case Encoding::UnixTime:
            d.value = raw; d.ok = true; break;
        case Encoding::FlagByte:
        case Encoding::EnumList:
            d.value = raw & 0xFF; d.ok = true; break;
        case Encoding::Tenths:
            d.value = raw / 10.0; d.ok = true; break;
        case Encoding::FlagTenths:
            d.value = (raw & 0xFF) / 10.0; d.ok = true; break;
        case Encoding::Switch:
            if (raw == 256 || raw == 257) { d.value = raw - 256; d.ok = true; }
            break;
    }
    return d;
}

Encoded encode(Encoding enc, double value) {
    Encoded e;
    if (!std::isfinite(value)) return e;
    auto set = [&](double raw) {
        if (raw < 0 || raw > 0xFFFFFFFFu) return;
        e.raw = static_cast<uint32_t>(std::lround(raw));
        e.ok = true;
    };
    switch (enc) {
        case Encoding::Plain:
        case Encoding::Mask24:
        case Encoding::UnixTime:
            set(value); break;
        case Encoding::FlagByte:
        case Encoding::EnumList:
            if (value >= 0 && value <= 255) set(256 + std::lround(value));
            break;
        case Encoding::Tenths:
            set(value * 10.0); break;
        case Encoding::FlagTenths:
            if (value >= 0 && value <= 25.5) set(256 + std::lround(value * 10.0));
            break;
        case Encoding::Switch:
            if (value == 0 || value == 1) set(256 + value);
            break;
    }
    if (enc == Encoding::Mask24 && e.ok && e.raw > 0xFFFFFF) e.ok = false;
    return e;
}

}  // namespace tpc
