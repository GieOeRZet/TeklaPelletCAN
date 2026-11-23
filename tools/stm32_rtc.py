#!/usr/bin/env python3
"""NewEstyma PASS 52: model RTC STM32F4 (0x40002800) dla tools/cortexm_rtos.py.
TR +0x00 / DR +0x04 (BCD, format 24 h), CR +0x08, ISR +0x0C (INITS b4, RSF b5, INITF b6, INIT b7), WPR +0x24 (klucze 0xCA/0x53 ignorowane).
Czas biezacy = start + (systick / ticks_per_s) sekund; zapis TR/DR w trybie INIT (ISR.INIT=1) przesuwa zegar.
Odczyt TR/DR zwraca aktualny czas (zapis do pamieci w hooku odczytu). Dzien tygodnia: konwencja FIRMWARE WDU = 0 (pon) .. 6 (niedz) (przy WDU=1 panel pokazuje "Wtorek")."""
import datetime
from unicorn import UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
TR, DR, CR, ISR = 0x00, 0x04, 0x08, 0x0C
def bcd(v): return ((v // 10) << 4) | (v % 10)
def unbcd(v): return ((v >> 4) & 0xF) * 10 + (v & 0xF)
class Rtc:
    def __init__(self, board, base=0x40002800, start=None, ticks_per_s=1000):
        self.b, self.base, self.tps = board, base, ticks_per_s
        self.start = start or datetime.datetime(2000, 11, 30, 0, 0, 0)
        self.t0 = board.counters["systick"]
        board.wr(base + ISR, 0x30)                                   # INITS | RSF
        board.mu.hook_add(UC_HOOK_MEM_READ, self._r, begin=base, end=base + 0xF)
        board.mu.hook_add(UC_HOOK_MEM_WRITE, self._w, begin=base, end=base + 0x3F)
    def now(self):
        return self.start + datetime.timedelta(seconds=(self.b.counters["systick"] - self.t0) / self.tps)
    def _r(self, uc, access, addr, size, val, ud):
        off = addr - self.base; n = self.now()
        if off == TR: self.b.wr(self.base + TR, (bcd(n.hour) << 16) | (bcd(n.minute) << 8) | bcd(n.second))
        elif off == DR: self.b.wr(self.base + DR, (bcd(n.year % 100) << 16) | ((n.isoweekday() - 1) << 13) | (bcd(n.month) << 8) | bcd(n.day))
    def _w(self, uc, access, addr, size, val, ud):
        off = addr - self.base
        if off == ISR:
            init = bool(val & 0x80); self.b.wr(self.base + ISR, (val & ~0x40 & 0xFFFFFFFF) | (0x40 if init else 0) | 0x30)
        elif off in (TR, DR) and self.b.rd(self.base + ISR) & 0x80:
            n = self.now()
            if off == TR: h, m, s = unbcd(val >> 16 & 0x3F), unbcd(val >> 8 & 0x7F), unbcd(val & 0x7F); n = n.replace(hour=h % 24, minute=m % 60, second=s % 60)
            else:
                y, mo, d = 2000 + unbcd(val >> 16 & 0xFF), unbcd(val >> 8 & 0x1F), unbcd(val & 0x3F)
                try: n = n.replace(year=y, month=mo or 1, day=d or 1)
                except ValueError: pass
            self.start = n; self.t0 = self.b.counters["systick"]
