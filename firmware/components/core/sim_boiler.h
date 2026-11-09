#pragma once
// Symulator kotła: odpowiada na zapytania SDO jak prawdziwy sterownik (cs=0x42, 4 bajty danych) i przyjmuje zapisy.
// Używany w trybie demo na urządzeniu (bez magistrali CAN) oraz w testach.
#include <map>
#include <set>
#include <vector>
#include "can_frame.h"
#include "reads.h"

namespace tpc {
// Atrapa kotła: odpowiada na SDO jak prawdziwy (cs=0x42, 4 bajty danych), zapisuje zapisy.
struct SimBoiler {
    std::map<uint16_t, uint32_t> reg;
    std::vector<std::pair<uint16_t, uint32_t>> writes;
    std::vector<CanFrame> to_engine;
    std::vector<uint16_t> reads_seen;
    bool abort_all = false;
    std::set<uint16_t> silent;       // rejestry, na które kocioł w ogóle nie odpowiada (timeout)

    bool on_can(const CanFrame& f) {
        if (f.id != 0x604) return true;
        const uint16_t idx = f.data[1] | (f.data[2] << 8);
        CanFrame r; r.id = 0x584; r.dlc = 8; r.data[1] = f.data[1]; r.data[2] = f.data[2]; r.data[3] = f.data[3];
        if (silent.count(idx) && f.data[0] == 0x40) { reads_seen.push_back(idx); return true; }
        if (abort_all) { r.data[0] = 0x80; r.data[7] = 0x06; to_engine.push_back(r); return true; }
        if (f.data[0] == 0x40) {
            reads_seen.push_back(idx);
            auto it = reg.find(idx);
            if (it == reg.end()) { r.data[0] = 0x80; r.data[4] = 0x00; r.data[5] = 0x00; r.data[6] = 0x02; r.data[7] = 0x06; }
            else { r.data[0] = 0x42; for (int i = 0; i < 4; i++) r.data[4 + i] = (it->second >> (8 * i)) & 0xFF; }
        } else {
            const int n = f.data[0] == 0x23 ? 4 : f.data[0] == 0x2B ? 2 : 1;
            uint32_t v = 0;
            for (int i = 0; i < n; i++) v |= (uint32_t)f.data[4 + i] << (8 * i);
            writes.push_back({idx, v});
            reg[idx] = v;
            r.data[0] = 0x60;
        }
        to_engine.push_back(r);
        return true;
    }
};


// Realistyczne wartości demonstracyjne rejestrów kotła (do symulatora i zrzutów).
inline void populate_demo(SimBoiler& b) {
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
            case Decode::B0_SET: case Decode::B0_CLEAR: raw = 257; break;
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
}

}  // namespace tpc
