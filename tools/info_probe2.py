#!/usr/bin/env python3
"""Etap E2: INFO - wypelnienia wildcardow czytane przy WEJSCIU na ekran: dla PID (0x3664 wersja SW, 0x3665 nazwa kotla, 0x2170 videRoom PIN) ustawia storage PRZED wejsciem (set_local) i czyta teksty.
Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/info_probe2.py LDIR OUT.json ROW_INFO. Tylko emulator."""
import json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths, ui_session as U, ctor_trace as C, ui_extras as X, ui_nav
from PIL import Image
d, out, idx = sys.argv[1], sys.argv[2], int(sys.argv[3])
def run(pid, v):
    s = U.UiSession.from_checkpoint(str(paths.FIRMWARE), os.path.join(d, "menu.state"), None); s.wait(120)
    nav = U.ListNav(s); nav.tall = Image.open(os.path.join(d, "menu_tall.png")); nav.rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb")); t = C.Tracer(s); t.log.clear()
    if pid is not None: s.set_local(pid, v)
    ok = ui_nav.tap_incremental(s, nav, idx) or ui_nav.tap_tail(s, nav, idx, 19); s.wait(1500)
    ws = C.widget_table(s, t); ex = X.extract(s, ws)
    return sorted((w["ay"], w["ax"], ex[w["this"]]["text"]) for w in ws if w["this"] in ex and ex[w["this"]].get("cls") == "text" and not ex[w["this"]].get("hidden") and (ex[w["this"]].get("text") or "").strip() and w["ay"] >= 40)
res = {"base": run(None, 0) if not __import__("os").environ.get("INFO_FMT") else [], "cases": []}
import os as _o
SETS = ((0x3664, (0, 1, 2213, 2214, 3000, 65535)), (0x3665, (0, 1, 5678, 100, 1000, 4294967295)), (0x2170, (0, 1, 5678, 1234, 65535)))
if _o.environ.get("INFO_FMT"): SETS = ((0x3664, tuple(int(x) for x in _o.environ["INFO_FMT"].split(",") if x.isdigit())),)
for pid, vals in SETS:
    for v in vals:
        res["cases"].append(dict(pid="0x%04X" % pid, value=v, texts=run(pid, v))); print(res["cases"][-1], flush=True)
        json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
