#!/usr/bin/env python3
"""NewEstyma PASS 46: listy parametrow ekranow USTAWIEN wg klasy strony i POZIOMU DOSTEPU — wprost z FUN_0803E714 (RUNTIME 0x0804E714).
python3 -I tools/panel_lists.py FW2213TK_kopia.bin runtime_param_table.csv resolver_t1.csv resolver_t2.csv out.csv
Funkcja czyta klase z modelu [MODEL+0x12B] i poziom [MODEL+0x158], dopisuje 16-bitowe klucze paneli do obiektu strony (param_1+0x20 + n*2, licznik param_1+0xE8)
a na koncu rozwiazuje je rezolwerem (FUN_08036FF2) i wola 0x0804842C (widgety). Harness: pusty obiekt strony w SRAM, model ustawiany bezposrednio; awaria po zapisie listy jest ignorowana
(lista jest juz w pamieci). Klucze rozwiazywane tabelami rezolwera: T1 (baza+instancja-1) i T2; klucze rejestru grafow (0x47/0x48) opisane osobno."""
import csv, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U
from unicorn import UcError, UC_HOOK_CODE
from unicorn.arm_const import *
FN, SENT, OBJ, MODEL = 0x0804E714, 0x08010002, 0x20034000, 0x20020784
def lists(binpath, classes, levels, insts=(1,)):
    s = U.UiSession(binpath); s.boot(400); b = s.b; mu = b.mu
    mu.hook_add(UC_HOOK_CODE, lambda uc, a, sz, u: uc.emu_stop(), begin=SENT & ~1, end=SENT & ~1)
    mu.hook_add(UC_HOOK_CODE, lambda uc, a, sz, u: (uc.reg_write(UC_ARM_REG_R0, 1), uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))), begin=0x08067224, end=0x08067224)
    out = []
    for lvl in levels:
        for cls in classes:
            for inst in insts:
                b.wr(MODEL + 0x158, lvl, 1); b.wr(MODEL + 0x12B, cls, 1); b.wr(MODEL + 0x12C, inst, 1)
                b.mu.mem_write(OBJ, b"\0" * 0x400); b.wr(OBJ + 8, MODEL, 4); b.wr(OBJ + 0x1C, OBJ + 0x200, 4)
                mu.reg_write(UC_ARM_REG_R0, OBJ); mu.reg_write(UC_ARM_REG_LR, SENT | 1); mu.reg_write(UC_ARM_REG_SP, 0x2002F000)
                err = ""
                try: mu.emu_start(FN | 1, 0, count=3000000)
                except UcError as e: err = str(e)
                n = b.rd(OBJ + 0xE8, 1); ids = [b.rd(OBJ + 0x20 + 2 * i, 2) for i in range(min(n, 120))]
                out.append(dict(level=lvl, cls=cls, inst=inst, n=n, ids=ids, err=err))
    return out
if __name__ == "__main__":
    rt = {int(r["key"], 16): r for r in csv.DictReader(open(sys.argv[2]))}
    t1 = {int(r["ui_key"], 16): int(r["value"], 16) for r in csv.DictReader(open(sys.argv[3]))}
    t2 = {int(r["ui_key"], 16): int(r["value"], 16) for r in csv.DictReader(open(sys.argv[4]))}
    res = lists(sys.argv[1], list(range(0, 0x12)), (0, 1, 2, 3))
    with open(sys.argv[5], "w", newline="") as f:
        w = csv.writer(f); w.writerow(["level", "cls", "inst", "idx", "panel_key", "src", "pid", "name", "list_len", "error"])
        for r in res:
            for i, k in enumerate(r["ids"]):
                if k in t1: pid, src = t1[k] + r["inst"] - 1, "T1"
                elif k in t2: pid, src = t2[k], "T2"
                else: pid, src = None, "?"
                w.writerow([r["level"], "0x%02X" % r["cls"], r["inst"], i, "0x%04X" % k, src, ("0x%04X" % pid) if pid is not None else "", rt.get(pid, {}).get("name", "") if pid is not None else "", r["n"], r["err"][:40]])
    print("OK", len(res), "list")
