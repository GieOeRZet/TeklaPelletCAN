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
SRC_R = ROOT / "rejestry/odczyty.csv"
DST_R = ROOT / "firmware/components/core/reads_table.cpp"
SRC_E = ROOT / "rejestry/encje.csv"
DST_E = ROOT / "firmware/components/core/entities_table.cpp"
SRC_A = ROOT / "rejestry/alarmy-kody.csv"
DST_A = ROOT / "firmware/components/core/alarm_names_table.cpp"


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


KIND = {"sensor": "Sensor", "binary_sensor": "Binary", "enum": "Enum"}
POLL = {"live": "Live", "l0": "L0", "l1": "L1", "l2": "L2"}


def render_reads():
    rows = list(csv.DictReader(open(SRC_R, encoding="utf-8")))
    ids = [r["id"] for r in rows]
    if len(set(ids)) != len(ids):
        raise SystemExit("zduplikowane id w odczyty.csv")
    out = ["// PLIK WYGENEROWANY przez tools/gen_points.py z rejestry/odczyty.csv – nie edytuj recznie.",
           '#include "reads.h"', "", "namespace tpc {", "", "const ReadPoint kReads[] = {"]
    for r in rows:
        wk = int(r["klucz_zapisu"]) if r["klucz_zapisu"] != "" else -1
        out.append(f'    {{"{esc(r["id"])}", {r["indeks"]}, Decode::{r["dekodowanie"]}, Kind::{KIND[r["rodzaj"]]}, '
                   f'"{esc(r["jednostka"])}", "{esc(r["klasa"])}", "{esc(r["nazwa"])}", "{esc(r["opcje"])}", '
                   f'Tier::{"Basic" if r["poziom_podgladu"] == "basic" else "Full"}, Poll::{POLL[r["odczyt"]]}, {wk}}},')
    out += ["};", "", f"const unsigned kReadCount = {len(rows)};", "", "}  // namespace tpc", ""]
    return "\n".join(out)


def render_entities():
    rows = list(csv.DictReader(open(SRC_E, encoding="utf-8")))
    ids = [r["id"] for r in rows]
    if len(set(ids)) != len(ids):
        raise SystemExit("zduplikowane id w encje.csv")
    out = ["// PLIK WYGENEROWANY przez tools/gen_points.py z rejestry/encje.csv – nie edytuj recznie.",
           '#include "entities.h"', "", "namespace tpc {", "", "const Entity kEntities[] = {"]
    for r in rows:
        out.append(f'    {{"{r["domena"]}", "{esc(r["id"])}", "{esc(r["nazwa"])}", "{esc(r["jednostka"])}", '
                   f'"{esc(r["klasa"])}", "{esc(r["zrodlo"])}"}},')
    out += ["};", "", f"const unsigned kEntityCount = {len(rows)};", "", "}  // namespace tpc", ""]
    return "\n".join(out)


def render_alarms():
    rows = list(csv.reader(open(SRC_A, encoding="utf-8-sig")))[1:]
    out = ["// PLIK WYGENEROWANY przez tools/gen_points.py z rejestry/alarmy-kody.csv – nie edytuj recznie.",
           '#include "alarms.h"', "", "namespace tpc {", "", "const AlarmName kAlarmNames[] = {"]
    for r in rows:
        out.append(f'    {{{int(r[0])}, "{esc(r[2])}"}},')
    out += ["};", "", f"const unsigned kAlarmNameCount = {len(rows)};", "", "}  // namespace tpc", ""]
    return "\n".join(out)


if __name__ == "__main__":
    text, text_r, text_e, text_a = render(), render_reads(), render_entities(), render_alarms()
    if "--check" in sys.argv:
        for path, t in ((DST, text), (DST_R, text_r), (DST_E, text_e), (DST_A, text_a)):
            if not path.exists() or path.read_text(encoding="utf-8") != t:
                raise SystemExit(f"{path.name} nieaktualny – uruchom tools/gen_points.py")
        print("tabele aktualne")
    else:
        DST.write_text(text, encoding="utf-8")
        DST_R.write_text(text_r, encoding="utf-8")
        DST_E.write_text(text_e, encoding="utf-8")
        DST_A.write_text(text_a, encoding="utf-8")
        print(f"zapisano {DST.name}, {DST_R.name}, {DST_E.name}")
