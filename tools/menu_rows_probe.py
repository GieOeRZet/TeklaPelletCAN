#!/usr/bin/env python3
"""NewEstyma PASS 40: budowa ekranu menu glownego w emulatorze i odczyt argumentow row-buildera FUN_0804BC6C (RUNTIME 0x0805BC6C).
python3 -I tools/menu_rows_probe.py FW2213TK_kopia.bin [out.csv]
Kompletny konstruktor ekranu: RUNTIME 0x0804BF7C (PROJECT 0x0803BF7C; wola konstruktor bazowy 0x08051D18, tablice 21x0x274 @ +0x42C).
Wiersze wypelnia FUN_08042160 (RUNTIME 0x08052160); poziom dostepu czytany z modelu [FUN_080414BA()+0x158].
UWAGA: po zbudowaniu wierszy emulacja konczy sie wywolaniem przez NULL (dalsze, niemodelowane obiekty) - dane wierszy sa juz wtedy zebrane."""
import csv, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import emu_startup as E
from unicorn import UcError, UC_HOOK_CODE
from unicorn.arm_const import *
SENT, OBJ, ROW0, STRIDE, BUILDER = 0x08010002, 0x20030000, 0x20030000 + 0x42C, 0x274, 0x0805BC6C

def build(binpath, access):
    mu, raw = E.boot(binpath)
    mu.hook_add(UC_HOOK_CODE, lambda uc, a, s, u: uc.emu_stop(), begin=SENT & ~1, end=SENT & ~1)
    def call(fn, r0=0):
        mu.reg_write(UC_ARM_REG_R0, r0); mu.reg_write(UC_ARM_REG_LR, SENT | 1); mu.reg_write(UC_ARM_REG_SP, 0x2002F000)
        try: mu.emu_start(fn | 1, 0, count=30000000)
        except UcError: pass
        return mu.reg_read(UC_ARM_REG_R0)
    model = call(0x080414BA); mu.mem_write(model + 0x158, bytes([access]))
    call(0x0804BF7C, OBJ)
    calls = []
    mu.hook_add(UC_HOOK_CODE, lambda uc, a, s, u: calls.append((uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_R1), uc.reg_read(UC_ARM_REG_R2))), begin=BUILDER, end=BUILDER)
    call(0x08052160, OBJ)
    return [((r - ROW0) // STRIDE, a, b) for r, a, b in calls], raw

if __name__ == "__main__":
    rows0, raw = build(sys.argv[1], 0); rows3, _ = build(sys.argv[1], 3)
    assert [r[0] for r in rows0] == list(range(15)) and [r[0] for r in rows3] == list(range(21)), (rows0, rows3)   # access 0 -> 15 wierszy, access 3 -> 21
    assert rows3[:15] == rows0
    out = sys.argv[2] if len(sys.argv) > 2 else None
    if out:
        with open(out, "w", newline="") as f:
            w = csv.writer(f); w.writerow(["row", "built_at_access", "bitmap_A", "bitmap_B"])
            for r, a, b in rows3: w.writerow([r, 0 if r < 15 else ">0", a, b])
    print("OK: menu_rows_probe  (access0: %d wierszy, access3: %d wierszy)" % (len(rows0), len(rows3)))
