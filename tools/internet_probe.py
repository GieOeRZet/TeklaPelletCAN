#!/usr/bin/env python3
"""Etap E3: ekran INTERNET - pola, teksty i zrodla. Baza + set_local(PID) PRZED wejsciem (teksty wypelniane przy wejsciu) dla PID 0x3730..0x3745 i wybranych; zmiany tekstow/widocznosci/przelacznikow.
Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/internet_probe.py LDIR OUT.json ROW [PID ...]. Tylko emulator."""
import json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths, ui_session as U, ctor_trace as C, ui_extras as X, ui_nav
from PIL import Image
d, out, idx = sys.argv[1], sys.argv[2], int(sys.argv[3]); pids = [int(x, 16) for x in sys.argv[4:]] or list(range(0x3730, 0x3746))
def run(pid, v, shot=None):
    s = U.UiSession.from_checkpoint(str(paths.FIRMWARE), os.path.join(d, "menu.state"), None); s.wait(120)
    nav = U.ListNav(s); nav.tall = Image.open(os.path.join(d, "menu_tall.png")); nav.rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb")); t = C.Tracer(s); t.log.clear()
    if pid is not None:
        try: s.set_local(pid, v)
        except KeyError: return None
    ok = ui_nav.tap_incremental(s, nav, idx) or ui_nav.tap_tail(s, nav, idx, 19); s.wait(1500)
    if shot: s.shot().save(shot)
    ws = C.widget_table(s, t); ex = X.extract(s, ws); r = {}
    for w in ws:
        e = ex.get(w["this"])
        if not e or e.get("hidden") or w["ay"] < 40: continue
        if e.get("cls") == "text" and (e.get("text") or "").strip(): r["T@%d,%d" % (w["ay"], w["ax"])] = e["text"]
        elif e.get("cls") == "btn": r["B@%d,%d" % (w["ay"], w["ax"])] = e.get("bmp")
        elif e.get("cls") == "image": r["I@%d,%d" % (w["ay"], w["ax"])] = "img"
    return r
base = run(None, 0, shot="/tmp/w/internet_base.png"); res = {"base": base, "cases": []}; print(base, flush=True)
for pid in pids:
    for v in (1, 0x41424344, 5):
        r = run(pid, v)
        if r is None: print("brak rekordu", hex(pid), flush=True); break
        diff = {k: (base.get(k), r.get(k)) for k in set(base) | set(r) if base.get(k) != r.get(k)}
        res["cases"].append(dict(pid="0x%04X" % pid, value=v, diff=diff)); print("0x%04X" % pid, v, diff, flush=True)
        json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
