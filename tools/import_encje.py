#!/usr/bin/env python3
"""Import katalogu WSZYSTKICH encji z projektu ESPHome PelletCAN do rejestry/encje.csv.

Uzycie:  python3 tools/import_encje.py <PelletCAN_packages.yaml> [rejestry/encje.csv]

Nazwy (name) sa identyczne jak w ESPHome, wiec entity_id w HA i na stronie urzadzenia = domena.<prefiks>_<slug nazwy>,
a oryginalna karta wykrywa je tak samo jak dotad. Kolumna `zrodlo` wskazuje punkt silnika (rejestry/odczyty.csv);
pusta = encja jeszcze nieprzeniesiona (urzadzenie zwraca dla niej stan "unknown").
"""
import csv, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMS = ["sensor", "binary_sensor", "text_sensor", "select", "switch", "button"]
TEXT_TO_READ = {  # encje tekstowe odpowiadajace enumom silnika
    "burner_state_text": "burner_state", "boiler_mode_text": "boiler_mode", "co_mode_text": "co_mode",
    "co2_mode_text": "co2_mode", "cwu_mode_text": "cwu_mode", "feeder_mode_text": "feeder_mode",
    "blower_mode_text": "blower_mode",
}
MODULE = {  # do jakiego modulu nalezy jeszcze nieprzeniesiona encja
    "alarm": "alarmy", "ah_": "alarmy", "sch_": "harmonogramy", "test_": "test_wyjsc", "conf_txt": "statystyki",
    "stat_txt": "statystyki", "fuel": "paliwo", "tank_pct": "paliwo", "burner_": "palnik", "snap": "diagnostyka",
    "diag": "diagnostyka", "sdo_": "diagnostyka", "fw_ver": "system", "sig_txt": "system", "mixer": "obiegi",
}


def module_of(ident, name, dom):
    for k, v in MODULE.items():
        if ident.startswith(k):
            return v
    if dom == "button":
        return "przyciski"
    if dom in ("select", "switch"):
        return "sterowanie"
    return "inne"


def main():
    src = Path(sys.argv[1]).read_text(encoding="utf-8")
    out = Path(sys.argv[2] if len(sys.argv) > 2 else ROOT / "rejestry/encje.csv")
    reads = {r["id"]: r for r in csv.DictReader(open(ROOT / "rejestry/odczyty.csv", encoding="utf-8"))}

    pos = sorted((src.index("\n" + d + ":\n"), d) for d in DOMS if "\n" + d + ":\n" in src)
    rows = []
    for i, (p, d) in enumerate(pos):
        end = pos[i + 1][0] if i + 1 < len(pos) else len(src)
        for b in re.split(r"\n  - platform: ", src[p:end])[1:]:
            plat = b.split("\n")[0].strip()
            idm, nm = re.search(r"\n    id: (\w+)", b), re.search(r'\n    name: "([^"]*)"', b)
            if not nm or re.search(r"\n    internal: true", b):
                continue
            name = nm.group(1).replace("${'CO1' if dwa_obiegi_co else 'CO'}", "CO")
            if "${" in name:
                raise SystemExit(f"nierozwiazana nazwa: {name}")
            ident = idm.group(1) if idm else re.sub(r"\W+", "_", name.lower()).strip("_")
            un, dc = re.search(r'unit_of_measurement: "([^"]*)"', b), re.search(r"device_class: (\w+)", b)
            z = ident if ident in reads else TEXT_TO_READ.get(ident, "")
            rows.append([d, ident, name, un.group(1) if un else "", dc.group(1) if dc else "", z,
                         "" if z else module_of(ident, name, d)])
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["domena", "id", "nazwa", "jednostka", "klasa", "zrodlo", "modul_do_przeniesienia"])
        w.writerows(rows)
    done = sum(1 for r in rows if r[5])
    print(f"zapisano {len(rows)} encji do {out}; podpietych do silnika: {done}")
    from collections import Counter
    print(Counter(r[6] for r in rows if not r[5]))


if __name__ == "__main__":
    main()
