#include <cassert>
#include <cstdio>
#include <map>
#include <string>
#include <vector>
#include "fake_boiler.h"
#include "../components/core/api.h"
#include "../components/core/json_parse.h"

using namespace tpc;

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
    b.reg[0x3600] = 300;            // zbiornik 300 kg
    b.reg[0x3604] = 20;             // rezerwa paliwa 20 kg
    b.reg[0x2272] = 100; b.reg[0x2257] = 256 + 50; b.reg[0x3700] = 40; b.reg[0x2292] = 256 + 46; b.reg[0x4005] = 60;  // do mocy kW (wzor zapasowy)
    b.reg[0x3706] = 184;             // moc palnika - odczyt bezposredni z panelu (k_pwr): 18,4 kW
    b.reg[0x404C] = 256 + 2;                              // alarm: następna pozycja 2 -> ostatni slot 1
    b.reg[0x4011] = 0x00010000 | 140;                     // slot 1: kod 140 (brak ognia), aktywny
    b.reg[0x4025] = 1700000000; b.reg[0x4039] = 0;       // początek, koniec (otwarty)
    b.reg[0x4010] = 0x00020000 | 2;                       // slot 0: przegrzanie, oczekuje
    b.reg[0x2154] = 0x00FF00;                             // harmonogram CWU pon
    b.reg[0x2259] = 256; b.reg[0x2283] = 256;             // podajnik/dmuchawa: Automat
    b.reg[0x2005 + 0] = 257;

    const uint8_t dev[6] = {0xA1, 0xB2, 0xC3, 0xD4, 0xE5, 0xF6};
    EngineConfig cfg;
    cfg.boot_delay_ms = 100;
    cfg.boot_guard_ms = 0;
    cfg.test_revert_s = 0;
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


    // ---- warstwa obliczana i encje dodatkowe
    t = run(e, b, t, 40000);
    assert(e.text_of("burner_state_code") == "5");
    assert(e.text_of("tank_pct") == "40");                         // 120/300
    assert(e.text_of("fuel_low") == "off");
    assert(e.text_of("burner_kw") != "" && e.text_of("burner_fuel_rate") != "");
    // moc palnika pochodzi teraz z bezposredniego odczytu (k_pwr, ten sam rejestr co liczy/pokazuje
    // sam panel) - w symulatorze ustawiony na 18,4 kW (SimBoiler::populate_demo), NIE z wzoru
    // (ilosc paliwa x wartosc opalowa x moc% x sprawnosc) - ten zostaje tylko jako zapasowe przyblizenie,
    // uzywane gdy odczyt bezposredni akurat niedostepny. Spalanie [kg/h] nadal przyblizone, ale juz
    // liczone z prawdziwej mocy: 18,4/(4,6*0,85) = 4,7.
    assert(e.text_of("burner_kw") == "18.4");
    assert(e.text_of("burner_fuel_rate") == "4.7");
    assert(e.text_of("can_ok") == "on" && e.text_of("mirror_mode") == "off");
    assert(e.text_of("fw_ver") == "0.1.0");
    assert(e.text_of("alarm_last_text") == "kod 140 (Brak ognia/opalu), aktywny" ||
           e.text_of("alarm_last_text").rfind("kod 140", 0) == 0);
    assert(e.text_of("alarm_active") == "on");
    assert(e.text_of("alarm_start_text") == "1700000000");
    assert(e.text_of("ah_0").rfind("kod 2", 0) == 0 && e.text_of("ah_0").find(", oczekuje") != std::string::npos);
    assert(e.text_of("ah_5") == "-");
    assert(e.text_of("sch_cwu_txt").rfind("00FF00 ", 0) == 0);
    // PDO modułu 86
    CanFrame pdo; pdo.id = 0x456; pdo.dlc = 1; pdo.data[0] = 1; e.on_frame(pdo, t);
    CanFrame pdo2; pdo2.id = 0x356; pdo2.dlc = 3; pdo2.data[0] = 0; pdo2.data[2] = 1; e.on_frame(pdo2, t);
    t = run(e, b, t, 1000);
    assert(e.text_of("feeder_running") == "on" && e.text_of("blower_running") == "off" && e.text_of("feeder2_running") == "on");

    // ---- usługi
    assert(e.call("set_setpoint", {{"which", 4}, {"value", 72}}, t) == Svc::Ok);
    t = run(e, b, t, 1000);
    assert(b.writes.back().first == 0x2003 && b.writes.back().second == 72);
    assert(e.call("set_setpoint", {{"which", 2}, {"value", 21.5}}, t) == Svc::Ok);     // CO komfort: raw = 215
    t = run(e, b, t, 1000);
    assert(b.writes.back().first == 0x2032 && b.writes.back().second == 215);
    assert(e.call("set_setpoint", {{"which", 2}, {"value", 99}}, t) == Svc::Range);
    assert(e.call("set_boiler_mode", {{"mode", 3}}, t) == Svc::Ok);
    t = run(e, b, t, 1000);
    assert(b.writes.back().first == 0x2002 && b.writes.back().second == 3);
    assert(e.call("set_param", {{"key", 0}, {"value", 45}}, t) == Svc::Ok);
    assert(e.call("set_param", {{"key", 99}, {"value", 1}}, t) == Svc::BadArgs);
    assert(e.call("nie_ma", {}, t) == Svc::UnknownAction);
    // harmonogram: 24 bity, zapis 4-bajtowy
    assert(e.call("set_schedule", {{"kind", 0}, {"day", 0}, {"bits", 0x0FF0F0}}, t) == Svc::Ok);
    t = run(e, b, t, 1000);
    assert(b.writes.back().first == 0x2154 && b.writes.back().second == 0x0FF0F0);
    // test wyjść wymaga klucza 2
    e.call("unlock", {{"pin", 900}}, t);
    assert(e.call("set_output", {{"out", 1}, {"mode", 2}}, t) == Svc::Level);
    e.call("unlock", {{"pin", 999}}, t);
    assert(e.call("set_output", {{"out", 1}, {"mode", 2}}, t) == Svc::Ok);
    assert(e.call("set_output", {{"out", 18}, {"mode", 2}}, t) == Svc::BadArgs);
    t = run(e, b, t, 1000);
    assert(b.writes.back().first == 0x2283 && b.writes.back().second == 0x0102);
    assert(e.call("test_reset", {}, t) == Svc::Ok);
    t = run(e, b, t, 1000);
    assert(b.writes.back().first == 0x2283 && b.writes.back().second == 0x0100);
    // przyciski i przełączniki
    assert(e.press("podajnik_podaj_paliwo_30_s", t) == Svc::Ok);
    t = run(e, b, t, 1000);
    assert(b.writes.back().first == 0x2259 && (b.writes.back().second & 0xFF) == 2);
    assert(e.press("podajnik_podaj_paliwo_30_s", t) == Svc::Blocked);      // już trwa podawanie -> blokada powtórzenia
    t = run(e, b, t, 32000);                                                // po 30 s wraca do Automatu
    assert(b.writes.back().first == 0x2259 && (b.writes.back().second & 0xFF) == 0);
    assert(e.set_switch("boiler_power_sw", false, t) == Svc::Ok);
    t = run(e, b, t, 1000);
    assert(b.writes.back().first == 0x2005 && (b.writes.back().second & 0xFF) == 0);
    assert(e.select("cwu_mode_sel", "Komfort", t) == Svc::Ok);
    t = run(e, b, t, 1000);
    assert(b.writes.back().first == 0x2014 && b.writes.back().second == 0x0103);
    assert(e.select("cwu_mode_sel", "zly", t) == Svc::BadArgs);
    // potwierdzenie alarmu: odczytany rejestr | bit 18, zapis 32-bitowy
    assert(e.press("potwierdz_alarm", t) == Svc::Ok);
    t = run(e, b, t, 1000);
    assert(b.writes.back().first == 0x4011 && (b.writes.back().second & (1u << 18)) != 0);   // zapis 4-bajtowy z bitem 18
    assert(e.press("raport_diagnostyczny_utworz", t) == Svc::Ok && e.text_of("diag_rep").rfind("TeklaPelletCAN", 0) == 0);
    // skaner rejestrów
    assert(e.call("sdo_scan", {{"from_index", 0x2001}, {"to_index", 0x2003}}, t) == Svc::Ok);
    t = run(e, b, t, 2000);
    assert(e.text_of("sdo_last").find("0x2003") == 0 || e.text_of("sdo_last") == "Skan zakonczony");
    assert(e.call("sdo_scan_stop", {}, t) == Svc::Ok);
    // sdo_read -> wynik w "SDO ostatni odczyt"
    assert(e.call("sdo_read", {{"index", 0x2001}}, t) == Svc::Ok);
    t = run(e, b, t, 1500);
    assert(e.text_of("sdo_last").rfind("0x2001.1 = ", 0) == 0);

    // ---- tryb mirror blokuje usługi
    EngineConfig mc2; mc2.access.mirror = true; mc2.boot_guard_ms = 0;
    Engine m2(mc2, [&](const CanFrame& f) { return b.on_can(f); }, dev);
    assert(m2.call("set_setpoint", {{"which", 4}, {"value", 70}}, 0) == Svc::Mirror);
    assert(m2.press("podajnik_automat", 0) == Svc::Mirror);

    // tryb mirror blokuje zapisy
    EngineConfig mc; mc.access.mirror = true;
    Engine m(mc, [&](const CanFrame& f) { return b.on_can(f); }, dev);
    assert(m.write("boiler_set_manual", 70, 0) == WriteStatus::Mirror);

    // CAN nie odpowiada -> can_ok = false
    FakeBoiler dead; dead.abort_all = true;
    Engine d(cfg, [&](const CanFrame& f) { return dead.on_can(f); }, dev);
    uint32_t td = run(d, dead, 0, 20000);
    assert(d.state_json(td).find("\"boiler_temp\":null") != std::string::npos);

    // stany w formacie HA (dla karty i integracji)
    std::string hs = e.states_json("tekla", t);
    assert(contains(hs, "\"entity_id\":\"sensor.tekla_kociol_temperatura\",\"state\":\"65.3\""));
    assert(contains(hs, "\"unit_of_measurement\":\"\xC2\xB0" "C\""));
    assert(contains(hs, "\"entity_id\":\"sensor.tekla_palnik_stan\",\"state\":\"Modulacja\""));
    assert(contains(hs, "\"entity_id\":\"binary_sensor.tekla_kociol_wlaczony\",\"state\":\"off\""));
    // historia alarmow: skonsolidowana w 1 encje (dawniej 20 osobnych ah_0..ah_19) - wpisy jako atrybuty
    assert(contains(hs, "\"entity_id\":\"sensor.tekla_historia_alarmow\""));
    assert(contains(hs, "\"ah_0\":\"kod 2"));
    assert(contains(hs, "\"entity_id\":\"sensor.tekla_palnik_kod_stanu\",\"state\":\"5\""));
    assert(contains(hs, "\"entity_id\":\"binary_sensor.tekla_alarm_aktywny\",\"state\":\"on\""));
    assert(slugify("Podajnik: Podaj paliwo (30 s)") == "podajnik_podaj_paliwo_30_s");

    std::string info = e.info_json(InfoExtras{"0.1.0", 12, 1, false}, t);
    assert(contains(info, "\"id\":\"A1B2C3D4E5F6\"") && contains(info, "\"fw\":\"0.1.0\""));
    // cichy rejestr (kocioł nie odpowiada): po 3 timeoutach odpytywany rzadko; po odzyskaniu odpowiedzi wraca do normy
    {
        FakeBoiler q; q.reg = b.reg; q.silent.insert(0x2283);
        Engine eq(cfg, [&](const CanFrame& f) { return q.on_can(f); }, dev);
        uint32_t tq = run(eq, q, 0, 60000);
        auto count = [&](uint16_t ix) { int n = 0; for (uint16_t v : q.reads_seen) n += v == ix; return n; };
        const int c1 = count(0x2283);
        assert(contains(eq.diag_json(tq), "\"quiet\":[\"0x2283\"]"));
        tq = run(eq, q, tq, 180000);                       // 3 min: brak kolejnych prób (pierwsza ponowna dopiero po 5 min)
        assert(count(0x2283) == c1);
        q.silent.clear();
        tq = run(eq, q, tq, 400000);                       // po 5 min próba, odpowiedź poprawna -> koniec wyciszenia
        assert(count(0x2283) > c1);
        assert(!contains(eq.diag_json(tq), "0x2283\"]") && contains(eq.diag_json(tq), "\"quiet\":[]"));
    }
    // zegar od klienta: /api/v1/time (ESP nie ma internetu ani RTC)
    {
        MemoryClientStore cs; cs.set_password("haslo123");
        int64_t clk = 0; uint32_t seq = 0;
        Api api(e, cs, ApiConfig{}, [&] { return (uint32_t)(t); }, [&](size_t n) { std::string r; for (size_t i = 0; i < n; i++) r += "ab"[(seq++) & 1]; return r; });
        ApiHooks hk; hk.set_time = [&](int64_t v) { clk = v; }; hk.get_time = [&]() -> int64_t { return clk; };
        api.set_hooks(hk);
        HttpRequest rq; rq.method = "POST"; rq.path = "/api/v1/time"; rq.body = "{\"epoch_ms\":1794200000000}";
        rq.headers["origin"] = "http://evil.example"; rq.headers["host"] = "192.168.0.5";
        assert(api.handle(rq).status == 401);                       // obcy origin bez tokenu
        HttpRequest pr; pr.method = "POST"; pr.path = "/api/v1/pair"; pr.body = "{\"password\":\"haslo123\",\"client_id\":\"app\",\"name\":\"a\"}";
        std::string tok;
        HttpResponse pres = api.handle(pr);
        Json pj; assert(json_parse(pres.body, pj)); tok = pj.str("token");
        rq.headers.erase("origin"); rq.headers["authorization"] = "Bearer " + tok;
        HttpResponse ok = api.handle(rq);
        assert(ok.status == 200 && clk == 1794200000);
        HttpRequest bad = rq; bad.body = "{\"epoch\":100}";
        assert(api.handle(bad).status == 422);                      // spoza sensownego zakresu
        HttpRequest ir; ir.method = "GET"; ir.path = "/api/v1/info";
        HttpResponse info = api.handle(ir);
        assert(contains(info.body, "\"time\":1794200000") && contains(info.body, "\"features\":[\"time\"]"));
    }
    puts("OK: testy silnika przeszly");
    return 0;
}
