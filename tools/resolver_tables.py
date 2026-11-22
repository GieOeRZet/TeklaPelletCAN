#!/usr/bin/env python3
"""NewEstyma: tabele rezolwera FUN_08036FF2 (logiczny klucz UI -> PID), czytane z BIN i laczone z tabela runtime.

python3 -I tools/resolver_tables.py FW2213TK_kopia.bin runtime_param_table_655.csv [out_prefix]

Ustalone z dezasemblacji rezolwera (RUNTIME 0x08046FF2; PROJECT 0x08036FF2):
 TABELA 1: RAW 0x37B48, rekordy 4 B (s16 klucz, u16 wartosc), 0x31 = 49 rekordow (licznik r2 liczy rekordy, nie bloki).
           Wynik = wartosc + instancja - 1, gdzie instancja = bajt [page_ctx+0x12C]  (rodziny CO1..CO4: baza, baza+1, ...).
           Klucz 0xA8 jest traktowany wprost jako rekord 0.
 TABELA 2: RAW 0x37578, rekordy 4 B (s16 klucz, u16 PID), 0x174 = 372 rekordy; wynik = PID wprost (bez instancji).
Po rezolucji: lookup w tabeli runtime (0x080215F6 runtime / 0x080115F6 PROJECT) po PID.
UWAGA (PASS 34): rekordy sa wyrownane do 4 B od bazy; odczyt przesuniety o 2 B daje falszywe pary (blad PASS 26).
"""
import csv, struct, sys
raw = open(sys.argv[1], "rb").read()
rt = {int(r["key"], 16): r for r in csv.DictReader(open(sys.argv[2]))}
T1, N1, T2, N2 = 0x37B48, 0x31, 0x37578, 0x174
def rows(base, n, inst):
    out = []
    for i in range(n):
        k, v = struct.unpack_from("<hH", raw, base + 4 * i)
        r = rt.get(v)
        out.append(dict(raw_off="0x%X" % (base + 4 * i), idx=i, ui_key="0x%04X" % (k & 0xFFFF), value="0x%04X" % v,
                        rule=("PID=value+inst-1" if inst else "PID=value"), in_runtime=int(r is not None),
                        name=r["name"] if r else ""))
    return out
t1, t2 = rows(T1, N1, True), rows(T2, N2, False)
print("T1 rekordow %d, w runtime %d ; T2 rekordow %d, w runtime %d" % (len(t1), sum(x["in_runtime"] for x in t1), len(t2), sum(x["in_runtime"] for x in t2)))
if len(sys.argv) > 3:
    for nm, t in (("t1", t1), ("t2", t2)):
        with open("%s_%s.csv" % (sys.argv[3], nm), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(t[0].keys())); w.writeheader(); w.writerows(t)
