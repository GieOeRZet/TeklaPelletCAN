#!/usr/bin/env python3
"""E7: etykiety PL wierszy list nastaw wprost z firmware: dla kazdej listy z list_scales.json wchodzi w ekran (poziom 3; kaskada/magazyn w LC3), czyta teksty widgetow
etykiet (x~30) po pozycji pionowej: etykieta wiersza o slocie s ma ay = ay(slot 0) + 50*s. Wynik: ui_model/list_labels_pl.json {klucz_listy: {idx: {slot, label_pl}}}.
Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/list_labels.py L3DIR LC3DIR OUT.json"""
import json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import ui_session as U, ctor_trace as C, ui_extras as X
from PIL import Image
l3, lc3, out = sys.argv[1:4]
sc = json.load(open(paths.UI_MODEL / "list_scales.json"))["lists"]; res = json.load(open(out)) if os.path.exists(out) else {}
for key, lst in sc.items():
    if key in res: continue
    node = lst["node"]; idx, kind = node.split("_", 1); idx = int(idx); d = lc3 if idx in (9, 10) else l3
    s = U.UiSession.from_checkpoint(str(paths.FIRMWARE), os.path.join(d, "menu.state"), None); s.wait(120)
    nav = U.ListNav(s); nav.tall = Image.open(os.path.join(d, "menu_tall.png")); nav.rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb")); t = C.Tracer(s); t.log.clear()
    if not nav.tap_row_from_top(idx): print(key, "TAP_FAILED", flush=True); continue
    s.wait(700)
    if kind == "settings": s.tap(400, 245, settle=800); s.wait(500)
    ws = C.widget_table(s, t); ex = X.extract(s, ws); lab = {}
    for w in ws:
        e = ex.get(w["this"], {})
        if e.get("cls") == "text" and not e.get("hidden") and w["ax"] < 100 and w["ay"] >= 40 and w["w"] > 60 and e.get("text"): lab.setdefault(w["ay"], e["text"])
    ays = sorted(lab); base = ays[0] if ays else None; rows = {}
    for r in lst["rows"]:
        sl = r.get("slot")
        if base is None or sl is None or (sl == 0 and r["idx"] != 0): continue
        t_ = lab.get(base + 50 * sl)
        if t_: rows[str(r["idx"])] = dict(slot=sl, label_pl=t_, pid=r.get("pid"))
    res[key] = dict(node=node, base_ay=base, labels_found=len(lab), rows=rows); json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
    print(key, node, "etykiet:", len(lab), "przypisano:", len(rows), "z", len(lst["rows"]), flush=True)
