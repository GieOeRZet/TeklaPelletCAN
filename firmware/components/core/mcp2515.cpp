#include "mcp2515.h"

namespace tpc {

namespace {
constexpr uint8_t CMD_RESET = 0xC0, CMD_READ = 0x03, CMD_WRITE = 0x02, CMD_BITMOD = 0x05;
constexpr uint8_t CMD_LOAD_TX0 = 0x40, CMD_RTS_TX0 = 0x81;
constexpr uint8_t CMD_READ_RX0 = 0x90, CMD_READ_RX1 = 0x94;

constexpr uint8_t REG_CANSTAT = 0x0E, REG_CANCTRL = 0x0F;
constexpr uint8_t REG_CNF3 = 0x28, REG_CNF2 = 0x29, REG_CNF1 = 0x2A;
constexpr uint8_t REG_CANINTF = 0x2C, REG_EFLG = 0x2D;
constexpr uint8_t REG_TXB0CTRL = 0x30;
constexpr uint8_t REG_RXB0CTRL = 0x60, REG_RXB1CTRL = 0x70;

constexpr uint8_t MODE_NORMAL = 0x00, MODE_CONFIG = 0x80, MODE_LISTEN = 0x60;
constexpr uint8_t INTF_RX0 = 0x01, INTF_RX1 = 0x02;
constexpr uint8_t TXREQ = 0x08;
}  // namespace

bool Mcp2515::write_reg(uint8_t addr, uint8_t value) {
    const uint8_t tx[3] = {CMD_WRITE, addr, value};
    uint8_t rx[3];
    return spi_.transfer(tx, rx, 3);
}

bool Mcp2515::read_reg(uint8_t addr, uint8_t& value) {
    const uint8_t tx[3] = {CMD_READ, addr, 0};
    uint8_t rx[3] = {0, 0, 0};
    if (!spi_.transfer(tx, rx, 3)) return false;
    value = rx[2];
    return true;
}

bool Mcp2515::bit_modify(uint8_t addr, uint8_t mask, uint8_t value) {
    const uint8_t tx[4] = {CMD_BITMOD, addr, mask, value};
    uint8_t rx[4];
    return spi_.transfer(tx, rx, 4);
}

bool Mcp2515::begin(CanSpeed, CanClock clock, CanMode mode) {
    const uint8_t reset = CMD_RESET;
    uint8_t rx;
    if (!spi_.transfer(&reset, &rx, 1)) return false;

    // Wejście w tryb konfiguracji i sprawdzenie.
    if (!write_reg(REG_CANCTRL, MODE_CONFIG)) return false;
    uint8_t st = 0;
    if (!read_reg(REG_CANSTAT, st) || (st & 0xE0) != MODE_CONFIG) return false;

    // 125 kbit/s: wartości jak w bibliotece mcp_can.
    uint8_t cnf1, cnf2, cnf3;
    if (clock == CanClock::MHz16) { cnf1 = 0x03; cnf2 = 0xF0; cnf3 = 0x86; }
    else                          { cnf1 = 0x01; cnf2 = 0xF1; cnf3 = 0x85; }  // 8 MHz
    if (!write_reg(REG_CNF1, cnf1) || !write_reg(REG_CNF2, cnf2) || !write_reg(REG_CNF3, cnf3)) return false;

    // Odbiór wszystkich ramek (maski/filtry wyłączone), RXB0 przelewa do RXB1.
    if (!write_reg(REG_RXB0CTRL, 0x64) || !write_reg(REG_RXB1CTRL, 0x60)) return false;
    if (!write_reg(REG_CANINTF, 0x00)) return false;

    const uint8_t target = (mode == CanMode::ListenOnly) ? MODE_LISTEN : MODE_NORMAL;
    if (!write_reg(REG_CANCTRL, target)) return false;
    if (!read_reg(REG_CANSTAT, st) || (st & 0xE0) != target) return false;
    return true;
}

bool Mcp2515::send(const CanFrame& f) {
    if (f.dlc > 8 || f.id > 0x7FF) return false;
    uint8_t ctrl;
    if (!read_reg(REG_TXB0CTRL, ctrl) || (ctrl & TXREQ)) return false;  // bufor zajęty

    uint8_t tx[1 + 5 + 8] = {CMD_LOAD_TX0};
    tx[1] = f.id >> 3;
    tx[2] = (f.id & 0x07) << 5;
    tx[3] = 0;
    tx[4] = 0;
    tx[5] = f.dlc;
    for (uint8_t i = 0; i < f.dlc; i++) tx[6 + i] = f.data[i];
    uint8_t rx[sizeof(tx)];
    if (!spi_.transfer(tx, rx, 6 + f.dlc)) return false;

    const uint8_t rts = CMD_RTS_TX0;
    return spi_.transfer(&rts, rx, 1);
}

bool Mcp2515::receive(CanFrame& f) {
    uint8_t flags;
    if (!read_reg(REG_CANINTF, flags)) return false;
    uint8_t cmd, clear;
    if (flags & INTF_RX0)      { cmd = CMD_READ_RX0; clear = INTF_RX0; }
    else if (flags & INTF_RX1) { cmd = CMD_READ_RX1; clear = INTF_RX1; }
    else return false;

    uint8_t tx[14] = {cmd};
    uint8_t rx[14] = {0};
    if (!spi_.transfer(tx, rx, 14)) return false;  // rx[1..13] = SIDH..D7
    // Ramki rozszerzone (IDE) ignorujemy – kocioł używa 11 bitów.
    const bool extended = rx[2] & 0x08;
    f.id = (rx[1] << 3) | (rx[2] >> 5);
    f.dlc = rx[5] & 0x0F;
    if (f.dlc > 8) f.dlc = 8;
    for (uint8_t i = 0; i < 8; i++) f.data[i] = rx[6 + i];
    // Czytanie przez komendę READ RX BUFFER zeruje flagę, ale bezpiecznie czyścimy.
    bit_modify(REG_CANINTF, clear, 0x00);
    return !extended;
}

void Mcp2515::clear_error_flags() { write_reg(REG_EFLG, 0x00); }

uint8_t Mcp2515::error_flags() {
    uint8_t v = 0;
    read_reg(REG_EFLG, v);
    return v;
}

}  // namespace tpc
