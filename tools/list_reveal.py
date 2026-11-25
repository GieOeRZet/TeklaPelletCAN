#!/usr/bin/env python3
"""Odslanianie warunkowych wierszy list NASTAW: dla wezla (indeks wiersza menu, kind=settings) i wariantow konfiguracji (PID=wartosc[,PID=wartosc]) wchodzi w liste
(set_local PRZED wejsciem) i zapisuje etykiety wierszy (teksty widgetow-etykiet, x<100) z kontenera zawartosci (vptr 0x807c6f0).
Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/list_reveal.py L3DIR IDX OUT.json "base" "0x299F=1" "0x3606=1,0x3707=1" ...   (pusty wariant 'base' = bez zmian). Tylko emulator."""
import json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths, ui_session as U, ctor_trace as C, ui_extras as X, ui_nav
from PIL import Image
d, idx, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
res = json.load(open(out)) if os.path.exists(out) else {}
for var in sys.argv[4:]:
    if var in res: continue
    s = U.UiSession.from_checkpoint(str(paths.FIRMWARE), os.path.join(d, "menu.state"), None); s.wait(120)
    nav = U.ListNav(s); nav.tall = Image.open(os.path.join(d, "menu_tall.png")); nav.rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb")); t = C.Tracer(s); t.log.clear()
    if var != "base":
        for kv in var.split(","): s.set_local(int(kv.split("=")[0], 16), int(kv.split("=")[1]))
    if not ui_nav.tap_incremental(s, nav, idx): res[var] = "NIE_WESZLO"; json.dump(res, open(out, "w"), indent=1); continue
    s.wait(700); s.tap(400, 245, settle=800); s.wait(800)
    ws = C.widget_table(s, t); ex = X.extract(s, ws); rd = s.b.rd
    labs = []
    for w in ws:
        e = ex.get(w["this"], {})
        if e.get("cls") == "text" and w["ax"] < 100 and e.get("text") and not e["text"].isdigit():
            p = rd(int(w["this"], 16) + 0x14); gp = rd(p + 0x14) if 0x20000000 <= p < 0x20030000 else 0
            if 0x20000000 <= gp < 0x20030000 and rd(gp) == 0x807c6f0: labs.append((w["ay"], e["text"]))
    res[var] = [x[1] for x in sorted(labs)]
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1); print(var, len(res[var]), flush=True)
