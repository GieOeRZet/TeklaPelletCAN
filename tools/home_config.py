#!/usr/bin/env python3
"""Ktore elementy HOME pojawiaja sie przy jakiej konfiguracji: dla kombinacji (0x2105, 0x2106, 0x2107, 0x2108) swiezy rozruch, odczyt widocznych widgetow HOME z RAM
(widocznosc efektywna) -> podpis (rect+bitmapa/tekst). Wynik: ui_model/home_config.json. Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/home_config.py OUT.json [LEVEL] COMBO ...  (COMBO = 4,1,1,1)"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import ui_session as U, ctor_trace as C, ui_extras as X
out = sys.argv[1]; level = int(sys.argv[2]); combos = sys.argv[3:]
res = json.load(open(out)) if os.path.exists(out) else {}
for cb in combos:
    if cb in res: continue
    v = [int(x) for x in cb.split(",")]; cfg = dict(zip((0x2105, 0x2106, 0x2107, 0x2108), v))
    s = U.UiSession(str(paths.FIRMWARE), None); t = C.Tracer(s); s.boot(500)
    for p, x in cfg.items(): s.set_local(p, x)
    s.set_access(level); s.wait(4500); ws = C.widget_table(s, t); ex = X.extract(s, ws); items = []
    for w in ws:
        e = ex.get(w["this"], {})
        if e.get("hidden") or w["w"] <= 0 or w["h"] <= 0 or w["w"] > 479: continue
        items.append(dict(rect=[w["ax"], w["ay"], w["w"], w["h"]], cls=e.get("cls"), bmp=e.get("bmp") if e.get("bmp") is not None else w.get("bitmap_id"), text=e.get("text"), tid=e.get("tid")))
    res[cb] = dict(cfg={hex(k): x for k, x in cfg.items()}, level=level, visible=sorted(items, key=lambda i: (i["rect"], str(i["bmp"]), str(i["text"]))))
    json.dump(res, open(out, "w"), ensure_ascii=False); print(cb, len(items), flush=True)
