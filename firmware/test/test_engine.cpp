#include <cassert>
#include <cstdio>
#include <map>
#include <string>
#include <vector>
#include "../components/core/engine.h"

using namespace tpc;

// Atrapa kotła: odpowiada na SDO jak prawdziwy (cs=0x42, 4 bajty danych), zapisuje zapisy.
struct FakeBoiler {
    std::map<uint16_t, uint32_t> reg;
    std::vector<std::pair<uint16_t, uint32_t>> writes;
    std::vector<CanFrame> to_engine;
    std::vector<uint16_t> reads_seen;
    bool abort_all = false;

    bool on_can(const CanFrame& f) {
        if (f.id != 0x604) return true;
        const uint16_t idx = f.data[1] | (f.data[2] << 8);
        CanFrame r; r.id = 0x584; r.dlc = 8; r.data[1] = f.data[1]; r.data[2] = f.data[2]; r.data[3] = f.data[3];
        if (abort_all) { r.data[0] = 0x80; r.data[7] = 0x06; to_engine.push_back(r); return true; }
        if (f.data[0] == 0x40) {
            reads_seen.push_back(idx);
            auto it = reg.find(idx);
            if (it == reg.end()) { r.data[0] = 0x80; r.data[4] = 0x00; r.data[5] = 0x00; r.data[6] = 0x02; r.data[7] = 0x06; }
            else { r.data[0] = 0x42; for (int i = 0; i < 4; i++) r.data[4 + i] = (it->second >> (8 * i)) & 0xFF; }
        } else {
            uint32_t v = f.data[4] | (f.data[5] << 8);
            writes.push_back({idx, v});
            reg[idx] = v;
            r.data[0] = 0x60;
        }
        to_engine.push_back(r);
        return true;
    }
};

static uint32_t run(Engine& e, FakeBoiler& b, uint32_t from, uint32_t ms) {
    uint32_t t = from;
    for (; t < from + ms; t += 2) {
        e.tick(t);
        auto frames = b.to_engine; b.to_engine.clear();
        for (auto& f : frames) e.on_frame(f, t);
    }
    return t;
}

static bool contains(const std::string& s, const std::string& sub) { return s.find(sub) != std::string::npos; }

int main() {
    FakeBoiler b;
    b.reg[0x2001] = 653;            // temp. kotła 65,3 °C
    b.reg[0x2003] = 65;             // zadana ręczna 65 °C
    b.reg[0x2007] = 256 + 5;        // palnik: modulacja
    b.reg[0x2005] = 257;            // kocioł włączony
    b.reg[0x2270] = 256 + 40;       // moc min 40 (flaga+bajt)
    b.reg[0x2271] = 256 + 100;      // moc max 100
    b.reg[0x2261] = 55;             // krzywa dmuchawy (poziom 1)
    b.reg[0x2002] = 2;              // tryb kotła: Auto
    b.reg[0x3601] = 120;            // paliwo 120 kg

    const uint8_t dev[6] = {0xA1, 0xB2, 0xC3, 0xD4, 0xE5, 0xF6};
    EngineConfig cfg;
    cfg.boot_delay_ms = 100;
    Engine e(cfg, [&](const CanFrame& f) { return b.on_can(f); }, dev);

    uint32_t t = run(e, b, 0, 60000);   // 60 s: pełny cykl odczytów
    uint32_t raw;
    assert(e.can_ok(t));
    assert(e.raw_of("boiler_temp", raw) && raw == 653);

    std::string st = e.state_json(t);
    assert(contains(st, "\"boiler_temp\":65.3"));
    assert(contains(st, "\"boiler_set_manual\":65"));
    assert(contains(st, "\"burner_state\":\"Modulacja\""));
    assert(contains(st, "\"boiler_mode\":\"Auto\""));
    assert(contains(st, "\"boiler_on\":1"));
    assert(contains(st, "\"param_70\":null"));        // rejestr bez odpowiedzi -> null
    // nastawy: wszystkie poziomy odczytane po starcie (odczyt nie wymaga PIN-u)
    assert(contains(st, "\"power_min\":40"));
    assert(e.raw_of("fan_mod_1", raw) && raw == 55);
    // CO2 pominięte przy jednym obiegu
    for (uint16_t ix : b.reads_seen) assert(ix != 0x4002 && ix != 0x2147);

    // opis punktów
    std::string pts = e.points_json();
    assert(contains(pts, "\"id\":\"boiler_set_manual\"") && contains(pts, "\"writable\":true"));
    assert(contains(pts, "\"options\":{\"0\":\"Wylaczony\""));

    // zapis poziomu 0 (setpoint kotła): 70 °C
    assert(e.write("boiler_set_manual", 70, t) == WriteStatus::Ok);
    assert(e.write("boiler_set_manual", 90, t) == WriteStatus::Range);
    assert(e.write("boiler_temp", 50, t) == WriteStatus::NotWritable);
    assert(e.write("nie_ma", 1, t) == WriteStatus::UnknownPoint);
    t = run(e, b, t, 1000);
    assert(!b.writes.empty() && b.writes.back().first == 0x2003 && b.writes.back().second == 70);
    assert(e.raw_of("boiler_set_manual", raw) && raw == 70);     // odczyt zwrotny po zapisie

    // poziom 1 (krzywa dmuchawy) wymaga PIN-u klucza 1
    assert(e.write("fan_mod_1", 60, t) == WriteStatus::Level);
    assert(e.unlock(1111, t) == 0);
    assert(e.write("fan_mod_1", 60, t) == WriteStatus::Level);
    assert(e.unlock(900, t) == 1);
    assert(e.write("fan_mod_1", 60, t) == WriteStatus::Ok);
    t = run(e, b, t, 1000);
    assert(b.writes.back().first == 0x2261 && b.writes.back().second == 60);   // krzywa: bez flagi
    // klucz 2
    assert(e.write("p_inertia", 3, t) == WriteStatus::Level);
    assert(e.unlock(999, t) == 2);
    // autoblokada po 5 min
    t = run(e, b, t, 301000);
    assert(e.level() == 0);

    // moc min nie może przekroczyć mocy max (jak w ESPHome)
    assert(e.write("power_min", 100, t) == WriteStatus::Ok);
    t = run(e, b, t, 1000);
    assert(b.writes.back().first == 0x2270 && b.writes.back().second == 256 + 100);
    assert(e.write("power_max", 30, t) == WriteStatus::Rejected);   // moc max < moc min

    // tryb mirror blokuje zapisy
    EngineConfig mc; mc.access.mirror = true;
    Engine m(mc, [&](const CanFrame& f) { return b.on_can(f); }, dev);
    assert(m.write("boiler_set_manual", 70, 0) == WriteStatus::Mirror);

    // CAN nie odpowiada -> can_ok = false
    FakeBoiler dead; dead.abort_all = true;
    Engine d(cfg, [&](const CanFrame& f) { return dead.on_can(f); }, dev);
    uint32_t td = run(d, dead, 0, 20000);
    assert(d.state_json(td).find("\"boiler_temp\":null") != std::string::npos);

    std::string info = e.info_json(InfoExtras{"0.1.0", 12, 1, false}, t);
    assert(contains(info, "\"id\":\"A1B2C3D4E5F6\"") && contains(info, "\"fw\":\"0.1.0\""));
    puts("OK: testy silnika przeszly");
    return 0;
}
