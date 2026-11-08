#!/usr/bin/env python3
"""Import katalogu odczytow (rejestr -> encja) z projektu ESPHome PelletCAN do rejestry/odczyty.csv.

Uzycie:  python3 tools/import_odczyty.py <PelletCAN_packages.yaml> [rejestry/odczyty.csv]

Czyta: instrukcje `case 0xXXXX: id(nazwa).publish_state(wyrazenie)` z obslugi odpowiedzi SDO,
definicje sensorow (nazwa, jednostka, klasa), liste cyklicznego odczytu (idxs) i listy l0/l1/l2.
Dolacza reczny zestaw punktow tekstowych/binarnych (stany, tryby), ktore w ESPHome sa osobna logika.
Poziom (tier): basic = pomiary i nastawy poziomu 0 (podglad), full = reszta.
"""
import csv, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DECODE = {  # wyrazenie z ESPHome -> kod dekodowania
    "(float) (int16_t) (raw & 0xFFFF)": "S16",
    "(float) (int16_t) (raw & 0xFFFF) / 10.0f": "S16_10",
    "(float) (raw & 0xFF)": "U8",
    "(float) (raw & 0xFF) / 10.0f": "U8_10",
    "(float) (raw & 0xFFFF)": "U16",
    "(float) (raw & 0xFFFF) / 10.0f": "U16_10",
    "(raw & 0xFFFF) / 10.0f": "U16_10",
    "(float) low": "LOW",
    "(float) low / 10.0f": "LOW_10",
    "(float) raw": "RAW",
    "(raw & 1) == 0": "B0_CLEAR",
    "(raw & 1) == 1": "B0_SET",
    "low != 0": "FLAG_LOW",
}
TEMP_DIV1 = {0x2003, 0x2004, 0x2010, 0x2012, 0x201A, 0x22AD, 0x22AE}  # zadane: pelne stopnie
BINARY = {"B0_CLEAR", "B0_SET", "FLAG_LOW"}

BASIC_IDS = {
    "boiler_temp", "boiler_set_manual", "boiler_set_result", "ch1_temp", "ch1_set_manual", "ch1_set_result",
    "ch1_pump", "ch2_temp", "ch2_set_manual", "ch2_set_result", "ch2_pump", "hw_temp", "hw_set_comfort",
    "hw_set_eco", "hw_set_result", "hw_pump", "co_set_comfort", "co_set_eco", "outside_temp", "ret_temp",
    "burner_temp", "tank_cap", "tank_kg", "burner_state", "boiler_mode", "co_mode", "co2_mode", "cwu_mode",
    "boiler_on",
}

# Punkty bez "case ... publish_state" w ESPHome (osobna logika): enumeracje i stany.
BURNER = "0:Wylaczony,1:Rozpalanie,2:Zarzenie,5:Modulacja,6:Wygaszanie / czyszczenie,7:Czyszczenie,8:Pauza,9:Stop,10:Alarm"
BMODE = "0:Czasowy auto,1:Czasowy reczny,2:Auto,3:Reczny"
CMODE = "0:Off,1:Eko,2:Harmonogram,3:Komfort"
OUTM = "0:Automat,1:Wylaczony,2:Wlaczony"
EXTRA = [
    # id, indeks, decode, kind, jednostka, klasa, nazwa, opcje
    ("burner_state", 0x2007, "LOW", "enum", "", "", "Palnik stan", BURNER),
    ("boiler_mode", 0x2002, "RAW", "enum", "", "", "Kociol tryb pracy", BMODE),
    ("co_mode", 0x2064, "LOW", "enum", "", "", "CO tryb", CMODE),
    ("co2_mode", 0x2065, "LOW", "enum", "", "", "CO2 tryb", CMODE),
    ("cwu_mode", 0x2014, "LOW", "enum", "", "", "CWU tryb", CMODE),
    ("feeder_mode", 0x2259, "LOW", "enum", "", "", "Podajnik tryb", OUTM),
    ("blower_mode", 0x2283, "LOW", "enum", "", "", "Dmuchawa tryb", OUTM),
    ("boiler_on", 0x2005, "FLAG_LOW", "binary_sensor", "", "running", "Kociol wlaczony", ""),
    ("tank_cap", 0x3600, "U16", "sensor", "kg", "weight", "Zbiornik pojemnosc", ""),
    ("tank_kg", 0x3601, "U16", "sensor", "kg", "weight", "Zbiornik paliwo", ""),
]
PK_DECODE = {"Plain": "U16", "FlagByte": "LOW", "Tenths": "U16_10", "FlagTenths": "LOW_10",
             "PlainS16": "S16", "TenthsS16": "S16_10"}


def arr(text, name):
    m = re.search(rf"static const uint16_t {name}\[\] = \{{([^}}]*)\}}", text)
    return {int(x, 16) for x in re.findall(r"0x[0-9A-Fa-f]+", m.group(1))} if m else set()


def main():
    src = Path(sys.argv[1]).read_text(encoding="utf-8")
    out = Path(sys.argv[2] if len(sys.argv) > 2 else ROOT / "rejestry/odczyty.csv")

    start = src.index("switch (idx) {\n                case 0x2001")
    sw = src[start:start + 16000]
    cases = re.findall(r"case (0x[0-9A-Fa-f]{4}): id\((\w+)\)\.publish_state\(([^;]*)\);", sw)

    defs = {}
    sec = src[src.index("\nsensor:"):]
    for b in re.split(r"\n  - platform: ", sec):
        i, n = re.search(r"\n    id: (\w+)", b), re.search(r'\n    name: "([^"]*)"', b)
        if i and n:
            u, d = re.search(r'unit_of_measurement: "([^"]*)"', b), re.search(r"device_class: (\w+)", b)
            defs[i.group(1)] = (n.group(1), u.group(1) if u else "", d.group(1) if d else "")
    bsec = src[src.index("\nbinary_sensor:"):src.index("\ntext_sensor:")]
    for b in re.split(r"\n  - platform: ", bsec):
        i, n = re.search(r"\n    id: (\w+)", b), re.search(r'\n    name: "([^"]*)"', b)
        if i and n:
            d = re.search(r"device_class: (\w+)", b)
            defs[i.group(1)] = (n.group(1), "", d.group(1) if d else "")

    idxs = arr(src[src.index("static const uint16_t idxs[]"):], "idxs")
    blk = src[src.index("static const uint16_t l0[]"):]
    l0, l1, l2 = arr(blk, "l0"), arr(blk, "l1"), arr(blk, "l2")

    pk, pk_rows = {}, []
    with open(ROOT / "rejestry/punkty.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            pk[int(r["indeks"], 16)] = (int(r["klucz"]), int(r["poziom"]))
            pk_rows.append(r)

    def name_of(raw):
        return raw.replace("${'CO1' if dwa_obiegi_co else 'CO'}", "CO")

    rows, seen = [], set()
    for idx_s, ident, expr in cases:
        idx = int(idx_s, 16)
        if expr.strip() == "t":
            dec = "S16" if idx in TEMP_DIV1 else "S16_10"
        else:
            dec = DECODE.get(expr.strip())
            if dec is None:
                raise SystemExit(f"nieznane wyrazenie: {expr} dla {ident}")
        name, unit, cls = defs[ident]
        kind = "binary_sensor" if dec in BINARY else "sensor"
        rows.append([ident, idx, dec, kind, unit, cls, name_of(name), ""])
        seen.add(idx)
    for e in EXTRA:
        if e[1] in seen:
            continue
        rows.append([e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7]])
        seen.add(e[1])

    # Nastawy z punkty.csv bez odczytu w ESPHome: dodaj ogolny odczyt zgodny z kodowaniem zapisu.
    for r in pk_rows:
        idx = int(r["indeks"], 16)
        if idx in seen:
            continue
        name = r["nazwa"] or f"Parametr 0x{idx:04X} (nieopisany)"
        rows.append([f"param_{r['klucz']}", idx, PK_DECODE[
            "PlainS16" if r["kodowanie"] == "Plain" and r["ze_znakiem"] == "1" else
            "TenthsS16" if r["kodowanie"] == "Tenths" and r["ze_znakiem"] == "1" else r["kodowanie"]],
            "sensor", "", "", name, ""])
        seen.add(idx)

    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "indeks", "dekodowanie", "rodzaj", "jednostka", "klasa", "nazwa", "opcje",
                    "poziom_podgladu", "odczyt", "klucz_zapisu", "poziom_zapisu"])
        for ident, idx, dec, kind, unit, cls, name, opts in rows:
            key, lvl = pk.get(idx, ("", ""))
            tier = "basic" if (ident in BASIC_IDS or lvl == 0) else "full"
            poll = "live" if idx in idxs else "l0" if idx in l0 else "l2" if idx in l2 else "l1"
            w.writerow([ident, f"0x{idx:04X}", dec, kind, unit, cls, name, opts, tier, poll, key, lvl])
    print(f"zapisano {len(rows)} odczytow do {out}")


if __name__ == "__main__":
    main()
