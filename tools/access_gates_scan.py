#!/usr/bin/env python3
"""NewEstyma PASS 47: skaner WSZYSTKICH odczytow poziomu dostepu ([model+0x158]) w firmware wraz z nastepujacym porownaniem.
python3 -I tools/access_gates_scan.py FW2213TK_kopia.bin out.csv
Szuka w calym BIN instrukcji `ldrb.w Rt,[Rn,#0x158]` (T3: F89n | Rt<<12|0x158) i `ldrb Rt,[Rn,#imm]` po `add Rn,#0x158`-podobnych uzyciach pomijamy (tylko ten wzorzec).
Dla kazdego trafienia dezasembluje 14 kolejnych instrukcji i wylicza prog: cbz/cbnz (==0 / !=0), cmp #N + bCC (==N, !=N, >=N, <N, >N), subs/orrs. Wynik to HEURYSTYKA
klasyfikacji progu — twardym dowodem jest sama lista instrukcji w kolumnie `ctx`. Adresy RUNTIME (PROJECT = -0x10000)."""
import csv, struct, sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
B = 0x08010000
raw = open(sys.argv[1], "rb").read(); md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
def func_start(o):
    """najblizszy wczesniejszy `push {...,lr}` (T1 0xB5xx albo T2 E92D 4xxx) w oknie 4 KB"""
    for k in range(o, max(0, o - 4096), -2):
        h = struct.unpack_from("<H", raw, k)[0]
        if (h & 0xFF00) == 0xB500: return B + k
        if h == 0xE92D and struct.unpack_from("<H", raw, k + 2)[0] & 0x4000: return B + k
    return None
rows = []
for o in range(0, len(raw) - 4, 2):
    h1, h2 = struct.unpack_from("<HH", raw, o)
    if (h1 & 0xFFF0) == 0xF890 and (h2 & 0xFFF) == 0x158:
        ins = list(md.disasm(raw[o:o + 64], B + o, count=14)); ctx = " ; ".join("%s %s" % (i.mnemonic, i.op_str) for i in ins[:9])
        thr = "?"; reg = "r%d" % (h2 >> 12) if (h2 >> 12) < 13 else "?"
        for i in ins[1:10]:
            m, ops = i.mnemonic, i.op_str.replace(" ", "")
            if m in ("cbz", "cbnz"): thr = "==0" if m == "cbz" else "!=0"; break
            if m == "cmp" and ops.startswith(reg + ",#"):
                n = int(ops.split("#")[1], 0); nxt = next((x for x in ins[ins.index(i) + 1:ins.index(i) + 4] if x.mnemonic.startswith(("b", "it"))), None)
                thr = "cmp#%d %s" % (n, nxt.mnemonic if nxt else ""); break
            if m in ("subs", "sub") and ops.startswith(reg + ","): thr = "sub#" + ops.split("#")[-1]; break
        rows.append(dict(addr="0x%08X" % (B + o), func="0x%08X" % func_start(o) if func_start(o) else "", reg=reg, thr=thr, ctx=ctx))
with open(sys.argv[2], "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["addr", "func", "reg", "thr", "ctx"]); w.writeheader(); w.writerows(rows)
import collections
print("odczytow [..+0x158]:", len(rows), "| funkcji:", len({r["func"] for r in rows}), "| progi:", dict(collections.Counter(r["thr"] for r in rows).most_common(12)))
