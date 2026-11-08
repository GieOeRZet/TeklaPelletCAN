#include <cassert>
#include <cstdio>
#include <cstring>
#include <vector>
#include "../components/core/codec.h"
#include "../components/core/mcp2515.h"
#include "../components/core/sdo.h"

using namespace tpc;

// Atrapa MCP2515: rejestry, bufor TX i jedna ramka w RXB0.
struct FakeMcp : ISpi {
    uint8_t reg[256] = {0};
    std::vector<std::vector<uint8_t>> log;
    bool rx_pending = false;
    uint8_t rxbuf[13] = {0};
    uint8_t txbuf[13] = {0};
    bool rts = false;

    bool transfer(const uint8_t* tx, uint8_t* rx, size_t len) override {
        log.emplace_back(tx, tx + len);
        memset(rx, 0, len);
        switch (tx[0]) {
            case 0xC0: memset(reg, 0, sizeof reg); reg[0x0E] = 0x80; break;
            case 0x02:
                reg[tx[1]] = tx[2];
                if (tx[1] == 0x0F) reg[0x0E] = tx[2] & 0xE0;
                break;
            case 0x03: rx[2] = reg[tx[1]]; break;
            case 0x05: reg[tx[1]] = (reg[tx[1]] & ~tx[2]) | (tx[3] & tx[2]); break;
            case 0x40: memcpy(txbuf, tx + 1, len - 1); break;
            case 0x81: rts = true; break;
            case 0x90: memcpy(rx + 1, rxbuf, 13); rx_pending = false; break;
        }
        if (rx_pending) reg[0x2C] |= 0x01; else reg[0x2C] &= ~0x01;
        return true;
    }
};

static void test_sdo() {
    CanFrame r = sdo_read_request(4, 0x2207, 1);
    assert(r.id == 0x604 && r.dlc == 8 && r.data[0] == 0x40);
    assert(r.data[1] == 0x07 && r.data[2] == 0x22 && r.data[3] == 1);

    CanFrame w = sdo_write_request(4, 0x2207, 1, 269, 2);
    assert(w.id == 0x604 && w.data[0] == 0x2B && w.data[4] == 0x0D && w.data[5] == 0x01);
    assert(sdo_write_request(4, 1, 1, 1, 3).id == 0);

    // odpowiedź 2 bajty: 0x4B, wartość 269
    CanFrame a; a.id = 0x584; a.dlc = 8;
    a.data[0] = 0x4B; a.data[1] = 0x07; a.data[2] = 0x22; a.data[3] = 1; a.data[4] = 0x0D; a.data[5] = 0x01;
    SdoReply p = sdo_parse_reply(4, a);
    assert(p.status == SdoStatus::Ok && !p.is_write_ack && p.index == 0x2207 && p.sub == 1);
    assert(p.size == 2 && p.value == 269);
    assert(sdo_parse_reply(5, a).status == SdoStatus::BadFrame);  // zły węzeł

    a.data[0] = 0x43; a.data[4] = 0x78; a.data[5] = 0x56; a.data[6] = 0x34; a.data[7] = 0x12;
    p = sdo_parse_reply(4, a);
    assert(p.size == 4 && p.value == 0x12345678);

    CanFrame ack; ack.id = 0x584; ack.dlc = 8; ack.data[0] = 0x60;
    ack.data[1] = 0x07; ack.data[2] = 0x22; ack.data[3] = 1;
    p = sdo_parse_reply(4, ack);
    assert(p.status == SdoStatus::Ok && p.is_write_ack && p.index == 0x2207);

    CanFrame ab; ab.id = 0x584; ab.dlc = 8; ab.data[0] = 0x80;
    ab.data[1] = 0x07; ab.data[2] = 0x22; ab.data[3] = 1;
    ab.data[4] = 0x02; ab.data[7] = 0x06;  // 0x06000002 – obiekt nie istnieje
    p = sdo_parse_reply(4, ab);
    assert(p.status == SdoStatus::Abort && p.abort_code == 0x06000002);
}

static void test_codec() {
    assert(decode(Encoding::FlagByte, 269).value == 13);
    assert(encode(Encoding::FlagByte, 13).raw == 269);
    assert(encode(Encoding::FlagByte, 256).ok == false);
    assert(decode(Encoding::Plain, 17).value == 17);
    assert(decode(Encoding::Tenths, 46).value == 4.6);
    assert(encode(Encoding::Tenths, 4.6).raw == 46);
    assert(decode(Encoding::Switch, 257).value == 1);
    assert(!decode(Encoding::Switch, 5).ok);
    assert(encode(Encoding::Switch, 0).raw == 256);
    assert(encode(Encoding::EnumList, 3).raw == 259);
    assert(encode(Encoding::Mask24, 0xFFFFFF).ok);
    assert(!encode(Encoding::Mask24, 0x1000000).ok);
    assert(!encode(Encoding::Plain, -1).ok);
    assert(decode(Encoding::FlagTenths, 256 + 46).value == 4.6);
}

static void test_mcp() {
    FakeMcp spi;
    Mcp2515 can(spi);
    assert(can.begin(CanSpeed::K125, CanClock::MHz16, CanMode::Normal));
    assert(spi.reg[0x2A] == 0x03 && spi.reg[0x29] == 0xF0 && spi.reg[0x28] == 0x86);
    assert(spi.reg[0x0F] == 0x00);

    CanFrame f = sdo_read_request(4, 0x2207, 1);
    assert(can.send(f));
    assert(spi.rts);
    assert(spi.txbuf[0] == (0x604 >> 3) && spi.txbuf[1] == ((0x604 & 7) << 5));
    assert(spi.txbuf[4] == 8 && spi.txbuf[5] == 0x40);

    // przychodzi odpowiedź 0x584
    spi.rxbuf[0] = 0x584 >> 3; spi.rxbuf[1] = (0x584 & 7) << 5; spi.rxbuf[4] = 8;
    spi.rxbuf[5] = 0x4B; spi.rxbuf[6] = 0x07; spi.rxbuf[7] = 0x22; spi.rxbuf[8] = 1;
    spi.rxbuf[9] = 0x0D; spi.rxbuf[10] = 0x01;
    spi.rx_pending = true; spi.reg[0x2C] = 0x01;
    CanFrame in;
    assert(can.receive(in));
    assert(in.id == 0x584 && in.dlc == 8);
    SdoReply p = sdo_parse_reply(4, in);
    assert(p.status == SdoStatus::Ok && p.value == 269);
    assert(!can.receive(in));  // nic więcej

    // zajęty bufor TX
    spi.reg[0x30] = 0x08;
    assert(!can.send(f));
}

int main() {
    test_sdo();
    test_codec();
    test_mcp();
    puts("OK: wszystkie testy przeszly");
    return 0;
}
