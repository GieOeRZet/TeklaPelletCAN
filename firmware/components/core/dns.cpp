#include "dns.h"

namespace tpc {

std::vector<uint8_t> dns_captive_response(const uint8_t* q, size_t n, uint32_t ip) {
    if (n < 12 || (q[2] & 0x80)) return {};                       // za krótkie albo to odpowiedź
    const uint16_t qd = (uint16_t)((q[4] << 8) | q[5]);
    if (qd != 1) return {};
    size_t i = 12;
    while (i < n && q[i] != 0) {                                 // nazwa (bez kompresji w pytaniu)
        if ((q[i] & 0xC0) || i + 1 + q[i] >= n) return {};
        i += 1 + q[i];
    }
    if (i + 5 > n) return {};
    const size_t qend = i + 5;                                   // 0 + typ(2) + klasa(2)
    const uint16_t qtype = (uint16_t)((q[i + 1] << 8) | q[i + 2]);

    std::vector<uint8_t> r(q, q + qend);
    r[2] = (uint8_t)(0x80 | (q[2] & 0x01));                      // QR=1, RD kopiowane
    r[3] = 0x80;                                                 // RA
    const bool a = (qtype == 1);
    r[6] = 0; r[7] = a ? 1 : 0;                                  // ANCOUNT
    r[8] = r[9] = r[10] = r[11] = 0;
    if (a) {
        const uint8_t ans[] = {0xC0, 0x0C, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00, 0x3C, 0x00, 0x04,
                               (uint8_t)(ip >> 24), (uint8_t)(ip >> 16), (uint8_t)(ip >> 8), (uint8_t)ip};
        r.insert(r.end(), ans, ans + sizeof ans);
    }
    return r;
}

}  // namespace tpc
