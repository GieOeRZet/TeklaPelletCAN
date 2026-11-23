#!/usr/bin/env python3
"""NewEstyma PASS 47: pokrycie zasobow firmware (bitmapy, TypedText PL) przez obejrzane ekrany.
python3 -I tools/resource_coverage.py FW2213TK_kopia.bin out.md TRACE_DIR [TRACE_DIR ...]
Wejscie: pliki trace_*.json z ui_explore (ID bitmap i par (jezyk, id tekstu) CZYTANYCH przez firmware przy rysowaniu). Wyjscie: raport MD z lista zasobow NIGDY nieuzytych
na zadnym z obejrzanych ekranow (kandydaci na ukryte ekrany/funkcje, stany i alarmy). Teksty czytane z tabeli PL (RAW 0x5BD80 + 4*ID, UTF-16)."""
import glob, json, os, struct, sys
raw = open(sys.argv[1], "rb").read(); B = 0x08010000
def pl(i):
    p = struct.unpack_from("<I", raw, 0x5BD80 + 4 * i)[0]
    if not (B <= p < B + len(raw)): return ""
    o = p - B; ch = []
    while o + 1 < len(raw):
        c = struct.unpack_from("<H", raw, o)[0]
        if c == 0: break
        ch.append(chr(c)); o += 2
    return "".join(ch).replace("\x02", "").replace("\n", " ")
bm, tx = set(), set(); files = []
for d in sys.argv[3:]:
    for f in glob.glob(os.path.join(d, "trace_*.json")):
        j = json.load(open(f)); bm |= set(j["bitmaps"]); tx |= {i for l, i in j["text"] if l == 0}; files.append(f)
sizes = {}
tsv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "DOKUMENTACJA", "bitmap_sizes.tsv")
if os.path.exists(tsv):
    for line in open(tsv):
        a = line.strip().split("\t")
        if len(a) == 2 and a[0][:3].isdigit(): sizes[int(a[0][:3])] = a[1]
unb = [i for i in range(188) if i not in bm]; unt = [i for i in range(495) if i not in tx and pl(i).strip()]
out = ["# Pokrycie zasobow firmware przez obejrzane ekrany\n", "Zrodlo: %d plikow trace_*.json. Bitmapy uzyte: **%d/188**. Teksty PL (niepuste) uzyte: **%d/%d**.\n" % (len(files), len(bm), len(tx), sum(1 for i in range(495) if pl(i).strip())),
       "\n## Bitmapy NIEUZYTE (%d)\n" % len(unb), "| ID | rozmiar |\n|---|---|"] + ["| %d | %s |" % (i, sizes.get(i, "")) for i in unb]
out += ["\n## Teksty PL NIEUZYTE (%d)\n" % len(unt), "| ID | tekst |\n|---|---|"] + ["| %d | %s |" % (i, pl(i)[:70].replace("|", "/")) for i in unt]
open(sys.argv[2], "w").write("\n".join(out) + "\n"); print("bitmapy %d/188, teksty PL %d uzyte, nieuzyte: bitmapy %d, teksty %d" % (len(bm), len(tx), len(unb), len(unt)))
