#!/usr/bin/env python3
"""Test regul widocznosci wierszy MENU: dla kombinacji (poziom, 0x2105, 0x2106, 0x2107, 0x2108, 0x350C, 0x3525) swiezy rozruch, wejscie w MENU i odczyt napisow wierszy
(widoczne widgety tekstowe etykiet, z RAM - bez przewijania). Wynik: JSON {kombinacja: [tytuly wg ay]}. Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/menu_rows_probe.py OUT.json COMBO ...   (COMBO = L,2105,2106,2107,2108,350C,3525)"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import ui_session as U, ctor_trace as C, ui_extras as X
out = sys.argv[1]; res = json.load(open(out)) if os.path.exists(out) else {}
for cb in sys.argv[2:]:
    if cb in res: continue
    L, a, b, c, d, e, f = [int(x) for x in cb.split(",")]
    cfg = {0x2105: a, 0x2106: b, 0x2107: c, 0x2108: d}
    if e: cfg.update({0x350C: e, 0x351A: 2})
    if f: cfg[0x3525] = f
    s = U.UiSession(str(paths.FIRMWARE), None); t = C.Tracer(s); s.boot(500)
    for p, x in cfg.items(): s.set_local(p, x)
    s.set_access(L); s.wait(300); s.tap(34, 235, settle=700); s.wait(600)
    ws = C.widget_table(s, t); ex = X.extract(s, ws)
    rows = sorted((w["ay"], ex[w["this"]]["text"]) for w in ws if ex.get(w["this"], {}).get("cls") == "text" and not ex[w["this"]].get("hidden") and ex[w["this"]].get("text") and 55 <= w["ax"] <= 90 and w["ay"] >= 46)
    res[cb] = [t_ for _, t_ in rows]; json.dump(res, open(out, "w"), ensure_ascii=False); print(cb, len(rows), flush=True)
