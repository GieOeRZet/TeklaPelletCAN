#!/usr/bin/env python3
"""PASS 65: szkielet drzewa menu (ui_model/menu_tree.json) ze zgromadzonych danych. Nic nie jest zgadywane bez oznaczenia:
evidence = MEASURED (emulator, krawedz/vtable), STRONG (spojne z kilku zrodel), DOC (opis z raportow PASS), OPEN (brak dowodu)."""
import csv, json, os, collections
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analiza", "FW2213TK-2026-11-22", "data")
OUT = os.path.join(D, "ui_model"); os.makedirs(OUT, exist_ok=True)
vt = json.load(open(os.path.join(D, "pass63_view_classes.json")))
act = json.load(open(os.path.join(D, "actions_pass61_L0_partial.json")))
# --- wezly (klasy ekranow po vtable) ---
V = {"0x808f708": "HOME", "0x808f66c": "MENU", "0x808f910": "PROGRAM", "0x808f944": "LISTA",
     "0x808ed7c": "KOCIOL", "0x808ede4": "PALNIK", "0x808f5d0": "OGRZEWANIE", "0x808f604": "CWU", "0x808f978": "SOLARY",
     "0x808edb0": "BUFOR", "0x808ec10": "ALARMY", "0x808f638": "INFO", "0x808f80c": "TEST_WYJSC", "0x808f770": "SIEC", "0x808f9ac": "INTERNET"}
EV = {"HOME": "MEASURED (ikona domu -> vtable)", "MENU": "MEASURED (PASS 40 vptr + krawedz '<')", "PROGRAM": "MEASURED (pasek programu na Kociol/Ogrzewanie)", "LISTA": "MEASURED (zebatka; wszystkie NASTAWY + Konfiguracja + Statystyki)"}
nodes = {}
def node(i, title, vptr=None, kind="screen", level_min=0, evidence="", note=""):
    nodes[i] = dict(id=i, title_pl=title, vtable=vptr, kind=kind, level_min=level_min, evidence=evidence or EV.get(i, "MEASURED (vtable w pass63_view_classes.json)"), note=note)
node("HOME", "Ekran glowny", "0x808f708", evidence="STRONG (vtable po ikonie domu + tytul dnia tygodnia na ekranie)", note="kafelki: MENU, Paliwo, plomien (klodka 0x2006), Ogrzewanie 1/2, Woda, zasilanie, AUTO; wiazania widgetow NIE zmierzone (OPEN)")
node("MENU", "MENU", "0x808f66c")
node("KOCIOL", "Kociol", "0x808ed7c"); node("PALNIK", "Palnik", "0x808ede4")
node("OGRZEWANIE", "Ogrzewanie obwod 1..4 (jedna klasa, instancje)", "0x808f5d0", note="PID = baza + instancja - 1 (zmierzone CO1 vs CO2)")
node("CWU", "Ciepla woda uzytkowa", "0x808f604"); node("SOLARY", "Solary", "0x808f978"); node("BUFOR", "Bufor", "0x808edb0")
node("ALARMY", "Historia alarmow", "0x808ec10", note="dane z rejestrow alarmow, nie z PID-ow GUI (PID-diff nie dotyczy)")
node("INFO", "Informacje o programie", "0x808f638", note="teksty statyczne")
node("TEST_WYJSC", "Test wyjsc", "0x808f80c", level_min=1); node("SIEC", "Siec", "0x808f770", level_min=1); node("INTERNET", "Internet", "0x808f9ac", level_min=1)
node("PROGRAM", "PROGRAM (harmonogram tygodniowy)", "0x808f910", note="widgety/wiazania PROGRAM NIE zmierzone (OPEN)")
node("LISTA", "Lista parametrow (NASTAWY / Konfiguracja / Statystyki)", "0x808f944", note="jedna klasa; tresc = klasa runtime x poziom -> panel_lists_by_level.csv")
node("KASKADA", "Kaskada", None, evidence="DOC (PASS 46: klasa runtime 8, warunek 0x350C != 0); nie wyrenderowana", note="OPEN: vtable, widgety, wiazania")
node("MAGAZYN", "Dodatkowy magazyn paliwa", None, evidence="DOC (PASS 46: klasa runtime 9, warunek 0x3525 != 0); nie wyrenderowany", note="OPEN: vtable, widgety, wiazania")
node("KONFIGURACJA", "Konfiguracja (lista klasy 0x10)", "0x808f944", evidence="MEASURED (LISTA z ctx 0x10)", note="zmienia widocznosc menu 0x2105..0x2108 od poziomu 1")
node("STATYSTYKI", "Statystyki (lista klasy 0x11)", "0x808f944", level_min=1, evidence="STRONG (PASS 46: klasa 0x11, 13 pozycji; ctx 0x11)")
for i, t, src in (("DLG_PIN", "Dialog PIN (4 cyfry, +/-, OK)", "DOC PASS 93/105"), ("DLG_PALIWO", "Dialog Paliwo (+/-, kg, czas, OK)", "DOC PASS 93/105"),
                  ("DLG_CZAS", "Dialog Ustaw czas (z zegara na ekranie glownym)", "DOC PASS 92/105"), ("DLG_EDYCJA", "Dialog edycji wartosci (suwak min-max, -/+, OK; zapis CAN 0x584)", "DOC PASS 93/105"),
                  ("DLG_ZASILANIE", "Okno trybow zasilania (z kafla zasilania)", "DOC PASS 50"), ("DLG_AUTO", "Okno AUTO (temperatury komfort/eco, suwaki)", "DOC MENU-TREE")):
    node(i, t, None, kind="dialog", evidence=src, note="OPEN: vtable, widgety, wiazania, ramka TX")
# --- wiersze menu (21) ---
rows = list(csv.DictReader(open(os.path.join(D, "menu_rows_21.csv")))); eff = {int(r["row"]): r for r in csv.DictReader(open(os.path.join(D, "menu_click_effects_21.csv")))}
NAMES = [("Kociol", "KOCIOL", None), ("Palnik", "PALNIK", None), ("Ogrzewanie 1", "OGRZEWANIE", [("0x2105", ">=", 1)]), ("Ogrzewanie 2", "OGRZEWANIE", [("0x2105", ">=", 2)]),
         ("Ogrzewanie 3", "OGRZEWANIE", [("0x2105", ">=", 3)]), ("Ogrzewanie 4", "OGRZEWANIE", [("0x2105", ">=", 4)]), ("Ciepla woda", "CWU", [("0x2106", "!=", 0)]),
         ("Solary", "SOLARY", [("0x2108", "!=", 0)]), ("Bufor", "BUFOR", [("0x2107", "!=", 0)]), ("Kaskada", "KASKADA", [("0x350C", "!=", 0)]),
         ("Dodatkowy magazyn paliwa", "MAGAZYN", [("0x3525", "!=", 0)]), ("Historia alarmow", "ALARMY", None), ("Informacje o programie", "INFO", None),
         ("Konfiguracja", "KONFIGURACJA", None), ("Poziom menu (PIN)", "DLG_PIN", None), ("Jezyk (Language)", None, None), ("Alarm dzwiekowy (przelacznik)", None, None),
         ("Test wyjsc", "TEST_WYJSC", None), ("Statystyki", "STATYSTYKI", None), ("Siec", "SIEC", None), ("Internet", "INTERNET", None)]
SW = json.load(open(os.path.join(OUT, "menu_sweep.json"))) if os.path.exists(os.path.join(OUT, "menu_sweep.json")) else {}
menu_rows = []
for r in rows:
    i = int(r["row"]); n, tgt, cond = NAMES[i]; e = eff.get(i, {})
    menu_rows.append(dict(row=i, title_pl=n, target=tgt, runtime_class=int(e.get("class", -1)), icon_bitmaps=[int(r["bitmap_A"]), int(r["bitmap_B"])],
                          level_min=0 if r["built_at_access"] == "0" else 1, config_cond=[dict(pid=p, op=o, val=v) for p, o, v in (cond or [])],
                          embedded_control=("language_cycle (PID 0x0003, 8 jezykow)" if i == 15 else "switch PID 0x3506" if i == 16 else "PIN dialog" if i == 14 else None),
                          visible_in=[k for k, v in SW.items() if i in v["rows_visible"]] if SW else None,
                          evidence="MEASURED (menu_sweep: wiersz widoczny gdy dodany do kontenera, 33 warianty konfiguracji x poziomy; ikona A=%d)" % int(r["bitmap_A"]) if SW else "STRONG (menu_rows_21 + PASS 40/41/46)"))
# --- krawedzie zmierzone (action_probe, poziom 0, wezly 0..5): tap w srodek widgetu dotykowego ---
KNOWN = {(65, 22): "przycisk powrotu < (naglowek, widget 130x45)", (91, 20): "napis < MENU (naglowek)", (479, 25): "ikona domu (prawy gorny rog)",
         (359, 249): "kafel zebatki (NASTAWY)", (414, 130): "pasek programu (PROGRAM)"}
E = []; seen = set()
for a in act:
    if a["effect"] != "SCREEN": continue
    f, t_ = a["effects"]["from_vptr"], a["effects"]["view_vptr"]; fn, tn = V.get(f, f), V.get(t_, t_)
    if fn == "LISTA" and tn != "HOME": tn = "ORIGIN"            # z listy powrot prowadzi do ekranu, z ktorego ja otwarto (klasa tego samego wezla inwentarza)
    key = (fn, a["x"], a["y"], tn)
    if key in seen: continue
    seen.add(key)
    E.append({"from": fn, "to": tn, "tap": [a["x"], a["y"]], "widget_size": [a["w"], a["h"]], "label": KNOWN.get((a["x"], a["y"]), "dotyk widgetu (niezidentyfikowany)"), "level_min": 0, "effect": "nav",
              "evidence": "MEASURED (action_probe PASS 61, poziom 0, wezly 0..5; klasa docelowa po vtable)"})
for a, b, lab, ev in (("HOME", "MENU", "kafel MENU (34,235)", "MEASURED (ui_explore: tap 34,235)"), ("HOME", "DLG_PALIWO", "kafel Paliwo", "DOC PASS 42/50"), ("HOME", "OGRZEWANIE", "kafel Ogrzewanie 1/2", "DOC"), ("HOME", "CWU", "kafel Woda", "DOC"),
                      ("HOME", "DLG_ZASILANIE", "kafel zasilania", "DOC PASS 50"), ("HOME", "DLG_AUTO", "kafel AUTO", "DOC"), ("HOME", "DLG_CZAS", "zegar", "DOC PASS 92"), ("LISTA", "DLG_EDYCJA", "wiersz liczbowy", "DOC PASS 93/105"),
                      ("MENU", "DLG_PIN", "wiersz Poziom menu", "STRONG (wiersz 14, klasa 15)")):
    E.append(dict(**{"from": a, "to": b}, tap=None, label=lab, level_min=0, effect="dialog" if b.startswith("DLG") else "nav", evidence=ev))
for m in menu_rows:
    if m["target"]: E.append(dict(**{"from": "MENU", "to": m["target"]}, tap=None, label="wiersz %d: %s" % (m["row"], m["title_pl"]), level_min=m["level_min"], config_cond=m["config_cond"], effect="nav", evidence=m["evidence"]))
# --- listy wg poziomu ---
pl = list(csv.DictReader(open(os.path.join(D, "panel_lists_by_level.csv")))); cnt = collections.OrderedDict()
for r in pl:
    if r["inst"] in ("1", "") : cnt.setdefault(r["cls"], {})[r["level"]] = int(r["list_len"] or 0)
lists = {c: dict(counts_by_level=v, source="panel_lists_by_level.csv (FUN_0803E714 wykonana w emulatorze, PASS 46)", evidence="MEASURED") for c, v in cnt.items()}
open_items = ["HOME: wiazania widgetow, okna (Paliwo, zasilanie, AUTO) - vtable/widgety nie zmierzone", "PROGRAM: widgety i wiazania (harmonogram 7 dni x 24 h)", "Kaskada, Dodatkowy magazyn paliwa: odslonic konfiguracja 0x350C/0x3525, zmierzyc",
              "Poziomy 1 i 3: inwentarz widgetow ekranow (mamy L0 i L2); menu: L1=L2=L3 (zmierzone); poziom 3 = CPU% w naglowku + 6 wrapperow", "Graf akcji: tylko 6 z 24 wezlow L0 (232 stukniecia); brak pozostalych klas i klas poza menu",
              "Dialogi: vtable, widgety, wiazania, ramki TX (PIN, Paliwo, czas, edycja, zasilanie, AUTO, potwierdzenia, bledy)", "Wiersze 15/16 (Jezyk, Alarm dzwiekowy): kontrolki wbudowane w wiersz (nie ekran)", "Alarmy: warunki per alarm, prezentacja, ACK", "Wykresy/Statystyki: widoki i dane"]
tree = dict(meta=dict(title="Drzewo menu igneoTouch FW2213TK (szkielet)", generated_by="tools/menu_tree_build.py (PASS 65)", firmware_sha256="1d679d6810cfb44a4c1d862d67552b7220f3edeb3a2807f3067d46185d0c5071",
                      evidence_legend="MEASURED=zmierzone w emulatorze; STRONG=spojne z wielu zrodel; DOC=z raportow, nie zmierzone tu; OPEN=brak dowodu", levels="0..3 (PIN 900->1, 999->2, 6154->3)"),
            nodes=list(nodes.values()), menu_rows=menu_rows, edges=E, lists_by_level=lists, open=open_items)
json.dump(tree, open(os.path.join(OUT, "menu_tree.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
md = ["# Drzewo menu (szkielet, PASS 65)\n", "Legenda dowodow: MEASURED / STRONG / DOC / OPEN. Pelne dane: `menu_tree.json`.\n", "## HOME\n- HOME -> MENU (kafel MENU), kafle: Paliwo, plomien, Ogrzewanie 1/2, Woda, zasilanie, AUTO, zegar (DOC; wiazania OPEN)\n", "## MENU (21 wierszy)\n", "| # | wiersz | cel | klasa runtime | poziom min | warunek konfiguracji | dowod |", "|---|---|---|---|---|---|---|"]
for m in menu_rows: md.append("| %d | %s | %s | %d | %d | %s | %s |" % (m["row"], m["title_pl"], m["target"] or "(kontrolka w wierszu)", m["runtime_class"], m["level_min"], ", ".join("%s %s %s" % (c["pid"], c["op"], c["val"]) for c in m["config_cond"]) or "-", m["evidence"].split(" (")[0]))
md += ["", "## Krawedzie zmierzone (poziom 0)\n", "| z | dotyk | cel | opis |", "|---|---|---|---|"] + ["| %s | %s | %s | %s |" % (e["from"], e["tap"], e["to"], e["label"]) for e in E if e["evidence"].startswith("MEASURED")]
md += ["", "## Listy NASTAWY: liczba pozycji wg poziomu 0/1/2/3\n"] + ["- klasa %s: %s" % (c, v["counts_by_level"]) for c, v in lists.items()] + ["", "## OPEN\n"] + ["- " + o for o in open_items]
open(os.path.join(OUT, "menu_tree.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
print(len(nodes), "wezlow", len(menu_rows), "wierszy menu", len(E), "krawedzi")
