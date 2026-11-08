#!/usr/bin/env python3
"""Import tablicy nastaw (akcja set_param) z projektu ESPHome PelletCAN do rejestry/punkty.csv.

Uzycie:  python3 tools/import_pelletcan.py <PelletCAN_packages.yaml> [rejestry/punkty.csv]

Czyta rownolegle tablice ix/lo/hi/lv z akcji `set_param` oraz odtwarza kodowanie z lancucha
if/else (te same warunki i kolejnosc), a nazwy bierze z rejestry/katalog-rejestrow.csv.
Po dodaniu nowej nastawy w ESPHome wystarczy uruchomic skrypt ponownie i obejrzec roznice (git diff).
"""
import csv, re, sys
from pathlib import Path


def arr(block, name, ctype):
    m = re.search(rf"static const {ctype} {name}\[\] = \{{([^}}]*)\}}", block)
    if not m:
        raise SystemExit(f"nie znaleziono tablicy {name}")
    return [x.strip() for x in m.group(1).split(",") if x.strip()]


def num(s):
    s = s.rstrip("fF")
    return int(s, 16) if s.lower().startswith("0x") else float(s)


def encoding(k):
    """Odtworzenie lancucha warunkow z set_param (kolejnosc ma znaczenie)."""
    if k <= 1: return "FlagByte", False
    if k == 2: return "FlagTenths", False
    if k == 3: return "Plain", True
    if k == 4: return "Tenths", False
    if k == 12: return "FlagTenths", False
    if k == 13: return "Tenths", True
    if k in (14, 20, 21) or 15 <= k <= 18 or 44 <= k <= 46: return "FlagByte", False
    if k in (22, 35, 41, 42, 43): return "Plain", False
    if k in (23, 40): return "Tenths", False
    if k in (32, 33): return "FlagTenths", False
    if 24 <= k <= 39: return "FlagByte", False
    if 51 <= k <= 57 or 59 <= k <= 64: return "FlagByte", False
    if k in (66, 67) or 73 <= k <= 75: return "FlagByte", False
    return "Plain", False


def main():
    src = Path(sys.argv[1]).read_text(encoding="utf-8")
    out = Path(sys.argv[2] if len(sys.argv) > 2 else Path(__file__).parent.parent / "rejestry/punkty.csv")
    start = src.index("action: set_param")
    block = src[start:start + 12000]
    ix, lo, hi, lv = (arr(block, n, t) for n, t in
                      (("ix", "uint16_t"), ("lo", "float"), ("hi", "float"), ("lv", "uint8_t")))
    n = len(ix)
    if not (len(lo) == len(hi) == len(lv) == n):
        raise SystemExit(f"rozne dlugosci tablic: {n} {len(lo)} {len(hi)} {len(lv)}")

    names = {}
    cat = Path(__file__).parent.parent / "rejestry/katalog-rejestrow.csv"
    with open(cat, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["wezel"] == "4" and r["sub"] == "1":
                names[int(r["index"], 16)] = r["nazwa"]

    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["klucz", "indeks", "nazwa", "kodowanie", "ze_znakiem", "min", "max", "poziom"])
        for k in range(n):
            e, signed = encoding(k)
            idx = num(ix[k])
            w.writerow([k, f"0x{idx:04X}", names.get(idx, ""), e, int(signed),
                        num(lo[k]), num(hi[k]), int(num(lv[k]))])
    print(f"zapisano {n} nastaw do {out}")


if __name__ == "__main__":
    main()
