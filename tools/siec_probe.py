#!/usr/bin/env python3
"""Etap E: ekran SIEC - tabela modulow CAN. Skan Node ID 1..127: heartbeat 0x700+n (05) + Identity 0x580+n (43 18 10 02 u32) -> teksty wierszy tabeli z RAM (nazwa | Node ID | SW | kolumna 4).
Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/siec_probe.py L1DIR OUT.json ROW_SIEC I N   (shard I z N). Tylko emulator."""
import json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths, ui_session as U, ctor_trace as C, ui_extras as X, ui_nav
from PIL import Image
d, out, idx, I, N = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
res = json.load(open(out)) if os.path.exists(out) else {}
def boot():
    s = U.UiSession.from_checkpoint(str(paths.FIRMWARE), os.path.join(d, "menu.state"), None); s.wait(120)
    nav = U.ListNav(s); nav.tall = Image.open(os.path.join(d, "menu_tall.png")); nav.rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb")); t = C.Tracer(s); t.log.clear()
    ok = ui_nav.tap_incremental(s, nav, idx) or ui_nav.tap_tail(s, nav, idx, 19); s.wait(900); return s, t, ok
def feed(s, nodes, rounds=6, ident=(0, 0, 0, 0)):
    for _ in range(rounds):
        for n in nodes:
            s.can(0x700 + n, [5]); s.wait(12); s.can(0x580 + n, [0x43, 0x18, 0x10, 2] + list(ident)); s.wait(12)
        s.wait(120)
def rows(s, t):
    ws = C.widget_table(s, t); ex = X.extract(s, ws); g = {}
    for w in ws:
        e = ex.get(w["this"])
        if e and e.get("cls") == "text" and not e.get("hidden") and (e.get("text") or "").strip() and w["ay"] >= 40: g.setdefault(w["ay"], []).append((w["ax"], e["text"]))
    return [[tx for _, tx in sorted(v)] for _, v in sorted(g.items())]
for n in range(1, 128):
    if n % N != I or str(n) in res: continue
    s, t, ok = boot()
    if not ok: res[str(n)] = dict(status="NIE_WESZLO"); continue
    feed(s, [n]); s.wait(500); res[str(n)] = dict(node="0x%02X" % n, rows=rows(s, t))
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1); print("0x%02X" % n, res[str(n)]["rows"], flush=True)
