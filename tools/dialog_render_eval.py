#!/usr/bin/env python3
"""PASS 70: render dialogow z DANYCH odczytanych z firmware: dla kazdego dialogu sekwencja rzeczywistych stukniec z menu.state (hak konstrukcji widgetow ctor_trace dodany PRZED uruchomieniem),
tablica widgetow z RAM + ekstrakcja klas/kolorow/tekstow (ui_extras), render rdzeniem ui_render, porownanie ze zrzutem emulatora w tym samym stanie. Wynik: OUT/<nazwa>_{ref,render,diff}.png, widgets.json, RUN_SUMMARY.json.
Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/dialog_render_eval.py FW L0DIR L1DIR L3DIR OUT [dialog ...]"""
import json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, ctor_trace as C, ui_extras as X, ui_render as R
from PIL import Image
import numpy as np
fw, L0, L1, L3, out = sys.argv[1:6]; only = sys.argv[6:]; os.makedirs(out, exist_ok=True)
def row(nav, idx): return lambda s: nav.tap_row_from_top(idx)
SC = {   # nazwa: (katalog, [kroki]) ; krok = ("row", idx) | ("tap", x, y, settle)
 "pin": (L1, [("tap", 450, 20, 900), ("clear",), ("tap", 34, 235, 900), ("row", 12)]),
 "program_day": (L0, [("row", 0), ("tap", 414, 130, 900), ("tap", 235, 175, 900)]),
 "program_copy": (L0, [("row", 0), ("tap", 414, 130, 900), ("tap", 235, 175, 900), ("tap", 235, 200, 900)]),
 "internet_editor": (L1, [("row", 18), ("tap", 180, 62, 900)]),
 "home_paliwo": ("HOME", [("tap", 103, 234, 900)]),
 "home_zasilanie": ("HOME", [("tap", 448, 234, 900)]),
 "home_auto": ("HOME", [("tap", 415, 76, 900)]),
 "home_czas": ("HOME", [("tap", 42, 19, 900)]),
 "home_data": ("HOME", [("tap", 240, 19, 900)]),
 "enum_dialog": (os.environ.get("ESTYMA_LC3", "/tmp/w/LC3"), [("row", 9), ("tap", 400, 245, 900), ("tap", 375, 76, 900)]),
 "enum_radio": (L3, [("row", 11), ("scroll",), ("scroll",), ("scroll",), ("tap", 430, 200, 900)]),
 "enum_text": (L3, [("row", 11), ("scroll",), ("scroll",), ("scroll",), ("tap", 440, 100, 900)]),
 "number_dialog": (L3, [("row", 0), ("tap", 400, 245, 900), ("tap", 375, 76, 900)]),
}
res = {}
for name, (d, steps) in SC.items():
    if only and name not in only: continue
    if d == "HOME":   # swiezy rozruch jak home_inventory.py (konfiguracja: 4 obiegi CO, CWU, bufor, solar)
        s = U.UiSession(fw, None); t = C.Tracer(s); s.boot(500)
        for p_, v_ in {0x2105: 4, 0x2106: 1, 0x2107: 1, 0x2108: 1}.items(): s.set_local(p_, v_)
        s.set_access(0); s.wait(4500); nav = None   # log NIE czyszczony: okna HOME to ukryte kontenery zbudowane przy starcie
    else:
        rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb")); s = U.UiSession.from_checkpoint(fw, os.path.join(d, "menu.state"), None); s.wait(120)
        nav = U.ListNav(s); nav.tall = Image.open(os.path.join(d, "menu_tall.png")); nav.rows = rows; t = C.Tracer(s); t.log.clear()
    for st in steps:
        if st[0] == "clear": t.log.clear(); continue
        if st[0] == "scroll": s.drag_until_change(240, 230, 240, 80, attempts=4, ticks=240, pause_end=160); s.wait(300); continue
        if st[0] == "row": nav.tap_row_from_top(st[1]); s.wait(700)
        else: s.tap(st[1], st[2], settle=st[3]); s.wait(300)
    s.wait(500); ws = C.widget_table(s, t); ex = X.extract(s, ws); ref = s.shot()
    json.dump(dict(widgets=ws, extras=ex), open(os.path.join(out, name + "_data.json"), "w"))
    vis = sorted([(ex[w["this"]]["z"], w) for w in ws if w["this"] in ex and not ex[w["this"]].get("hidden") and "z" in ex[w["this"]]], key=lambda x: x[0]); dim = None
    for i, (z, w) in enumerate(vis[:-1]):                       # korzen okna modalnego: pelnoekranowy widget 'other' tuz przed panelem okna (duzy widget ~440 px szer.)
        nx = vis[i + 1][1]
        if z > 10 and (w["w"], w["h"]) == (480, 272) and ex[w["this"]]["cls"] == "other" and 380 <= nx["w"] <= 470 and nx["h"] >= 200: dim = (180, z); break
    a = R.render(ws, ex, dim=dim); dd = np.abs(np.asarray(a).astype(int) - np.asarray(ref.convert("RGB")).astype(int)).sum(axis=2)
    mae = float(dd.mean() / 3); frac = float((dd > 40).mean())
    a.save(os.path.join(out, name + "_render.png")); ref.save(os.path.join(out, name + "_ref.png")); Image.fromarray(np.clip(dd, 0, 255).astype("uint8")).save(os.path.join(out, name + "_diff.png"))
    res[name] = dict(widgets=len(ws), mae=round(mae, 2), pct_diff=round(frac * 100, 1), view=hex(s.b.rd(s.b.rd(0x20024818)))); print(name, res[name], flush=True)
    json.dump(res, open(os.path.join(out, "RUN_SUMMARY.json"), "w"), indent=1)
