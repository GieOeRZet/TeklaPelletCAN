#!/usr/bin/env python3
"""NewEstyma PASS 48: klastry SRAM referencjonowane literalami w BIN i ich klasyfikacja.
python3 -I tools/ram_clusters.py FW2213TK_kopia.bin runtime_param_table_655.csv out.csv
Zlicza wystapienia 32-bitowych literalow z zakresu SRAM 0x20000000..0x2003FFFF (wyrownanych do 4 B) i klasyfikuje adres: 'param' (storage rekordu tabeli runtime, w tym wnetrze rekordu wg typu),
'config-gap' (wewnatrz bloku ustawien 0x200208EC..+0x3DD9, ale poza storage'em jakiegokolwiek rekordu = pole niezarejestrowane), 'known-object' (manager 0x20008D84, provider 0x20008D64, sink 0x20008D60, poller 0x2002466C, model 0x20020784, struktura dotyku 0x200247E4), 'other'."""
import collections, csv, struct, sys
raw = open(sys.argv[1], "rb").read(); rt = list(csv.DictReader(open(sys.argv[2])))
sz = {"u8": 1, "u16": 2, "s16": 2, "u32": 4, "u32?": 4}; cover = {}
for r in rt:
    st = int(r["storage"], 16)
    for k in range(sz.get(r["type_name"], 1)): cover[st + k] = r["key"]
KNOWN = {0x20008D84: "manager", 0x20008D64: "provider", 0x20008D60: "sink", 0x2002466C: "poller", 0x20020784: "model", 0x200247E4: "touch-cache", 0x20024860: "currentLanguage", 0x20005EF0: "klasy-menu", 0x20005F08: "access-menu"}
cnt = collections.Counter(struct.unpack_from("<I", raw, o)[0] for o in range(0, len(raw) - 3, 4))
rows = []
for a, n in cnt.items():
    if 0x20000000 <= a < 0x20040000:
        if a in cover: c = "param " + cover[a]
        elif a in KNOWN: c = "known " + KNOWN[a]
        elif 0x200208EC <= a < 0x200208EC + 0x3DDA: c = "config-gap"
        else: c = "other"
        rows.append((a, n, c))
rows.sort(key=lambda x: -x[1])
with open(sys.argv[3], "w", newline="") as f:
    w = csv.writer(f); w.writerow(["addr", "refs", "class"]); [w.writerow(["0x%08X" % a, n, c]) for a, n, c in rows]
print("adresow SRAM z literalami:", len(rows)); print("klasy:", collections.Counter(c.split()[0] for _, _, c in rows))
print("TOP 25 wg liczby literalow:")
for a, n, c in rows[:25]: print("  0x%08X %3d  %s" % (a, n, c))
print("config-gap (pola niezarejestrowane w bloku ustawien), TOP 12:")
for a, n, c in [x for x in rows if x[2] == "config-gap"][:12]: print("  0x%08X (+0x%X) %3d" % (a, a - 0x200208EC, n))
