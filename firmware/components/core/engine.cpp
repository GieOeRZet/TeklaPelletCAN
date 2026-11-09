#include "engine.h"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdarg>
#include <cstdlib>
#include <cstring>
#include "alarms.h"
#include "json_writer.h"
#include "point.h"

namespace tpc {

namespace {
const uint16_t kTix[22] = {0x2259, 0x2283, 0x2284, 0x2286, 0x311F, 0x229D, 0x229E, 0x229F, 0x22A0, 0x214A, 0x214B,
                           0x214C, 0x214D, 0x216D, 0x351E, 0x351F, 0x2279, 0x2293, 0x2298, 0x2295, 0x2296, 0x2285};
const uint16_t kConf[18] = {0x3501, 0x3500, 0x3505, 0x3720, 0x2106, 0x2108, 0x2107, 0x2123, 0x3602,
                            0x3603, 0x350A, 0x350B, 0x299E, 0x350C, 0x350D, 0x3525, 0x3629, 0x299D};
const uint16_t kStats[14] = {0x3608, 0x3609, 0x3611, 0x3612, 0x3507, 0x3618, 0x3619,
                             0x362A, 0x3610, 0x3613, 0x3614, 0x3615, 0x3616, 0x3628};
constexpr uint16_t kPower = 0x2005, kFeeder = 0x2259, kBlower = 0x2283;

std::string num_str(double v) { return JsonWriter::fmt(v); }

std::string join_hex(const std::vector<int64_t>& v) {
    std::string o; char t[12];
    for (size_t k = 0; k < v.size(); k++) {
        if (v[k] < 0) snprintf(t, sizeof t, "------"); else snprintf(t, sizeof t, "%06X", (unsigned)v[k]);
        if (k) o += ' ';
        o += t;
    }
    return o;
}
std::string join_dec(const std::vector<int64_t>& v, const char* none) {
    std::string o;
    for (size_t k = 0; k < v.size(); k++) {
        if (k) o += ' ';
        o += v[k] < 0 ? std::string(none) : std::to_string((long long)v[k]);
    }
    return o;
}
}  // namespace

Engine::Engine(const EngineConfig& cfg, SendFn send, const uint8_t device_id[6])
    : cfg_(cfg), send_(std::move(send)),
      queue_(cfg.node, [this](const CanFrame& f) { return send_(f); }, [this](const SdoResult& r) { on_done(r); }),
      access_(cfg.access), st_(kReadCount) {
    for (int i = 0; i < 6; i++) dev_[i] = device_id[i];
    ent_read_.assign(kEntityCount, -1);
    for (unsigned r = 0; r < kReadCount; r++) {
        read_of_idx_[kReads[r].index] = (int)r;
        if (kReads[r].poll == Poll::Live) live_.push_back(r);
    }
    for (unsigned e = 0; e < kEntityCount; e++) {
        if (!kEntities[e].source[0]) continue;
        for (unsigned r = 0; r < kReadCount; r++)
            if (std::string(kEntities[e].source) == kReads[r].id) { ent_read_[e] = (int)r; break; }
    }
    ah_raw_.assign(20, 0); ah_t0_.assign(20, 0); ah_t1_.assign(20, 0); ah_txt_.assign(20, std::string());
    sch_cwu_.assign(7, -1); sch_co_.assign(7, -1); sch_boil_.assign(7, -1);
    test_vals_.assign(22, -1); conf_v_.assign(18, -1); stats_.assign(14, -1);
    for (int i = 0; i < 7; i++) bg_.push_back(i < 6 ? 0x2154 + i : 0x2160);
    for (int i = 0; i < 7; i++) bg_.push_back(0x2126 + 4 * i);
    for (int i = 0; i < 7; i++) bg_.push_back(0x2209 + i);
    for (uint16_t s : kStats) bg_.push_back(s);
    for (uint16_t c : kConf) bg_.push_back(c);
}

std::string Engine::device_id_hex() const {
    char b[13];
    snprintf(b, sizeof b, "%02X%02X%02X%02X%02X%02X", dev_[0], dev_[1], dev_[2], dev_[3], dev_[4], dev_[5]);
    return b;
}

bool Engine::skipped(const ReadPoint& p) const {
    auto q = quiet_.find(p.index);
    if (q != quiet_.end() && q->second.fails >= 3 && (int32_t)(now_ms_ - q->second.next_ms) < 0) return true;
    if (cfg_.two_circuits) return false;
    switch (p.index) {  // rejestry drugiego obiegu CO
        case 0x4002: case 0x2147: case 0x22AE: case 0x229A: case 0x2065: return true;
        default: return false;
    }
}

void Engine::logf(const char* fmt, ...) {
    if (!log_) return;
    char b[200];
    va_list ap; va_start(ap, fmt); vsnprintf(b, sizeof b, fmt, ap); va_end(ap);
    log_(b);
}

// ---------------------------------------------------------------- zadania SDO

void Engine::read_index(uint16_t index, uint32_t flags) {
    SdoJob j; j.index = index; j.sub = (flags & F_TYPE) ? 2 : 1; j.tag = index | flags;
    queue_.push(j);
}

void Engine::write_index(uint16_t index, uint32_t value, uint8_t size) {
    logf("ZAPIS 0x%04X <- %u (%u B)", index, (unsigned)value, (unsigned)size);
    SdoJob j; j.write = true; j.index = index; j.sub = 1; j.value = value; j.size = size; j.tag = index | F_WRITE;
    queue_.push(j);
}

void Engine::on_frame(const CanFrame& f, uint32_t now) {
    now_ = now;
    rx_frames_++;
    if (f.id == COB_SDO_RESP + cfg_.node) { rx_seen_ = true; last_rx_ms_ = now; rx_sdo_++; }
    // PDO modułu wejść/wyjść (węzeł 86): podajnik 0x456 b0.0, dmuchawa 0x356 b0.0, podajnik palnika 0x356 b2.0
    if (f.id == 0x456 && f.dlc >= 1) { pdo_feeder_ = f.data[0] & 1; pdo_seen_feeder_ = true; }
    if (f.id == 0x356 && f.dlc >= 1) {
        pdo_blower_ = f.data[0] & 1; pdo_seen_blower_ = true;
        if (f.dlc >= 3) { pdo_feeder2_ = f.data[2] & 1; pdo_seen_feeder2_ = true; }
    }
    queue_.on_frame(f, now);
    if (scan_q_) scan_q_->on_frame(f, now);
}

void Engine::on_done(const SdoResult& r) {
    const uint16_t index = r.job.tag & 0xFFFF;
    const uint32_t fl = r.job.tag & 0xFFFF0000u;
    if (r.outcome == SdoOutcome::Ok) { sdo_ok_++; last_ok_ms_ = now_ms_; quiet_.erase(index); }
    else if (r.outcome == SdoOutcome::Abort) {
        sdo_abort_++; last_abort_code_ = r.abort_code; last_abort_index_ = index;
        if (fl & F_WRITE) logf("ABORT zapisu 0x%04X kod 0x%08X", index, (unsigned)r.abort_code);
    } else if (r.outcome == SdoOutcome::Timeout) {
        sdo_timeout_++;
        if (timeouts_.size() < 64 || timeouts_.count(index)) timeouts_[index]++;
        if (!(fl & F_WRITE) && sdo_ok_ > 0 && now_ms_ - last_ok_ms_ < 10000) {   // kocioł żyje, a ten rejestr milczy
            Quiet& q = quiet_[index];
            if (q.fails < 255) q.fails++;
            if (q.fails >= 3) {
                const uint32_t step = q.fails - 3 < 4 ? (300000u << (q.fails - 3)) : 3600000u;   // 5, 10, 20, 40 min, potem 1 h
                q.next_ms = now_ms_ + (step > 3600000u ? 3600000u : step);
                if (q.fails == 3) logf("Rejestr 0x%04X nie odpowiada – odpytuje rzadko", index);
            }
        }
        if (fl & F_WRITE) logf("BRAK ODPOWIEDZI na zapis 0x%04X", index);
    }
    if (fl & F_WRITE) {
        if (r.outcome == SdoOutcome::Ok) after(300, [this, index]() { read_index(index); });   // odczyt zwrotny
        return;
    }
    if (fl & F_TYPE) {
        Typed* t = index == kPower ? &power_ : index == kFeeder ? &feeder_ : index == kBlower ? &blower_ : nullptr;
        if (t && r.outcome == SdoOutcome::Ok) t->type = r.value & 0xFF;
        return;
    }
    if (r.outcome != SdoOutcome::Ok) return;
    if (fl & F_DIAG) {
        char b[96];
        snprintf(b, sizeof b, "0x%04X.%d = %u (signed %d, %d B)", index, r.job.sub, (unsigned)r.value,
                 r.job.sub == 1 ? (int)(int16_t)(r.value & 0xFFFF) : (int)r.value, r.size);
        sdo_last_ = b;
    }
    on_read(index, r.value);
}

void Engine::on_read(uint16_t index, uint32_t raw) {
    xraw_[index] = raw;
    auto it = read_of_idx_.find(index);
    if (it != read_of_idx_.end()) {
        st_[it->second].valid = true;
        st_[it->second].raw = raw;
        st_[it->second].value = decode_value(kReads[it->second].decode, raw);
    }
    if (index == kPower) power_.last_raw = raw;
    if (index == kFeeder) feeder_.last_raw = raw;
    if (index == kBlower) blower_.last_raw = raw;

    // --- harmonogramy
    if (index >= 0x2154 && index <= 0x2159) { sch_cwu_[index - 0x2154] = raw & 0xFFFFFF; return; }
    if (index == 0x2160) { sch_cwu_[6] = raw & 0xFFFFFF; return; }
    if (index >= 0x2126 && index <= 0x2141 && ((index - 0x2126) % 4) == 0) { sch_co_[(index - 0x2126) / 4] = raw & 0xFFFFFF; return; }
    if (index >= 0x2209 && index <= 0x220F) { sch_boil_[index - 0x2209] = raw & 0xFFFFFF; return; }
    // --- test wyjść
    for (int k = 0; k < 22; k++) if (kTix[k] == index) { test_vals_[k] = raw & 0xFF; break; }
    // --- konfiguracja
    for (int k = 0; k < 18; k++)
        if (kConf[k] == index) { conf_v_[k] = (raw >= 256 && raw < 512) ? (int64_t)raw - 256 : (int64_t)raw; break; }
    // --- statystyki i licznik paliwa
    for (int k = 0; k < 14; k++) if (kStats[k] == index) {
        stats_[k] = (k >= 8 && k <= 12 && raw >= 256) ? (int64_t)raw - 256 : (int64_t)raw;
        if (k == 4 && raw > 0 && (fuel_hist_.empty() || now_ - fuel_t_ >= 3300000UL)) {
            fuel_hist_.push_back((int32_t)raw); fuel_t_ = now_;
            if (fuel_hist_.size() > 25) fuel_hist_.erase(fuel_hist_.begin());
        }
        break;
    }
    // --- alarmy
    if (index == 0x404C) {
        const int old = alarm_pos_;
        alarm_pos_ = raw & 0xFF;
        last_slot_ = ((int)(raw & 0xFF) + 19) % 20;
        if (old != alarm_pos_ && ah_boot_) queue_alarm_history();
        read_index(0x4010 + last_slot_);
        return;
    }
    if (index >= 0x4010 && index < 0x4024) {
        const int hs = index - 0x4010;
        ah_raw_[hs] = raw;
        const bool is_last = (hs == last_slot_) || last_slot_ < 0;
        if (is_last) { alarm_raw_ = raw; alarm_slot_ = hs; }
        const uint32_t code = raw & 0xFFFF;
        ah_txt_[hs] = code == 0 ? std::string() : alarm_text(raw);
        if (!is_last) return;
        alarm_code_ = code;
        alarm_flag_active_ = (raw >> 16) & 1;
        set_text("alarm_last_text", code == 0 ? "brak" : alarm_text(raw));
        char rb[24]; snprintf(rb, sizeof rb, "0x%08X", (unsigned)raw);
        set_text("alarm_raw_text", rb);
        if (code == 0) { set_text("alarm_active", "off"); set_text("alarm_start_text", "0"); set_text("alarm_end_text", "0"); return; }
        read_index(0x4024 + hs);
        return;
    }
    if (index >= 0x4024 && index < 0x4038) {
        const int i = index - 0x4024;
        ah_t0_[i] = raw;
        if (i != alarm_slot_) return;
        alarm_t0_ = raw;
        set_text("alarm_start_text", std::to_string((unsigned)raw));
        read_index(0x4038 + i);
        return;
    }
    if (index >= 0x4038 && index < 0x404C) {
        const int i = index - 0x4038;
        ah_t1_[i] = raw;
        if (i != alarm_slot_) return;
        set_text("alarm_end_text", std::to_string((unsigned)raw));
        const bool open_end = (raw == 0) || (raw < alarm_t0_);
        set_text("alarm_active", (alarm_code_ != 0 && (alarm_flag_active_ || open_end)) ? "on" : "off");
        return;
    }
}

std::string Engine::alarm_text(uint32_t raw) const {
    const uint32_t code = raw & 0xFFFF;
    const bool active = (raw >> 16) & 1, confirmed = (raw >> 17) & 1;
    const char* nm = alarm_name((uint16_t)code);
    char b[160];
    snprintf(b, sizeof b, "kod %u%s%s%s%s%s", (unsigned)code, nm[0] ? " (" : "", nm, nm[0] ? ")" : "",
             active ? ", aktywny" : "", confirmed ? ", oczekuje" : "");
    return b;
}

// ---------------------------------------------------------------- kolejki odczytu

void Engine::queue_params(Poll p) {
    for (unsigned i = 0; i < kReadCount; i++)
        if (kReads[i].poll == p && !skipped(kReads[i])) par_q_.push_back(kReads[i].index);
}
void Engine::queue_all_params() {
    par_q_.clear();
    queue_params(Poll::L0); queue_params(Poll::L1); queue_params(Poll::L2);
    for (uint16_t c : kConf) par_q_.push_back(c);
}
void Engine::queue_schedules() { for (uint16_t i : bg_) par_q_.push_back(i); }
void Engine::queue_alarm_history() {
    if (par_q_.size() > 100) return;
    for (int i = 0; i < 20; i++) par_q_.push_back(0x4010 + i);
    for (int i = 0; i < 20; i++) par_q_.push_back(0x4024 + i);
    for (int i = 0; i < 20; i++) par_q_.push_back(0x4038 + i);
}

uint8_t Engine::unlock(uint16_t pin, uint32_t now_ms) {
    now_ = now_ms;
    const uint8_t before = access_.level();
    const uint8_t lvl = access_.unlock(pin, now_ms);
    logf("PIN: poziom dostepu %d", (int)lvl);
    if (lvl > before) queue_all_params();   // po PIN-ie odśwież nastawy wyższych poziomów
    return lvl;
}

void Engine::tick(uint32_t now) {
    now_ms_ = now;
    now_ = now;
    access_.tick(now);
    const bool cok = can_ok(now);
    if (cok != was_can_ok_) { was_can_ok_ = cok; logf(cok ? "CAN: kociol odpowiada" : "CAN: brak odpowiedzi kotla"); }
    // timery jednorazowe
    for (size_t i = 0; i < timers_.size();) {
        if (now >= timers_[i].when) { auto fn = std::move(timers_[i].fn); timers_.erase(timers_.begin() + i); fn(); }
        else i++;
    }
    if (!booted_ && now >= cfg_.boot_delay_ms) {
        booted_ = true;
        queue_all_params();
        queue_alarm_history();
        ah_boot_ = true;
    }
    // autopowrót wyjść testowych na Automat
    if (cfg_.test_revert_s > 0 && test_mask_ && now - test_t_ > cfg_.test_revert_s * 1000UL) test_reset();

    if (scan_on_) {   // skaner rejestrów (podczas skanu pomijamy odczyt cykliczny)
        if (scan_q_ && now - scan_last_ms_ >= 100 && scan_q_->pending() == 0) {
            if (scan_cur_ > scan_end_) { scan_on_ = false; sdo_last_ = "Skan zakonczony"; }
            else { SdoJob j; j.index = (uint16_t)scan_cur_++; j.sub = scan_sub_; j.tag = j.index | F_DIAG; scan_q_->push(j); scan_last_ms_ = now; }
        }
        if (scan_q_) scan_q_->tick(now);
        queue_.tick(now);
        return;
    }

    if (queue_.pending() < 2) {
        if (now - last_live_ms_ >= cfg_.live_period_ms && !live_.empty()) {
            // typy rejestrów sterujących poznajemy sami (sub 2), zanim pozwolimy na zapis
            static const uint16_t tidx[3] = {kPower, kFeeder, kBlower};
            Typed* ts[3] = {&power_, &feeder_, &blower_};
            for (int k = 0; k < 3; k++)
                if (ts[k]->type == 0 && (now / cfg_.live_period_ms) % 8 == (uint32_t)(k * 3)) {
                    static uint8_t tries[3] = {0, 0, 0};
                    if (++tries[k] > 6) ts[k]->type = 0x06; else read_index(tidx[k], F_TYPE);
                }
            for (size_t tries = 0; tries < live_.size(); tries++) {
                const unsigned i = live_[live_pos_++ % live_.size()];
                if (skipped(kReads[i])) continue;
                read_index(kReads[i].index);
                last_live_ms_ = now;
                break;
            }
        } else if (!par_q_.empty()) {
            const uint16_t ix = par_q_.front();
            par_q_.erase(par_q_.begin());
            read_index(ix);
        } else if (now - last_bg_ms_ >= 400) {
            // tło: harmonogramy, konfiguracja, statystyki, alarm (pozycja), licznik paliwa, dodatkowe rejestry
            last_bg_ms_ = now;
            const size_t total = bg_.size() + xpoll_.size() + 1;
            const size_t i = bg_pos_++ % total;
            if (i < bg_.size()) read_index(bg_[i]);
            else if (i < bg_.size() + xpoll_.size()) read_index(xpoll_[i - bg_.size()], F_DIAG);
            else read_index(0x404C);
        }
    }
    queue_.tick(now);
    if (now - last_recompute_ >= 500) { last_recompute_ = now; recompute(now); }
}

// ---------------------------------------------------------------- obliczenia

double Engine::value_of(const char* id, bool* ok) const {
    for (unsigned i = 0; i < kReadCount; i++)
        if (strcmp(id, kReads[i].id) == 0) { if (ok) *ok = st_[i].valid; return st_[i].value; }
    if (ok) *ok = false;
    return 0;
}

bool Engine::raw_of(const std::string& id, uint32_t& raw) const {
    for (unsigned i = 0; i < kReadCount; i++)
        if (id == kReads[i].id && st_[i].valid) { raw = st_[i].raw; return true; }
    return false;
}

void Engine::recompute(uint32_t now) {
    bool ok1, ok2, ok3, ok4, ok5;
    // kod stanu palnika = ta sama wartość co enum
    const double bs = value_of("burner_state", &ok1);
    if (ok1) set_text("burner_state_code", num_str(bs));

    // moc palnika [kW] i spalanie [kg/h]
    const double test = value_of("fuel_test", &ok1), tmax = value_of("p_feed_max", &ok2), per = value_of("p_feeder_period", &ok3);
    const double cv = value_of("fuel_heat", &ok4), p = value_of("burner_power", &ok5);
    if (ok1 && ok2 && ok3 && ok4 && ok5 && per > 0) {
        const double kgh100 = test * tmax / per;
        const double kw = kgh100 * cv * cfg_.burner_eff_kw * p / 100.0;
        set_text("burner_kw", num_str(std::round(kw * 10.0) / 10.0));
        set_text("burner_fuel_rate", num_str(std::round(kw / (cv * cfg_.burner_eff_fuel) * 10.0) / 10.0));
    }
    // zbiornik, rezerwa, zużycie 24 h i prognoza
    const double cap = value_of("tank_cap", &ok1), kg = value_of("tank_kg", &ok2);
    if (ok1 && ok2 && cap > 0) set_text("tank_pct", num_str(std::round(kg * 100.0 / cap)));
    double res = value_of("boil_fuel_reserve", &ok3);
    if (!ok3) res = 0;
    if (ok2) set_text("fuel_low", (res > 0 && kg <= res) ? "on" : "off");
    if (fuel_hist_.size() >= 3) {
        const double used = fuel_hist_.back() - fuel_hist_.front();
        const double span = (double)(fuel_hist_.size() - 1);
        if (used >= 0) {
            const double rate = used * 24.0 / span;
            set_text("fuel_use_24h", num_str(rate));
            if (ok2 && rate > 0.2) set_text("fuel_days", num_str(std::fmax(0.0, (kg - res) / rate)));
        }
    }
    // PDO (po 30 s bez ramki: wyłączone)
    auto pdo = [&](const char* id, bool seen, bool val) { if (seen) set_text(id, val ? "on" : "off"); else if (now > 30000) set_text(id, "off"); };
    pdo("feeder_running", pdo_seen_feeder_, pdo_feeder_);
    pdo("blower_running", pdo_seen_blower_, pdo_blower_);
    pdo("feeder2_running", pdo_seen_feeder2_, pdo_feeder2_);

    set_text("can_ok", can_ok(now) ? "on" : "off");
    set_text("mirror_mode", cfg_.access.mirror ? "on" : "off");
    set_text("access_level_sensor", std::to_string(access_.level()));
    set_text("fw_ver", cfg_.fw);
    // historia alarmów: "kod ...|początek|koniec" albo "-"
    for (int i = 0; i < 20; i++) {
        std::string o = "-";
        if (!ah_txt_[i].empty()) { char b[40]; snprintf(b, sizeof b, "|%u|%u", (unsigned)ah_t0_[i], (unsigned)ah_t1_[i]); o = ah_txt_[i] + b; }
        set_text("ah_" + std::to_string(i), o);
    }
    set_text("sch_cwu_txt", join_hex(sch_cwu_));
    set_text("sch_co_txt", join_hex(sch_co_));
    set_text("sch_boil_txt", join_hex(sch_boil_));
    set_text("test_state_txt", join_dec(test_vals_, "-"));
    set_text("conf_txt", join_dec(conf_v_, "--"));
    set_text("stat_txt", join_dec(stats_, "--"));
    if (!sdo_last_.empty()) set_text("sdo_last", sdo_last_);
    // selecty trybu i przełącznik kotła odzwierciedlają stan odczytany z kotła
    std::string lbl;
    for (auto pr : {std::make_pair("co_mode_sel", "co_mode"), std::make_pair("co2_mode_sel", "co2_mode"), std::make_pair("cwu_mode_sel", "cwu_mode")}) {
        const double v = value_of(pr.second, &ok1);
        if (ok1 && enum_label("0:Off,1:Eko,2:Harmonogram,3:Komfort", (int)v, lbl)) set_text(pr.first, lbl);
    }
    const double on = value_of("boiler_on", &ok1);
    if (ok1) set_text("boiler_power_sw", on != 0 ? "on" : "off");
    set_text("restart", "off");
}

std::string Engine::text_of(const std::string& id) const {
    auto it = computed_.find(id);
    return it == computed_.end() ? std::string() : it->second;
}

// ---------------------------------------------------------------- zapis

bool Engine::writes_blocked(bool flag, Svc& why) const {
    if (cfg_.access.mirror) { why = Svc::Mirror; return true; }
    if (!flag || !cfg_.access.write_enabled) { why = Svc::Disabled; return true; }
    return false;
}

WriteStatus Engine::write(const std::string& id, double value, uint32_t now) {
    const ReadPoint* rp = find_read_by_id(id);
    if (!rp) return WriteStatus::UnknownPoint;
    if (rp->write_key < 0) return WriteStatus::NotWritable;
    return write_key(rp->write_key, value, now);
}

WriteStatus Engine::write_key(int key, double value, uint32_t now) {
    now_ = now;
    if (key < 0 || key > 255) return WriteStatus::NotWritable;
    const Point* p = find_point_by_key((uint8_t)key);
    if (!p) return WriteStatus::NotWritable;
    uint32_t raw = 0;
    switch (access_.check_write(*p, value, now, raw)) {
        case WriteResult::Ok: break;
        case WriteResult::Mirror: return WriteStatus::Mirror;
        case WriteResult::Level: return WriteStatus::Level;
        case WriteResult::NoPoint: return WriteStatus::NotWritable;
        case WriteResult::Range: return WriteStatus::Range;
    }
    bool ok;
    // zależności między nastawami (jak w ESPHome)
    if (key == 0) { const double mx = value_of("power_max", &ok); if (ok && value > mx) return WriteStatus::Rejected; }
    if (key == 1) { const double mn = value_of("power_min", &ok); if (ok && value < mn) return WriteStatus::Rejected; }
    if (key == 47) { const double cap = value_of("tank_cap", &ok); if (ok && value > cap) return WriteStatus::Rejected; }
    write_index(p->index, raw, 2);
    return WriteStatus::Ok;
}

Svc Engine::typed_write(uint16_t index, Typed& t, uint32_t value) {
    const int ty = t.type == 0 ? 0x06 : t.type;
    const uint8_t size = (ty == 0x05) ? 1 : ((ty == 0x06 || ty == 0x03) ? 2 : 4);
    uint32_t v = value;
    if (!t.alt && size != 1) v |= (t.last_raw & 0xFF00);   // wariant A: zachowaj górny bajt jak zwraca kocioł
    write_index(index, v, size);
    return Svc::Ok;
}

Svc Engine::set_power(bool on) {
    Svc why;
    if (now_ < cfg_.boot_guard_ms) return Svc::Blocked;
    if (writes_blocked(cfg_.power_write, why)) return why;
    typed_write(kPower, power_, on ? 1 : 0);
    after(4000, [this, on]() {
        bool ok; const double cur = value_of("boiler_on", &ok);
        if (!(ok && ((cur != 0) == on))) power_.alt = !power_.alt;   // następne kliknięcie spróbuje drugi wariant
    });
    return Svc::Ok;
}

Svc Engine::set_feeder(int mode) {
    Svc why;
    bool ok; const double on = value_of("boiler_on", &ok);
    if (mode == 2 && (now_ < cfg_.boot_guard_ms || !(ok && on != 0) || (feeder_.last_raw & 0xFF) == 2)) return Svc::Blocked;
    if (writes_blocked(cfg_.feeder_write, why)) return why;
    typed_write(kFeeder, feeder_, mode);
    after(8000, [this, mode]() { if ((feeder_.last_raw & 0xFF) != (uint32_t)mode) feeder_.alt = !feeder_.alt; });
    if (mode == 2 && cfg_.feeder_on_s > 0)
        after(cfg_.feeder_on_s * 1000UL, [this]() { typed_write(kFeeder, feeder_, 0); });   // sam wraca do Automatu
    return Svc::Ok;
}

Svc Engine::set_blower(int mode) {
    Svc why;
    bool ok; const double on = value_of("boiler_on", &ok);
    (void)on;
    if (mode == 2 && now_ < cfg_.boot_guard_ms) return Svc::Blocked;
    if (writes_blocked(cfg_.blower_write, why)) return why;
    typed_write(kBlower, blower_, mode);
    after(8000, [this, mode]() { if ((blower_.last_raw & 0xFF) != (uint32_t)mode) blower_.alt = !blower_.alt; });
    if (mode == 2 && cfg_.blower_on_s > 0)
        after(cfg_.blower_on_s * 1000UL, [this]() { typed_write(kBlower, blower_, 0); });
    return Svc::Ok;
}

Svc Engine::mode_send(uint16_t index, int mode) {
    Svc why;
    if (now_ < cfg_.boot_guard_ms) return Svc::Blocked;
    if (writes_blocked(cfg_.mode_write, why)) return why;
    write_index(index, 0x0100 | (uint32_t)(mode & 3), 2);
    return Svc::Ok;
}

Svc Engine::set_output(int out, int mode) {
    Svc why;
    if (out < 0 || out > 21 || out == 18 || mode < 0 || mode > 2) return Svc::BadArgs;
    if (writes_blocked(cfg_.output_test_write, why)) return why;
    if (access_.level() < 2) return Svc::Level;
    write_index(kTix[out], 0x0100 | (uint32_t)mode, 2);
    if (mode) test_mask_ |= (1u << out); else test_mask_ &= ~(1u << out);
    test_t_ = now_;
    return Svc::Ok;
}

Svc Engine::test_reset() {
    for (int out = 0; out < 22; out++)
        if (test_mask_ & (1u << out)) write_index(kTix[out], 0x0100, 2);
    test_mask_ = 0;
    return Svc::Ok;
}

// ---------------------------------------------------------------- usługi (akcje)

static bool arg(const Args& a, const char* k, double& v) {
    auto it = a.find(k);
    if (it == a.end()) return false;
    v = it->second;
    return true;
}

static Svc from_write(WriteStatus s) {
    switch (s) {
        case WriteStatus::Ok: return Svc::Ok;
        case WriteStatus::Mirror: return Svc::Mirror;
        case WriteStatus::Level: return Svc::Level;
        case WriteStatus::Range: return Svc::Range;
        case WriteStatus::Rejected: return Svc::Rejected;
        default: return Svc::BadArgs;
    }
}

Svc Engine::call(const std::string& action, const Args& a, uint32_t now) {
    now_ = now;
    double x, y, z, w;
    Svc why;
    if (action == "unlock") {
        if (!arg(a, "pin", x)) return Svc::BadArgs;
        unlock((uint16_t)x, now);
        return Svc::Ok;
    }
    if (action == "set_setpoint") {
        if (!arg(a, "which", x) || !arg(a, "value", y) || x < 0 || x > 4) return Svc::BadArgs;
        if (writes_blocked(cfg_.setpoint_write, why)) return why;
        return from_write(write_key(100 + (int)x, y, now));
    }
    if (action == "set_boiler_mode") {
        if (!arg(a, "mode", x) || x < 0 || x > 3) return Svc::BadArgs;
        if (writes_blocked(cfg_.setpoint_write, why)) return why;
        return from_write(write_key(106, x, now));
    }
    if (action == "set_param") {
        if (!arg(a, "key", x) || !arg(a, "value", y) || x < 0 || x > 80) return Svc::BadArgs;
        return from_write(write_key((int)x, y, now));
    }
    if (action == "set_schedule") {
        if (!arg(a, "kind", x) || !arg(a, "day", y) || !arg(a, "bits", z) || x < 0 || x > 2 || y < 0 || y > 6) return Svc::BadArgs;
        if (writes_blocked(cfg_.schedule_write, why)) return why;
        const int d = (int)y;
        const uint16_t idx = x == 0 ? (d == 6 ? 0x2160 : 0x2154 + d) : x == 1 ? 0x2126 + 4 * d : 0x2209 + d;
        write_index(idx, (uint32_t)z & 0xFFFFFF, 4);
        return Svc::Ok;
    }
    if (action == "set_output") {
        if (!arg(a, "out", x) || !arg(a, "mode", y)) return Svc::BadArgs;
        return set_output((int)x, (int)y);
    }
    if (action == "set_output_pct") {
        if (!arg(a, "value", x) || x < 0 || x > 100) return Svc::BadArgs;
        if (writes_blocked(cfg_.output_test_write, why)) return why;
        if (access_.level() < 2) return Svc::Level;
        write_index(0x2298, 0x0100 | (uint32_t)x, 2);
        test_mask_ |= (1u << 17); test_t_ = now;
        return Svc::Ok;
    }
    if (action == "test_refresh") { for (uint16_t t : kTix) par_q_.push_back(t); return Svc::Ok; }
    if (action == "test_reset") return test_reset();
    if (action == "alarm_refresh") { par_q_.push_back(0x404C); queue_alarm_history(); return Svc::Ok; }
    if (action == "param_refresh") { queue_all_params(); return Svc::Ok; }
    if (action == "schedule_refresh") { queue_schedules(); return Svc::Ok; }
    if (action == "sdo_read") {
        if (!arg(a, "index", x)) return Svc::BadArgs;
        SdoJob j; j.index = (uint16_t)x; j.sub = arg(a, "sub", y) ? (uint8_t)y : 1; j.tag = j.index | F_DIAG;
        queue_.push(j);
        return Svc::Ok;
    }
    if (action == "sdo_write") {
        if (!arg(a, "index", x) || !arg(a, "value", z) || !arg(a, "size", w) || (w != 1 && w != 2 && w != 4)) return Svc::BadArgs;
        if (cfg_.access.mirror) return Svc::Mirror;
        if (!cfg_.access.write_enabled) return Svc::Disabled;
        SdoJob j; j.write = true; j.index = (uint16_t)x; j.sub = arg(a, "sub", y) ? (uint8_t)y : 1;
        j.value = (uint32_t)z; j.size = (uint8_t)w; j.tag = j.index | F_WRITE;
        queue_.push(j);
        return Svc::Ok;
    }
    if (action == "sdo_scan") {
        if (!arg(a, "from_index", x) || !arg(a, "to_index", y) || x < 0 || y < x || y > 0xFFFF) return Svc::BadArgs;
        scan_sub_ = arg(a, "sub", z) ? (uint8_t)z : 1;
        scan_node_ = arg(a, "node", z) ? (uint8_t)z : cfg_.node;
        scan_cur_ = (uint32_t)x; scan_end_ = (uint32_t)y;
        scan_q_.reset(new SdoQueue(scan_node_, [this](const CanFrame& f) { return send_(f); },
                                   [this](const SdoResult& r) { on_scan_done(r); }, 150, 0));
        scan_on_ = true; scan_last_ms_ = now;
        return Svc::Ok;
    }
    if (action == "sdo_scan_stop") { scan_on_ = false; scan_q_.reset(); sdo_last_ = "Skan przerwany"; return Svc::Ok; }
    if (action == "sdo_poll_add") {
        if (!arg(a, "index", x)) return Svc::BadArgs;
        for (uint16_t i : xpoll_) if (i == (uint16_t)x) return Svc::Ok;
        xpoll_.push_back((uint16_t)x);
        return Svc::Ok;
    }
    if (action == "sdo_poll_clear") { xpoll_.clear(); return Svc::Ok; }
    return Svc::UnknownAction;
}

void Engine::on_scan_done(const SdoResult& r) {
    if (r.outcome != SdoOutcome::Ok) return;
    char b[96];
    snprintf(b, sizeof b, "0x%04X.%d = %u (signed %d, %d B)", (unsigned)(r.job.tag & 0xFFFF), r.job.sub, (unsigned)r.value,
             (int)(int16_t)(r.value & 0xFFFF), r.size);
    sdo_last_ = b;
}

Svc Engine::press(const std::string& id, uint32_t now) {
    now_ = now;
    if (id == "potwierdz_alarm") {
        if (!cfg_.alarm_confirm || cfg_.access.mirror) return Svc::Disabled;
        if (alarm_slot_ < 0 || alarm_slot_ > 19 || (alarm_raw_ & 0xFFFF) == 0) return Svc::Rejected;
        write_index(0x4010 + alarm_slot_, alarm_raw_ | (1u << 18), 4);   // bit 18 = żądanie potwierdzenia
        return Svc::Ok;
    }
    if (id == "podajnik_automat") return set_feeder(0);
    if (id == "podajnik_wylacz") return set_feeder(1);
    if (id == "podajnik_podaj_paliwo_30_s") return set_feeder(2);
    if (id == "dmuchawa_automat") return set_blower(0);
    if (id == "dmuchawa_wylacz") return set_blower(1);
    if (id == "dmuchawa_wlacz_czasowo") return set_blower(2);
    if (id == "raport_diagnostyczny_utworz") {
        char r[255];
        snprintf(r, sizeof r, "TeklaPelletCAN fw=%s up=%umin can=%s sdo_ok=%u sdo_abort=%u lvl=%d mirror=%s write=%s",
                 cfg_.fw.c_str(), (unsigned)(now / 60000UL), can_ok(now) ? "OK" : "BLAD", (unsigned)sdo_ok_,
                 (unsigned)sdo_abort_, (int)access_.level(), cfg_.access.mirror ? "true" : "false",
                 cfg_.access.write_enabled ? "true" : "false");
        set_text("diag_rep", r);
        return Svc::Ok;
    }
    if (id == "snap_a_punkt_odniesienia" || id == "snap_b_pokaz_zmiany" || id == "snap_stop") return Svc::Unsupported;
    return Svc::UnknownAction;
}

Svc Engine::set_switch(const std::string& id, bool on, uint32_t now) {
    now_ = now;
    if (id == "boiler_power_sw") return set_power(on);
    return Svc::Unsupported;   // "restart" obsługuje warstwa platformy
}

Svc Engine::select(const std::string& id, const std::string& option, uint32_t now) {
    now_ = now;
    int mode = option == "Off" ? 0 : option == "Eko" ? 1 : option == "Harmonogram" ? 2 : option == "Komfort" ? 3 : -1;
    if (mode < 0) return Svc::BadArgs;
    if (id == "co_mode_sel") return mode_send(0x2064, mode);
    if (id == "co2_mode_sel") return mode_send(0x2065, mode);
    if (id == "cwu_mode_sel") return mode_send(0x2014, mode);
    return Svc::UnknownAction;
}

// ---------------------------------------------------------------- JSON

static const char* kind_name(Kind k) {
    switch (k) { case Kind::Sensor: return "sensor"; case Kind::Binary: return "binary_sensor"; case Kind::Enum: return "enum"; }
    return "sensor";
}

std::string Engine::info_json(const InfoExtras& x, uint32_t now) const {
    JsonWriter w;
    w.begin_obj();
    w.kv("name", "TeklaPelletCAN").kv("id", device_id_hex()).kv("fw", x.fw.empty() ? cfg_.fw : x.fw).key("api").num(1);
    w.kvb("writable", !cfg_.access.mirror && cfg_.access.write_enabled);
    w.kvb("can_ok", can_ok(now));
    w.key("level").num(access_.level());
    w.kvb("mirror", cfg_.access.mirror);
    w.key("uptime_s").num(x.uptime_s);
    w.key("clients").num(x.clients);
    w.kvb("dev_key", x.dev_key);
    w.kvb("password_set", x.password_set);
    w.end_obj();
    return w.take();
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
        w.kvb("writable", wp != nullptr);
        if (wp) {
            const bool tenth = wp->encoding == Encoding::Tenths || wp->encoding == Encoding::FlagTenths ||
                               wp->encoding == Encoding::TenthsS16;
            w.kv("min", wp->min).kv("max", wp->max).kv("step", tenth ? 0.1 : 1.0);
            w.key("level").num(wp->level);
        }
        w.end_obj();
    }
    w.end_arr().end_obj();
    return w.take();
}

std::string Engine::diag_json(uint32_t now) const {
    JsonWriter w;
    w.begin_obj().kvb("can_ok", can_ok(now)).key("rx_frames").num(rx_frames_).key("rx_sdo").num(rx_sdo_);
    w.key("sdo_ok").num(sdo_ok_).key("sdo_abort").num(sdo_abort_).key("sdo_timeout").num(sdo_timeout_);
    char b[24];
    snprintf(b, sizeof b, "0x%08X", (unsigned)last_abort_code_);
    w.kv("last_abort_code", b);
    snprintf(b, sizeof b, "0x%04X", (unsigned)last_abort_index_);
    w.kv("last_abort_index", b);
    w.key("timeouts").begin_obj();
    {   // 8 rejestrów z największą liczbą timeoutów
        std::vector<std::pair<uint32_t, uint16_t>> v;
        for (auto& kv : timeouts_) v.push_back({kv.second, kv.first});
        std::sort(v.rbegin(), v.rend());
        for (size_t i = 0; i < v.size() && i < 8; i++) { snprintf(b, sizeof b, "0x%04X", (unsigned)v[i].second); w.key(b).num(v[i].first); }
    }
    w.end_obj();
    w.key("quiet").begin_arr();
    for (auto& kv : quiet_) if (kv.second.fails >= 3) { snprintf(b, sizeof b, "0x%04X", (unsigned)kv.first); w.str(b); }
    w.end_arr();
    w.key("queue").num(queue_.pending()).key("level").num(access_.level());
    w.kvb("mirror", cfg_.access.mirror).kvb("write_enabled", cfg_.access.write_enabled);
    w.kvb("pdo_feeder_seen", pdo_seen_feeder_).kvb("pdo_blower_seen", pdo_seen_blower_);
    w.end_obj();
    return w.take();
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
    return w.take();
}

std::string Engine::states_json(const std::string& prefix, uint32_t now) const {
    JsonWriter w;
    w.reserve(32768);   // jedna alokacja zamiast dublowania bufora (oszczędza stertę ESP)
    w.begin_obj().key("t").num(now).kvb("can_ok", can_ok(now)).key("level").num(access_.level());
    w.key("states").begin_arr();
    for (unsigned e = 0; e < kEntityCount; e++) {
        const Entity& en = kEntities[e];
        std::string state = "unknown";
        const int ri = ent_read_[e];
        if (ri >= 0) {
            if (st_[ri].valid) {
                const std::string dom = en.domain;
                if (dom == "binary_sensor") state = st_[ri].value != 0 ? "on" : "off";
                else if (kReads[ri].kind == Kind::Enum && dom == "text_sensor") {
                    std::string label;
                    state = enum_label(kReads[ri].options, (int)st_[ri].value, label)
                                ? label : "nieznany (" + std::to_string((int)st_[ri].value) + ")";
                } else state = JsonWriter::fmt(st_[ri].value);
            }
        } else {
            auto it = computed_.find(en.id);
            if (it != computed_.end()) state = it->second;
        }
        w.begin_obj().kv("entity_id", entity_id(en, prefix)).kv("state", state).kv("id", en.id).kv("domain", en.domain);
        w.key("attributes").begin_obj().kv("friendly_name", en.name);
        if (en.unit[0]) w.kv("unit_of_measurement", en.unit);
        if (en.dclass[0]) w.kv("device_class", en.dclass);
        if (!strcmp(en.domain, "select")) {
            w.key("options").begin_arr().str("Off").str("Eko").str("Harmonogram").str("Komfort").end_arr();
        }
        w.end_obj().end_obj();
    }
    w.end_arr().end_obj();
    return w.take();
}

}  // namespace tpc
