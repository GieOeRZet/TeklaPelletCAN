#!/usr/bin/env python3
"""NewEstyma: wstrzykiwanie ramek odpowiedzi 0x0584 do prawdziwego kodu firmware (RX handler RUNTIME 0x08072A90; parser 0x08072B22)
i obserwacja storage. python3 -I tools/can_rx_inject.py FW2213TK_kopia.bin  (uruchamia testy zachowania).
Struktura kompaktowa przekazywana do handlera: {u16 StdId; u8 DLC; u8 Data[8]} (Data[0]=cmd, [1..2]=indeks LE, [3]=subindeks, [4..7]=wartosc LE).
Na szynie ta sama ramka: ID 0x584, DLC 8, dane = Data[0..7]. Harness stubuje kolejke TX (RUNTIME 0x08067224)."""
import os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import emu_startup as E
from unicorn.arm_const import *
from unicorn import UC_HOOK_CODE
OBJ, FR, SENT = 0x2002466C, 0x20012800, 0x08010002

class Rig:
    def __init__(self, binpath):
        self.mu, self.raw = E.boot(binpath); mu = self.mu
        mu.hook_add(UC_HOOK_CODE, lambda uc, a, s, u: uc.emu_stop(), begin=SENT & ~1, end=SENT & ~1)
        mu.hook_add(UC_HOOK_CODE, lambda uc, a, s, u: (uc.reg_write(UC_ARM_REG_R0, 1), uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))), begin=0x08067224, end=0x08067224)
        mu.mem_write(OBJ + 8, b"\x01"); mu.mem_write(OBJ + 0x10, b"\x01"); self.call(0x080729FC, OBJ)   # poller ustawia +0x0C (okno odpowiedzi)
    def call(self, fn, r0, r1=0):
        m = self.mu; m.reg_write(UC_ARM_REG_R0, r0); m.reg_write(UC_ARM_REG_R1, r1); m.reg_write(UC_ARM_REG_LR, SENT | 1); m.reg_write(UC_ARM_REG_SP, 0x20011000)
        m.emu_start(0x080729FC | 1 if fn == 0x080729FC else fn | 1, 0, count=500000)
    def rd(self, a, n=1): return int.from_bytes(self.mu.mem_read(a, n), "little")
    def respond(self, pid, val, cmd=0x42, sub=1, sid=0x584):
        f = struct.pack("<HB", sid, 8) + bytes([cmd, pid & 255, pid >> 8, sub]) + struct.pack("<I", val & 0xFFFFFFFF)
        self.mu.mem_write(FR, f + b"\0" * 8); self.call(0x08072A90, OBJ, FR)

if __name__ == "__main__":
    r = Rig(sys.argv[1]); L = 0x20021FAA
    def t(label, pid, val, st, n, expect, **kw):
        b = r.rd(st, n); r.respond(pid, val, **kw); a = r.rd(st, n); print("%-46s %d -> %d %s" % (label, b, a, "OK" if a == expect else "BLAD(oczekiwano %d)" % expect)); assert a == expect
    t("Language(u8 0..30) <- 5", 3, 5, L, 1, 5)
    t("Language <- 200 (poza zakresem)", 3, 200, L, 1, 5)
    t("Language <- 30 (max)", 3, 30, L, 1, 30)
    t("Language <- 31 (max+1)", 3, 31, L, 1, 30)
    t("Main module type 0x3500 <- 1", 0x3500, 1, 0x20021FAB, 1, 1)
    t("Main module type <- 7 (poza)", 0x3500, 7, 0x20021FAB, 1, 1)
    t("Language, cmd 0x60 (ack) <- 9", 3, 9, L, 1, 30, cmd=0x60)       # nie jest 0x42 -> ignorowane
    t("Language, subindeks 2 <- 9", 3, 9, L, 1, 30, sub=2)
    t("Language, StdId 0x585 <- 9", 3, 9, L, 1, 30, sid=0x585)
    S16 = 0x20020914   # 0x2016 Room measured temp, s16 -100..1500 (klasa 0, live)
    t("Room temp 0x2016 (s16) <- -50", 0x2016, -50 & 0xFFFF, S16, 2, 0xFFCE)
    t("Room temp <- -200 (ponizej min -100)", 0x2016, -200 & 0xFFFF, S16, 2, 0xFFCE)
    t("Room temp <- 1500 (max)", 0x2016, 1500, S16, 2, 1500)
    t("Room temp <- 1501 (powyzej max)", 0x2016, 1501, S16, 2, 1500)
    print("OK: can_rx_inject")
