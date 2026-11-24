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
 "pin": (L1, [("row", 12)]),
 "program_day": (L0, [("row", 0), ("tap", 414, 130, 900), ("tap", 235, 175, 900)]),
 "program_copy": (L0, [("row", 0), ("tap", 414, 130, 900), ("tap", 235, 175, 900), ("tap", 235, 200, 900)]),
 "internet_editor": (L1, [("row", 18), ("tap", 180, 62, 900)]),
 "number_dialog": (L3, [("row", 0), ("tap", 400, 245, 900), ("tap", 375, 76, 900)]),
}
res = {}
for name, (d, steps) in SC.items():
    if only and name not in only: continue
    rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb")); s = U.UiSession.from_checkpoint(fw, os.path.join(d, "menu.state"), None); s.wait(120)
    nav = U.ListNav(s); nav.tall = Image.open(os.path.join(d, "menu_tall.png")); nav.rows = rows; t = C.Tracer(s); t.log.clear()
    for st in steps:
        if st[0] == "row": nav.tap_row_from_top(st[1]); s.wait(700)
        else: s.tap(st[1], st[2], settle=st[3]); s.wait(300)
    s.wait(500); ws = C.widget_table(s, t); ex = X.extract(s, ws); ref = s.shot()
    a = R.render(ws, ex); dd = np.abs(np.asarray(a).astype(int) - np.asarray(ref.convert("RGB")).astype(int)).sum(axis=2)
    mae = float(dd.mean() / 3); frac = float((dd > 40).mean())
    a.save(os.path.join(out, name + "_render.png")); ref.save(os.path.join(out, name + "_ref.png")); Image.fromarray(np.clip(dd, 0, 255).astype("uint8")).save(os.path.join(out, name + "_diff.png"))
    res[name] = dict(widgets=len(ws), mae=round(mae, 2), pct_diff=round(frac * 100, 1), view=hex(s.b.rd(s.b.rd(0x20024818)))); print(name, res[name], flush=True)
    json.dump(res, open(os.path.join(out, "RUN_SUMMARY.json"), "w"), indent=1)
