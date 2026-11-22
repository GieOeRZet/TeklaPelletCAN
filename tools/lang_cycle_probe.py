#!/usr/bin/env python3
"""NewEstyma PASS 39: wykonanie sciezki class 12 (jezyk) w firmware. python3 -I tools/lang_cycle_probe.py FW2213TK_kopia.bin
Sekwencja jak w RAW 0x3C12A (RUNTIME 0x0804C12A): r = F473BA(); F473E6(r+1) -> zapis key 3 mod 8 + setLanguage (tail-call 0x080491D6)."""
import os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import emu_startup as E
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
SENT, KEY3, CURLANG = 0x08010002, 0x20021FAA, 0x20024860
mu, raw = E.boot(sys.argv[1])
mu.hook_add(UC_HOOK_CODE, lambda uc, a, s, u: uc.emu_stop(), begin=SENT & ~1, end=SENT & ~1)
mu.hook_add(UC_HOOK_CODE, lambda uc, a, s, u: (uc.reg_write(UC_ARM_REG_R0, 1), uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))), begin=0x08067224, end=0x08067224)
def call(fn, r0=0, r1=0):
    mu.reg_write(UC_ARM_REG_R0, r0); mu.reg_write(UC_ARM_REG_R1, r1); mu.reg_write(UC_ARM_REG_LR, SENT | 1); mu.reg_write(UC_ARM_REG_SP, 0x20011000)
    mu.emu_start(fn | 1, 0, count=3000000); return mu.reg_read(UC_ARM_REG_R0)
rd = lambda a, n: int.from_bytes(mu.mem_read(a, n), "little")
LANG = ["PL", "EN", "LT", "SK", "CZ", "ES", "RO", "EST"]
seq = []
for step in range(10):
    r = call(0x080473BA); res = call(0x080473E6, 0, (r + 1) & 0xFFFF)
    seq.append((rd(KEY3, 1), rd(CURLANG, 2)))
    print("krok %d: GET=%d -> key3=%d, currentLanguage=%d (%s)" % (step + 1, r, seq[-1][0], seq[-1][1], LANG[seq[-1][1] & 7]))
assert [s[0] for s in seq] == [1, 2, 3, 4, 5, 6, 7, 0, 1, 2], seq        # cykl 0..7 mod 8
assert [s[1] for s in seq] == [s[0] for s in seq]                         # currentLanguage == key3
print("OK: lang_cycle_probe")
