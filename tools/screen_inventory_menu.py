#!/usr/bin/env python3
"""PASS 57: inwentarz widgetow ekranow osiagalnych z MENU: dla kazdego wiersza listy menu (rows.pkl) wchodzi (ze sledzeniem konstrukcji), zapisuje widgety ekranu,
potem kafel ustawien (400,245) i zapisuje widgety NASTAW; opcjonalnie kafel (344,245)/PROGRAM. python3 -I tools/screen_inventory_menu.py FW.bin DIR OUT.json [rows...]"""
import os, sys, json, pickle, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, ctor_trace as C
from PIL import Image
fw, d, out = sys.argv[1:4]; sel = [int(x) for x in sys.argv[4:]]
raw = open(fw, "rb").read(); B = 0x08010000
DB = [(raw[0x8071958 - B + 2 * i], raw[0x8071958 - B + 2 * i + 1]) for i in range(496)]
def pl(i):
    try:
        p = struct.unpack_from("<I", raw, 0x5BD80 + 4 * i)[0]; o = p - B; r = []
        while True:
            c = struct.unpack_from("<H", raw, o)[0]
            if c == 0: break
            r.append(chr(c)); o += 2
        return "".join(r)
    except Exception: return "?"
rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb"))
s = U.UiSession.from_checkpoint(fw, os.path.join(d, "menu.state"), None); s.wait(120)
nav = U.ListNav(s); nav.tall = Image.open(os.path.join(d, "menu_tall.png")); nav.rows = rows
t = C.Tracer(s); res = []
def grab(label, idx, action):
    t.log.clear(); action(); s.wait(700); ws = C.widget_table(s, t)
    for w in ws:
        if w["text_id"] is not None:
            w["text_pl"] = pl(w["text_id"] + 57); w["font"], w["align"] = DB[w["text_id"]] if w["text_id"] < 496 else (None, None)
    title = next((w["wildcard"] or w["text_pl"] for w in sorted(ws, key=lambda w: w["ay"]) if w["role"] == "text" and 0 <= w["ay"] < 46 and w["w"] >= 300 and (w["wildcard"] or w.get("text_pl"))), "")
    res.append(dict(node="%s_%s" % (idx, label), parent=idx, tap=label, title=title, widgets=ws)); print(idx, label, repr(title), len(ws), flush=True)
    json.dump(res, open(out, "w"), ensure_ascii=False)
for idx in (sel or range(len(rows))):
    s.b.load_state(os.path.join(d, "menu.state")); s.wait(60)
    grab("screen", idx, lambda: nav.tap_row_from_top(idx))
    grab("settings", idx, lambda: s.tap(400, 245, settle=800))
