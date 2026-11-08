#!/usr/bin/env python3
"""Generuje firmware/components/core/points_table.cpp z rejestry/punkty.csv.

Uzycie:  python3 tools/gen_points.py          # zapisuje plik
         python3 tools/gen_points.py --check  # tylko sprawdza, czy plik jest aktualny (CI)
"""
import csv, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "rejestry/punkty.csv"
DST = ROOT / "firmware/components/core/points_table.cpp"


def enc_name(kodowanie, signed):
    if signed:
        if kodowanie == "Plain": return "PlainS16"
        if kodowanie == "Tenths": return "TenthsS16"
        raise SystemExit(f"kodowanie ze znakiem nieobslugiwane: {kodowanie}")
    return kodowanie


def flt(x):
    t = repr(float(x))          # zawsze z kropka: 30.0, -10.0, 2.5
    return t + "f"


def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def render():
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    keys = [int(r["klucz"]) for r in rows]
    if len(set(keys)) != len(keys):
        raise SystemExit("zduplikowane klucze w punkty.csv")
    out = ["// PLIK WYGENEROWANY przez tools/gen_points.py z rejestry/punkty.csv – nie edytuj recznie.",
           '#include "point.h"', "", "namespace tpc {", "", "const Point kPoints[] = {"]
    for r in rows:
        mn, mx = float(r["min"]), float(r["max"])
        out.append(f'    {{{int(r["klucz"])}, {r["indeks"]}, Encoding::{enc_name(r["kodowanie"], r["ze_znakiem"] == "1")}, '
                   f'{flt(mn)}, {flt(mx)}, {int(r["poziom"])}, "{esc(r["nazwa"])}"}},')
    out += ["};", "", f"const unsigned kPointCount = {len(rows)};", "", "}  // namespace tpc", ""]
    return "\n".join(out)


if __name__ == "__main__":
    text = render()
    if "--check" in sys.argv:
        if not DST.exists() or DST.read_text(encoding="utf-8") != text:
            raise SystemExit("points_table.cpp nieaktualny – uruchom tools/gen_points.py")
        print("points_table.cpp aktualny")
    else:
        DST.write_text(text, encoding="utf-8")
        print(f"zapisano {DST}")
