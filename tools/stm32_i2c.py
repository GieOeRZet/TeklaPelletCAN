#!/usr/bin/env python3
"""NewEstyma: model I2C (STM32F4 v1) dla tools/cortexm_rtos.py — master, flagi statyczne ustawiane przy zdarzeniach zapisu.
Rejestry: CR1 0x00 (START bit8, STOP bit9, ACK bit10, SWRST bit15), DR 0x10, SR1 0x14 (SB b0, ADDR b1, BTF b2, RXNE b6, TXE b7, AF b10), SR2 0x18 (MSL b0, BUSY b1, TRA b2).
Zdarzenia: START -> SB=1, SR2=MSL|BUSY; zapis adresu do DR -> ADDR=1 (jesli slave istnieje, inaczej AF=1), TRA wg bitu R/W; zapis danych -> log + TXE|BTF; STOP -> SR1=TXE, SR2=0.
Slave'y: dict {adres7: obiekt z write(byte) / read() -> byte}. Log: self.log (tick, addr, 'W'/'R', dane). Brak przerwan i DMA.
Ograniczenie: flagi sa statyczne (nie kasuja sie po odczycie SR1/SR2); wystarcza dla typowych petli SPL (I2C_CheckEvent)."""
import struct
from unicorn import UC_HOOK_MEM_WRITE, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_PC
CR1, DR, SR1, SR2 = 0x00, 0x10, 0x14, 0x18

class I2C:
    def __init__(self, board, base=0x40005400, slaves=None):
        self.b, self.base, self.slaves = board, base, slaves or {}
        self.log, self.state, self.addr, self.rw, self.rd_buf = [], "idle", None, 0, b""
        board.wr(base + SR1, 0x80, 2); board.wr(base + SR2, 0, 2)
        board.mu.hook_add(UC_HOOK_MEM_WRITE, self._w, begin=base, end=base + 0x3F)
        from unicorn import UC_HOOK_MEM_READ
        board.mu.hook_add(UC_HOOK_MEM_READ, self._r, begin=base + DR, end=base + DR + 3)

    def _after(self, fn):
        """wykonaj fn() PO biezacej instrukcji zapisu (zeby nie nadpisac wartosci zapisywanej przez firmware)"""
        uc = self.b.mu; pc = uc.reg_read(UC_ARM_REG_PC) & ~1
        h = struct.unpack("<H", bytes(uc.mem_read(pc, 2)))[0]; nxt = pc + (4 if (h >> 11) in (0x1D, 0x1E, 0x1F) else 2)
        holder = []
        def once(u, a, sz, ud):
            u.hook_del(holder[0]); fn()
        holder.append(uc.hook_add(UC_HOOK_CODE, once, begin=nxt, end=nxt))

    def _set(self, sr1, sr2): self.b.wr(self.base + SR1, sr1, 2); self.b.wr(self.base + SR2, sr2, 2)
    def _w(self, uc, access, addr, size, val, ud):
        off = addr - self.base
        if off == CR1:
            if val & 0x8000: self.state = "idle"; self._after(lambda: (self.b.wr(self.base + CR1, val & ~0x8000, 2), self._set(0x80, 0)))
            if val & 0x100:                                     # START
                self.state = "addr"; self._after(lambda: (self.b.wr(self.base + CR1, self.b.rd(self.base + CR1, 2) & ~0x100, 2), self._set(0x81, 3)))
            if val & 0x200:                                     # STOP
                self.state = "idle"; self._after(lambda: (self.b.wr(self.base + CR1, self.b.rd(self.base + CR1, 2) & ~0x200, 2), self._set(0x80, 0)))
        elif off == DR:
            v = val & 0xFF; t = self.b.counters["systick"]
            if self.state == "addr":
                self.addr, self.rw = v >> 1, v & 1; ok = self.addr in self.slaves
                self.log.append((t, self.addr, "R" if self.rw else "W", None)); self.state = "data"
                if ok and not self.rw and hasattr(self.slaves[self.addr], "start_write"): self.slaves[self.addr].start_write()
                if ok and self.rw: self.rd_buf = self.slaves[self.addr].read_start() if hasattr(self.slaves[self.addr], "read_start") else b""
                self._after(lambda: self._set((0x86 if self.rw else 0x86) if ok else 0x480, (3 | (0 if self.rw else 4)) if ok else 3))
                if ok and self.rw: self._after(lambda: self._load_next())
            elif self.state == "data" and not self.rw:
                self.log.append((t, self.addr, "w", v))
                if self.addr in self.slaves: self.slaves[self.addr].write(v)
                self._after(lambda: self._set(0x86, 7))
    def _r(self, uc, access, addr, size, val, ud):
        if self.state == "data" and self.rw and self.addr in self.slaves: self._after(self._load_next)
    def _load_next(self):
        s = self.slaves.get(self.addr); v = s.read() if s else 0xFF
        self.b.wr(self.base + DR, v, 2); self._set(0xC6, 3)


class FT5x06:
    """FocalTech FT5x06 (adres 0x38): TD_STATUS 0x02, P1_XH 0x03 (zdarzenie<<6 | X[11:8]), P1_XL 0x04, P1_YH 0x05 (id<<4 | Y[11:8]), P1_YL 0x06.
    Zdarzenia: 0 = nacisniecie, 1 = zwolnienie, 2 = kontakt, 3 = brak. touch(x,y) -> nacisniecie (potem kontakt), release() -> zwolnienie (potem brak)."""
    def __init__(self): self.regs = bytearray(256); self.ptr = 0; self._first = True; self.regs[0x03] = 0xC0; self.regs[0x05] = 0x0F; self.pending = None; self.reads = []
    def start_write(self): self._first = True
    def write(self, v):
        if self._first: self.ptr = v; self._first = False
    def read_start(self): return b""
    def read(self):
        v = self.regs[self.ptr & 0xFF]; self.reads.append((self.ptr, v)); self.ptr += 1
        if self.ptr > 0x06 and self.pending is not None: self.regs[0x03] = self.pending[0]; self.pending = None
        return v
    def _set(self, ev, x, y, n):
        self.regs[0x02] = n; self.regs[0x03] = (ev << 6) | (x >> 8 & 15); self.regs[0x04] = x & 255; self.regs[0x05] = y >> 8 & 15; self.regs[0x06] = y & 255
    def touch(self, x, y): self.last = (x, y); self._set(0, x, y, 1); self.pending = (0x80 | (x >> 8 & 15),)   # po pierwszym odczycie -> kontakt (2)
    def release(self): x, y = getattr(self, 'last', (0, 0)); self._set(1, x, y, 0); self.pending = (0xC0,)   # zwolnienie niesie OSTATNIA pozycje (jak prawdziwy FT5x06)                          # po odczycie -> brak (3)
