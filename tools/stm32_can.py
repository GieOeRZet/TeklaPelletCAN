#!/usr/bin/env python3
"""NewEstyma: model CAN2 (bxCAN, 0x40006800) dla tools/cortexm_rtos.py.
TX: firmware (RUNTIME 0x08071734) wybiera wolna skrzynke z TSR (bity 26..28 TME0..2), zapisuje TIxR/TDTxR/TDLxR/TDHxR i ustawia TXRQ (TIxR bit0).
    Model ustawia TME w TSR przy starcie, a po TXRQ przechwytuje ramke do `tx` (dict id/dlc/data/ext), zeruje TXRQ.
RX: inject(id, data) wpisuje ramke do skrzynki FIFO0 (RIR@+0x1B0, RDTR@+0x1B4, RDLR@+0x1B8, RDHR@+0x1BC), RF0R.FMP0=1 i zglasza IRQ 64 (CAN2_RX0).
    ISR firmware (0x0807F9F8 -> serializer 0x080717DC) zwalnia FIFO zapisem RF0R.RFOM0 (bit 5), wiec model nic wiecej nie musi robic.
Ograniczenia: tylko FIFO0, brak filtrow, brak bledow/BUSOFF, brak IRQ TX (CAN2_TX IRQ 63)."""
import struct
from unicorn import UC_HOOK_MEM_WRITE, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_PC
CAN2 = 0x40006800
TSR, RF0R, TI0 = 0x08, 0x0C, 0x180

class Can2:
    def __init__(self, board, rx_irq=64):
        self.b, self.rx_irq = board, rx_irq
        self.tx, self.rx_log = [], []
        board.wr(CAN2 + TSR, 0x1C000000)                    # TME0..2 = skrzynki puste
        board.mu.hook_add(UC_HOOK_MEM_WRITE, self._tx_write, begin=CAN2 + TI0, end=CAN2 + TI0 + 0x2F)

    def _tx_write(self, uc, access, addr, size, val, ud):
        off = addr - (CAN2 + TI0)
        if off % 16 == 0 and val & 1:                       # TIxR.TXRQ
            mb = off // 16
            pc = uc.reg_read(UC_ARM_REG_PC) & ~1
            h = struct.unpack("<H", bytes(uc.mem_read(pc, 2)))[0]
            nxt = pc + (4 if (h >> 11) in (0x1D, 0x1E, 0x1F) else 2)
            def once(u, a, sz, ud2, self=self, mb=mb):
                u.hook_del(self._h); self._capture(mb)
            self._h = uc.hook_add(UC_HOOK_CODE, once, begin=nxt, end=nxt)

    def _capture(self, mb):
        b = self.b; base = CAN2 + TI0 + 16 * mb
        tir, tdt, tdl, tdh = (b.rd(base + o) for o in (0, 4, 8, 12))
        ide = tir >> 2 & 1
        fr = dict(mb=mb, ext=ide, id=(tir >> 3) if ide else (tir >> 21), dlc=tdt & 0xF, data=(struct.pack("<II", tdl, tdh))[: tdt & 0xF], tick=b.counters["systick"])
        self.tx.append(fr); b.wr(base, tir & ~1)             # TXRQ wyzerowane przez sprzet
        b.wr(CAN2 + TSR, b.rd(CAN2 + TSR) | 0x1C000000 | (3 << (8 * mb)))   # TME + RQCP/TXOK

    def inject(self, stdid, data, ext=False):
        b = self.b; d = bytes(data) + b"\0" * (8 - len(data)); lo, hi = struct.unpack("<II", d)
        b.wr(CAN2 + 0x1B0, (stdid << 3 | 4) if ext else (stdid << 21)); b.wr(CAN2 + 0x1B4, len(data) & 0xF)
        b.wr(CAN2 + 0x1B8, lo); b.wr(CAN2 + 0x1BC, hi); b.wr(CAN2 + RF0R, (b.rd(CAN2 + RF0R) & ~3) | 1)
        self.rx_log.append((stdid, bytes(data))); b.raise_irq(self.rx_irq)
