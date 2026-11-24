#!/usr/bin/env python3
"""PASS 66: ogolny model list NASTAWY / Konfiguracja / Statystyki (ui_model/lists.json) z panel_lists_by_level.csv + pid_matrix_655.csv.
Wiersz listy = jeden schemat: kind (number|switch|enum), PID, nazwa, typ, zakres surowy, domyslna, jednostka (wskazowka z nazwy EN; w UI jednostka jest czescia etykiety), poziom_min.
kind jest WYWNIOSKOWANY z zakresu (INFERENCE) i potwierdzony w emulatorze na przykladach (dialog liczbowy z suwakiem, dialog wyboru radio, edytor tekstu)."""
import csv, json, os, re, collections
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analiza_archiwum", "FW2213TK-2026-11-22", "data")
pm = {r["pid"]: r for r in csv.DictReader(open(os.path.join(D, "pid_matrix_655.csv")))}
rows = [r for r in csv.DictReader(open(os.path.join(D, "panel_lists_by_level.csv"))) if r["pid"] or r["panel_key"]]
CLS = {"0x00": "KOCIOL", "0x01": "OGRZEWANIE", "0x02": "OGRZEWANIE", "0x03": "OGRZEWANIE", "0x04": "OGRZEWANIE", "0x05": "CWU", "0x06": "SOLARY", "0x07": "BUFOR", "0x08": "KASKADA", "0x09": "MAGAZYN", "0x0A": "PALNIK", "0x10": "KONFIGURACJA", "0x11": "STATYSTYKI"}
lists = collections.OrderedDict(); first_level = {}
for r in rows:
    key = (r["cls"], r["inst"]); lv = int(r["level"]); k2 = (r["cls"], r["inst"], r["panel_key"], r["pid"])
    first_level[k2] = min(first_level.get(k2, 9), lv)
for r in rows:
    if int(r["level"]) != 3: continue                           # kolejnosc i zestaw wg najwyzszego poziomu (3); poziom_min z first_level
    m = pm.get(r["pid"]); cls = r["cls"]; inst = r["inst"]
    e = dict(idx=int(r["idx"]), panel_key=r["panel_key"], pid=r["pid"] or None, name_en=r["name"], level_min=first_level[(cls, inst, r["panel_key"], r["pid"])])
    if m:
        lo, hi = int(m["min"]), int(m["max"]); u = re.findall(r"\[([^\]]+)\]", m["name"])
        e.update(type=m["type"], raw_min=lo, raw_max=hi, raw_default=int(m["default"]), mode=m["mode"], unit_hint=u[-1] if u else None,
                 kind="switch" if (lo, hi) == (0, 1) else "enum" if hi - lo <= 8 else "number", kind_evidence="INFERENCE z zakresu; dialog liczbowy/radio/edytor tekstu zmierzone w emulatorze")
    else:
        e.update(kind="chart_or_special", kind_evidence="OPEN: klucz bez PID (np. 0x47/0x48 wykresy)")
    lists.setdefault("%s|%s|inst%s" % (cls, CLS.get(cls, "?"), inst), []).append(e)
kinds = collections.Counter(x["kind"] for v in lists.values() for x in v)
out = dict(meta=dict(title="Modele list parametrow (NASTAWY/Konfiguracja/Statystyki)", generated_by="tools/lists_build.py (PASS 66)",
        one_schema=["wiersz: etykieta (TypedText, zawiera jednostke) + wartosc po prawej + (kind=switch: przelacznik on/off | kind=enum: tekst wartosci | kind=number: wartosc liczbowa)",
                    "separator grupy: ikona klucza + cyfra poziomu (poziom_min dla wierszy pod nim)", "dialogi: number = tytul (etykieta z jednostka), duza wartosc, min/max, suwak, -/+, OK; enum = lista radio + OK; tekst (np. Nazwa) = edytor znakow (ABC/abc/123.0/?!&) + OK"],
        differences_between_rows=["jednostka (czesc etykiety)", "skala dziesietna (np. 0.5 przy surowej 5; zmierzone: Room temp hysteresis surowa 0-50 -> dialog 0-5)", "zakres min/max", "krok (suwak -/+) - OPEN: nie zmierzony per wiersz"],
        kinds_total=dict(kinds), measured_examples=dict(kociol_liczbowe=["Temperatura zadana [°C] 60..80 = 65", "Histereza zalaczenia [°C] 0..20 = 10", "Histereza wylaczenia [°C] 0..20 = 0"],
            ogrzewanie_liczbowe=["Temperatura komfortowa [°C] 15..30 = 21.0", "Temperatura ekonomiczna [°C] 10..30 = 18.0", "Histereza [°C] 0..5 = 0.5"], enum=["Tryb pracy: reczny/pogodowy (dialog radio + OK)", "Czujnik pokojowy: brak/..."],
            tekst=["Nazwa (edytor znakow z klawiatura ABC/abc/123.0/?!&)"], przelacznik="Automatyczny tryb lato, Czujnik CO, Stala pompa (suwak on/off); stukniecie w test NIE zmienilo PID - OPEN"),
        open=["skala/format/krok per wiersz (zmierzyc dialogi lub z kodu: C4 u ChatGPT)", "etykiety PL/EN wierszy (TypedText) per wiersz", "zachowanie przelacznika (stukniecie: gdzie, jaka ramka CAN)", "zapis z dialogu edycji (ramka 0x584 przy OK) - nie zmierzony dla list"]), lists=lists)
os.makedirs(os.path.join(D, "ui_model"), exist_ok=True)
json.dump(out, open(os.path.join(D, "ui_model", "lists.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print({k: len(v) for k, v in lists.items()}, dict(kinds))
