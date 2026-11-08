#include "engine.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include "json_writer.h"
#include "point.h"

namespace tpc {

static const char* kind_name(Kind k) {
    switch (k) {
        case Kind::Sensor: return "sensor";
        case Kind::Binary: return "binary_sensor";
        case Kind::Enum: return "enum";
    }
    return "sensor";
}

Engine::Engine(const EngineConfig& cfg, SendFn send, const uint8_t device_id[6])
    : cfg_(cfg), send_(std::move(send)),
      queue_(cfg.node, [this](const CanFrame& f) { return send_(f); },
             [this](const SdoResult& r) { on_done(r); }),
      access_(cfg.access), st_(kReadCount) {
    for (int i = 0; i < 6; i++) dev_[i] = device_id[i];
    for (unsigned i = 0; i < kReadCount; i++) if (kReads[i].poll == Poll::Live) live_.push_back(i);
}

bool Engine::skipped(const ReadPoint& p) const {
    if (cfg_.two_circuits) return false;
    switch (p.index) {  // rejestry drugiego obiegu CO
        case 0x4002: case 0x2147: case 0x22AE: case 0x229A: case 0x2065: return true;
        default: return false;
    }
}

std::string Engine::device_id_hex() const {
    char b[13];
    snprintf(b, sizeof b, "%02X%02X%02X%02X%02X%02X", dev_[0], dev_[1], dev_[2], dev_[3], dev_[4], dev_[5]);
    return b;
}

uint8_t Engine::unlock(uint16_t pin, uint32_t now_ms) {
    now_ = now_ms;
    const uint8_t before = access_.level();
    const uint8_t lvl = access_.unlock(pin, now_ms);
    if (lvl > before) queue_all_params(now_ms);  // po PIN-ie odśwież nastawy wyższych poziomów
    return lvl;
}

void Engine::queue_params(Poll p, uint32_t) {
    for (unsigned i = 0; i < kReadCount; i++)
        if (kReads[i].poll == p && !skipped(kReads[i])) par_q_.push_back(i);
}

void Engine::queue_all_params(uint32_t now) {
    par_q_.clear();
    queue_params(Poll::L0, now);
    queue_params(Poll::L1, now);
    queue_params(Poll::L2, now);
}

void Engine::on_frame(const CanFrame& f, uint32_t now) {
    now_ = now;
    if (f.id == COB_SDO_RESP + cfg_.node) { rx_seen_ = true; last_rx_ms_ = now; }
    queue_.on_frame(f, now);
}

void Engine::on_done(const SdoResult& r) {
    const unsigned idx = r.job.tag & 0xFFFF;
    const bool is_write = (r.job.tag & 0x10000) != 0;
    if (r.outcome != SdoOutcome::Ok) return;
    if (is_write) {  // po potwierdzonym zapisie odczytaj rejestr ponownie
        SdoJob j; j.index = kReads[idx].index; j.tag = idx;
        queue_.push(j);
        return;
    }
    if (idx >= kReadCount) return;
    PointState& s = st_[idx];
    s.valid = true;
    s.raw = r.value;
    s.value = decode_value(kReads[idx].decode, r.value);
    s.t_ms = now_;
}

void Engine::tick(uint32_t now) {
    now_ = now;
    access_.tick(now);
    if (!booted_ && now >= cfg_.boot_delay_ms) {
        booted_ = true;
        queue_all_params(now);
    }
    // cykliczny odczyt wybranych punktów
    if (now - last_live_ms_ >= cfg_.live_period_ms && queue_.pending() < 2 && !live_.empty()) {
        for (size_t tries = 0; tries < live_.size(); tries++) {
            const unsigned i = live_[live_pos_++ % live_.size()];
            if (skipped(kReads[i])) continue;
            SdoJob j; j.index = kReads[i].index; j.tag = i;
            queue_.push(j);
            last_live_ms_ = now;
            break;
        }
    } else if (!par_q_.empty() && queue_.pending() < 2) {
        const unsigned i = par_q_.front();
        par_q_.erase(par_q_.begin());
        SdoJob j; j.index = kReads[i].index; j.tag = i;
        queue_.push(j);
    }
    queue_.tick(now);
}

bool Engine::raw_of(const std::string& id, uint32_t& raw) const {
    for (unsigned i = 0; i < kReadCount; i++)
        if (id == kReads[i].id && st_[i].valid) { raw = st_[i].raw; return true; }
    return false;
}

WriteStatus Engine::write(const std::string& id, double value, uint32_t now) {
    now_ = now;
    const ReadPoint* rp = find_read_by_id(id);
    if (!rp) return WriteStatus::UnknownPoint;
    if (rp->write_key < 0) return WriteStatus::NotWritable;
    const Point* p = find_point_by_key((uint8_t)rp->write_key);
    if (!p) return WriteStatus::NotWritable;

    uint32_t raw = 0;
    switch (access_.check_write(*p, value, now, raw)) {
        case WriteResult::Ok: break;
        case WriteResult::Mirror: return WriteStatus::Mirror;
        case WriteResult::Level: return WriteStatus::Level;
        case WriteResult::NoPoint: return WriteStatus::NotWritable;
        case WriteResult::Range: return WriteStatus::Range;
    }
    // Zależności między nastawami (jak w ESPHome): moc min <= moc max.
    auto val = [&](uint16_t index) -> const PointState* {
        for (unsigned i = 0; i < kReadCount; i++)
            if (kReads[i].index == index && st_[i].valid) return &st_[i];
        return nullptr;
    };
    if (p->key == 0) { const PointState* mx = val(0x2271); if (mx && value > mx->value) return WriteStatus::Rejected; }
    if (p->key == 1) { const PointState* mn = val(0x2270); if (mn && value < mn->value) return WriteStatus::Rejected; }

    SdoJob j;
    j.write = true; j.index = rp->index; j.sub = 1; j.value = raw; j.size = 2;
    j.tag = 0x10000 | (uint32_t)(rp - kReads);
    queue_.push(j);
    return WriteStatus::Ok;
}

std::string Engine::info_json(const InfoExtras& x, uint32_t now) const {
    JsonWriter w;
    w.begin_obj();
    w.kv("name", "TeklaPelletCAN").kv("id", device_id_hex()).kv("fw", x.fw).key("api").num(1);
    w.kvb("writable", !cfg_.access.mirror && cfg_.access.write_enabled);
    w.kvb("can_ok", can_ok(now));
    w.key("level").num(access_.level());
    w.kvb("mirror", cfg_.access.mirror);
    w.key("uptime_s").num(x.uptime_s);
    w.key("clients").num(x.clients);
    w.kvb("dev_key", x.dev_key);
    w.end_obj();
    return w.out();
}

std::string Engine::points_json() const {
    JsonWriter w;
    w.begin_obj().key("api").num(1);
    w.key("points").begin_arr();
    for (unsigned i = 0; i < kReadCount; i++) {
        const ReadPoint& p = kReads[i];
        if (skipped(p)) continue;
        w.begin_obj().kv("id", p.id).kv("name", p.name).kv("kind", kind_name(p.kind));
        w.kv("unit", p.unit).kv("class", p.dclass);
        if (p.kind == Kind::Enum) {
            w.key("options").begin_obj();
            const char* o = p.options;
            while (o && *o) {
                char* end;
                long v = strtol(o, &end, 10);
                const char* label = end + 1;
                const char* comma = strchr(label, ',');
                size_t len = comma ? (size_t)(comma - label) : strlen(label);
                char kbuf[16];
                snprintf(kbuf, sizeof kbuf, "%ld", v);
                w.kv(kbuf, std::string(label, len));
                o = comma ? comma + 1 : nullptr;
            }
            w.end_obj();
        }
        const Point* wp = p.write_key >= 0 ? find_point_by_key((uint8_t)p.write_key) : nullptr;
        const bool writable = wp != nullptr;
        w.kvb("writable", writable);
        if (writable) {
            const bool tenth = wp->encoding == Encoding::Tenths || wp->encoding == Encoding::FlagTenths ||
                               wp->encoding == Encoding::TenthsS16;
            w.kv("min", wp->min).kv("max", wp->max).kv("step", tenth ? 0.1 : 1.0);
            w.key("level").num(wp->level);
        }
        w.end_obj();
    }
    w.end_arr().end_obj();
    return w.out();
}

std::string Engine::state_json(uint32_t now) const {
    JsonWriter w;
    w.begin_obj().key("t").num(now).kvb("can_ok", can_ok(now));
    w.key("level").num(access_.level());
    w.key("v").begin_obj();
    for (unsigned i = 0; i < kReadCount; i++) {
        const ReadPoint& p = kReads[i];
        if (skipped(p)) continue;
        w.key(p.id);
        if (st_[i].valid) w.num(st_[i].value); else w.null();
    }
    w.end_obj().key("text").begin_obj();
    for (unsigned i = 0; i < kReadCount; i++) {
        const ReadPoint& p = kReads[i];
        if (p.kind != Kind::Enum || skipped(p) || !st_[i].valid) continue;
        std::string label;
        if (enum_label(p.options, (int)st_[i].value, label)) w.kv(p.id, label);
        else w.kv(p.id, "nieznany (" + std::to_string((int)st_[i].value) + ")");
    }
    w.end_obj().end_obj();
    return w.out();
}

}  // namespace tpc
