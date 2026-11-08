// Symulator: uruchamia silnik z atrapą kotła i zrzuca stany (format HA) do pliku – dla testów karty w przeglądarce.
#include <cstdio>
#include <cstdlib>
#include "fake_boiler.h"
#include "../components/core/reads.h"

int main(int argc, char** argv) {
    const char* out = argc > 1 ? argv[1] : "states.json";
    FakeBoiler b;
    for (unsigned i = 0; i < kReadCount; i++) {   // wartości domyślne wg dekodowania
        const ReadPoint& p = kReads[i];
        uint32_t raw = 20;
        switch (p.decode) {
            case Decode::S16_10: raw = 612; break;        // 61,2
            case Decode::S16: raw = 60; break;
            case Decode::U16_10: raw = 46; break;
            case Decode::LOW: case Decode::U8: raw = 256 + 30; break;
            case Decode::LOW_10: case Decode::U8_10: raw = 256 + 45; break;
            case Decode::FLAG_LOW: raw = 257; break;
            case Decode::BIT0: case Decode::NBIT0: raw = 257; break;
            default: raw = 60; break;
        }
        b.reg[p.index] = raw;
    }
    b.reg[0x2001] = 784;  b.reg[0x2003] = 70;  b.reg[0x2004] = 70;     // kocioł 78,4 / zadana 70
    b.reg[0x4001] = 512;  b.reg[0x22AD] = 55;  b.reg[0x2110] = 545;    // CO 51,2 / zadana 55; CWU 54,5
    b.reg[0x215F] = 38;   b.reg[0x4000] = 612; b.reg[0x226C] = 3120;   // zewn. 3,8 °C; powrót 61,2; palnik 312
    b.reg[0x2007] = 5;    b.reg[0x2002] = 2;   b.reg[0x2005] = 257;    // modulacja, auto, włączony
    b.reg[0x2064] = 3;    b.reg[0x2014] = 3;   b.reg[0x3600] = 300;  b.reg[0x3601] = 180;
    b.reg[0x2299] = 257;  b.reg[0x2278] = 256;                          // pompa CO on, CWU off
    // historia alarmów: ostatni slot 1 (kod 140 aktywny), slot 0 (przegrzanie, zakończony)
    b.reg[0x404C] = 256 + 2;  b.reg[0x4011] = 0x00010000 | 140;  b.reg[0x4010] = 2;
    b.reg[0x4025] = 1794150000; b.reg[0x4039] = 0;  b.reg[0x4024] = 1794000000; b.reg[0x4038] = 1794003600;
    b.reg[0x2154] = 0x00FF00; b.reg[0x2126] = 0x3FFFC0;
    const uint8_t dev[6] = {1, 2, 3, 4, 5, 6};
    EngineConfig cfg; cfg.boot_delay_ms = 100;
    Engine e(cfg, [&](const CanFrame& f) { return b.on_can(f); }, dev);
    uint32_t t = 0;
    for (; t < 90000; t += 2) {
        e.tick(t);
        auto fr = b.to_engine; b.to_engine.clear();
        for (auto& f : fr) e.on_frame(f, t);
    }
    FILE* f = fopen(out, "w");
    std::string j = e.states_json("tekla", t);
    fwrite(j.data(), 1, j.size(), f);
    fclose(f);
    printf("zapisano %s (%zu B)\n", out, j.size());
    return 0;
}
