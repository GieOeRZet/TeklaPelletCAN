#!/usr/bin/env python3
"""PASS 54: generuje specyfikacje poziomow dostepu 0/1/2 (do wdrozenia) z data/panel_lists_by_level.csv (wynik wykonania FUN 0x0804E714 w emulatorze).
python3 -I tools/spec_levels.py DATA_DIR OUT.md OUT.csv"""
import csv, os, sys, collections
NAMES = {"0x00": "Kocioł", "0x01": "Ogrzewanie obwód 1..4 (instancje)", "0x05": "Ciepła woda użytkowa", "0x06": "Solary", "0x07": "Bufor", "0x08": "Kaskada (gdy 0x350C != 0)", "0x09": "Dodatkowy magazyn paliwa (gdy 0x3525 != 0)", "0x0A": "Palnik", "0x10": "Konfiguracja", "0x11": "Statystyki"}
def main(data, out_md, out_csv):
    rows = [r for r in csv.DictReader(open(os.path.join(data, "panel_lists_by_level.csv"), encoding="utf-8")) if int(r["level"]) <= 2 and r.get("pid")]
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        if r["inst"] not in ("1", ""): continue
        by[r["cls"].upper().replace("0X", "0x")][int(r["level"])].append((r["panel_key"], r["pid"], r["name"]))
    md = ["# SPECYFIKACJA POZIOMOW DOSTEPU 0 / 1 / 2 (NASTAWY ekranow) — generowane z emulacji firmware\n"]
    w = csv.writer(open(out_csv, "w", encoding="utf-8", newline="")); w.writerow(["screen_class", "screen", "level_added", "panel_key", "pid", "name"])
    for cls in sorted(by, key=lambda x: int(x, 16)):
        md.append("\n## %s — %s\n" % (cls, NAMES.get(cls, "")))
        seen = set()
        for lv in (0, 1, 2):
            items = by[cls].get(lv)
            if items is None: md.append("**Poziom %d:** brak danych\n" % lv); continue
            new = [i for i in items if i not in seen]; seen.update(items)
            md.append("**Poziom %d** (razem %d, nowe wzgledem poprzedniego: %d)\n" % (lv, len(items), len(new)))
            if new:
                md.append("| klucz | PID | nazwa |\n|---|---|---|")
                for k, p, n in new: md.append("| %s | %s | %s |" % (k, p, n)); w.writerow([cls, NAMES.get(cls, ""), lv, k, p, n])
                md.append("")
    open(out_md, "w", encoding="utf-8").write("\n".join(md))
if __name__ == "__main__": main(*sys.argv[1:4])
