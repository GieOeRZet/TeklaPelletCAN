#!/usr/bin/env python3
"""NewEstyma: publikacja lokalnych zmian parametrow (callback managera FUN_08010FCE, RUNTIME 0x08020FCE) w emulatorze.
python3 -I tools/publish_probe.py FW2213TK_kopia.bin  — zmienia storage 'Language' i sprawdza ramke 0x584/0x42 w kolejce TX.
Harness: function-level (patrz can_rx_inject.py); kolejka TX (RUNTIME 0x08067224) przechwytywana."""
import os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import emu_startup as E
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
MGR, SENT, CB = 0x20008D84, 0x08010002, 0x08020FCE
mu, raw = E.boot(sys.argv[1]); recs = []
def q(uc, a, s, u):
    recs.append(bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1), 20))); uc.reg_write(UC_ARM_REG_R0, 1); uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
mu.hook_add(UC_HOOK_CODE, q, begin=0x08067224, end=0x08067224)
mu.hook_add(UC_HOOK_CODE, lambda uc, a, s, u: uc.emu_stop(), begin=SENT & ~1, end=SENT & ~1)
def tick(n=1):
    for _ in range(n):
        mu.reg_write(UC_ARM_REG_R0, MGR); mu.reg_write(UC_ARM_REG_LR, SENT | 1); mu.reg_write(UC_ARM_REG_SP, 0x20011000); mu.emu_start(CB | 1, 0, count=3000000)
dec = lambda r: dict(sid=struct.unpack_from("<I", r, 0)[0], dlc=r[10], cmd=r[11], pid=r[12] | r[13] << 8, sub=r[14], val=int.from_bytes(r[15:19], "little"))
tick(200); base = len(recs)                       # ustalenie stanu poczatkowego (publikacje wartosci poczatkowych)
mu.mem_write(0x20021FAA, b"\x07"); tick(200)      # lokalna zmiana Language 0 -> 7
new = [dec(r) for r in recs[base:]]
assert len(new) == 1 and new[0]["sid"] == 0x584 and new[0]["dlc"] == 8 and new[0]["cmd"] == 0x42 and new[0]["pid"] == 3 and new[0]["sub"] == 1 and new[0]["val"] & 0xFF == 7, new
n2 = len(recs); tick(200); assert len(recs) == n2   # bez kolejnej zmiany: brak ponownej publikacji (shadow zaktualizowany)
print("OK: publish_probe  (baseline ramek: %d; po zmianie: 1 ramka %s)" % (base, new[0]))
