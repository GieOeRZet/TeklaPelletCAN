#include "sdo.h"

namespace tpc {

static void put_addr(CanFrame& f, uint16_t index, uint8_t sub) {
    f.data[1] = index & 0xFF;
    f.data[2] = (index >> 8) & 0xFF;
    f.data[3] = sub;
}

CanFrame sdo_read_request(uint8_t node, uint16_t index, uint8_t sub) {
    CanFrame f;
    f.id = COB_SDO_REQ + node;
    f.dlc = 8;
    f.data[0] = 0x40;
    put_addr(f, index, sub);
    return f;
}

CanFrame sdo_write_request(uint8_t node, uint16_t index, uint8_t sub, uint32_t value, uint8_t size) {
    CanFrame f;
    uint8_t cs;
    switch (size) {
        case 1: cs = 0x2F; break;
        case 2: cs = 0x2B; break;
        case 4: cs = 0x23; break;
        default: return f;  // id 0 = błąd
    }
    f.id = COB_SDO_REQ + node;
    f.dlc = 8;
    f.data[0] = cs;
    put_addr(f, index, sub);
    for (uint8_t i = 0; i < size; i++) f.data[4 + i] = (value >> (8 * i)) & 0xFF;
    return f;
}

SdoReply sdo_parse_reply(uint8_t node, const CanFrame& f) {
    SdoReply r;
    if (f.id != COB_SDO_RESP + node || f.dlc < 4) return r;
    const uint8_t b0 = f.data[0];
    r.index = f.data[1] | (f.data[2] << 8);
    r.sub = f.data[3];
    if (b0 == 0x80) {
        if (f.dlc < 8) return r;
        r.status = SdoStatus::Abort;
        r.abort_code = f.data[4] | (f.data[5] << 8) | (f.data[6] << 16) | ((uint32_t)f.data[7] << 24);
        return r;
    }
    if (b0 == 0x60) {
        r.status = SdoStatus::Ok;
        r.is_write_ack = true;
        return r;
    }
    // Initiate upload response: ccs=2 (0x40), e=bit1, s=bit0, n=bity 3..2.
    if ((b0 & 0xE0) == 0x40 && (b0 & 0x02)) {
        uint8_t size = (b0 & 0x01) ? (4 - ((b0 >> 2) & 0x03)) : 4;
        if (f.dlc < 4 + size) return r;
        r.size = size;
        for (uint8_t i = 0; i < size; i++) r.value |= (uint32_t)f.data[4 + i] << (8 * i);
        r.status = SdoStatus::Ok;
    }
    return r;
}

}  // namespace tpc
