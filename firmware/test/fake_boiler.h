#pragma once
#include <map>
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

