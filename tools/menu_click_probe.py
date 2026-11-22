#!/usr/bin/env python3
"""NewEstyma PASS 41: 'klikniecie' wiersza menu = wywolanie handlera przycisku FUN_0807EB00 (RUNTIME 0x0808EB00) w emulatorze.
python3 -I tools/menu_click_probe.py FW2213TK_kopia.bin [out.csv]
Handler(this=ekran, sender=&wiersz): szuka indeksu i, dla ktorego sender == this[+0x3B4] + i*0x274 (liczba wierszy: bajt this+0x3B8),
po czym wola FUN_0803C064 (RUNTIME 0x0804C064) z (this[+0x3C], i) -> klasa = tablica 0x20005EF0[i] -> TBB.
Siostrzany handler FUN_0807EB36 (RUNTIME 0x0808EB36) robi to samo z FUN_0804EC18 (drugi callback; nie badany).
Harness: poziom dostepu 3, obiekt presentera [this+0x3C] = pusty obszar, kolejka TX stubowana."""
import csv, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import emu_startup as E
from unicorn import UcError, UC_HOOK_CODE
from unicorn.arm_const import *
SENT, OBJ, PRES = 0x08010002, 0x20030000, 0x20034000

def run(binpath):
    mu, raw = E.boot(binpath)
    mu.hook_add(UC_HOOK_CODE, lambda uc, a, s, u: uc.emu_stop(), begin=SENT & ~1, end=SENT & ~1)
    mu.hook_add(UC_HOOK_CODE, lambda uc, a, s, u: (uc.reg_write(UC_ARM_REG_R0, 1), uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))), begin=0x08067224, end=0x08067224)
    def call(fn, r0=0, r1=0):
        mu.reg_write(UC_ARM_REG_R0, r0); mu.reg_write(UC_ARM_REG_R1, r1); mu.reg_write(UC_ARM_REG_LR, SENT | 1); mu.reg_write(UC_ARM_REG_SP, 0x2002F000)
        try: mu.emu_start(fn | 1, 0, count=30000000); return None
        except UcError: return "ERR pc=0x%X" % mu.reg_read(UC_ARM_REG_PC)
    rd = lambda a, n=1: int.from_bytes(mu.mem_read(a, n), "little")
    model = mu.reg_read(UC_ARM_REG_R0) if call(0x080414BA) is None else 0
    model = mu.reg_read(UC_ARM_REG_R0); mu.mem_write(model + 0x158, b"\x03")
    call(0x0804BF7C, OBJ); call(0x08052160, OBJ); mu.mem_write(OBJ + 0x3C, struct.pack("<I", PRES))
    snap = lambda: dict(key3=rd(0x20021FAA), lang=rd(0x20024860, 2), ctx12A=rd(model + 0x12A), ctx12B=rd(model + 0x12B), ctx12C=rd(model + 0x12C))
    rows = []
    for i in range(21):
        b = snap(); err = call(0x0808EB00, OBJ, OBJ + 0x42C + i * 0x274); a = snap()
        rows.append(dict(row=i, cls=rd(0x20005EF0 + i), before=b, after=a, error=err or "", changed={k: (b[k], a[k]) for k in b if b[k] != a[k]}))
    return rows

if __name__ == "__main__":
    rows = run(sys.argv[1]); ch = {r["row"]: r["changed"] for r in rows}
    assert ch[15] == {"key3": (0, 1), "lang": (0, 1)}, ch[15]                                   # wiersz 15 (klasa 12) = zmiana jezyka
    assert [ch[i].get("ctx12B", (0, 0))[1] for i in (3, 4, 5)] == [2, 3, 4] and [ch[i].get("ctx12C", (0, 0))[1] for i in (3, 4, 5)] == [2, 3, 4]   # CO2..CO4
    assert ch[1].get("ctx12B", (0, 0))[1] == 10 and ch[13].get("ctx12B", (0, 0))[1] == 16 and ch[18].get("ctx12B", (0, 0))[1] == 17
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w", newline="") as f:
            w = csv.writer(f); w.writerow(["row", "class", "changed", "error"])
            for r in rows: w.writerow([r["row"], r["cls"], ";".join("%s:%d->%d" % (k, v[0], v[1]) for k, v in r["changed"].items()), r["error"]])
    print("OK: menu_click_probe")
