#include "access.h"

namespace tpc {

uint8_t Access::unlock(uint16_t pin, uint32_t now) {
    if (pin == cfg_.pin2) level_ = 2;
    else if (pin == cfg_.pin1) level_ = 1;
    else level_ = 0;
    last_ms_ = now;
    return level_;
}

uint8_t Access::tick(uint32_t now) {
    if (level_ > 0 && cfg_.autolock_ms && now - last_ms_ >= cfg_.autolock_ms) level_ = 0;
    return level_;
}

WriteResult Access::check_write(const Point& p, double value, uint32_t now, uint32_t& raw) {
    if (cfg_.mirror || !cfg_.write_enabled) return WriteResult::Mirror;
    tick(now);
    touch(now);
    if (p.level > level_) return WriteResult::Level;
    if (value < p.min || value > p.max) return WriteResult::Range;
    Encoded e = encode(p.encoding, value);
    if (!e.ok) return WriteResult::Range;
    raw = e.raw;
    return WriteResult::Ok;
}

}  // namespace tpc
