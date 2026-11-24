#!/usr/bin/env python3
"""E7: etykiety PL wierszy list nastaw wprost z firmware: dla kazdej listy z list_scales.json wchodzi w ekran (poziom 3; kaskada/magazyn w LC3), czyta teksty widgetow
etykiet (x~30) po pozycji pionowej: etykieta wiersza o slocie s ma ay = ay(slot 0) + 50*s. Wynik: ui_model/list_labels_pl.json {klucz_listy: {idx: {slot, label_pl}}}.
Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/list_labels.py L3DIR LC3DIR OUT.json"""
import json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import ui_session as U, ctor_trace as C, ui_extras as X, ui_nav
from PIL import Image
l3, lc3, out = sys.argv[1:4]
sc = json.load(open(paths.UI_MODEL / "list_scales.json"))["lists"]; res = json.load(open(out)) if os.path.exists(out) else {}
for key, lst in sc.items():
    if key in res and res[key]["labels_found"] > 0 and key not in os.environ.get("REDO", "").split(","): continue
    node = lst["node"]; idx, kind = node.split("_", 1); idx = int(idx); d = lc3 if idx in (9, 10) else l3
    s = U.UiSession.from_checkpoint(str(paths.FIRMWARE), os.path.join(d, "menu.state"), None); s.wait(120)
    nav = U.ListNav(s); nav.tall = Image.open(os.path.join(d, "menu_tall.png")); nav.rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb")); t = C.Tracer(s); t.log.clear()
    ok = ui_nav.tap_incremental(s, nav, idx) and hex(s.b.rd(s.b.rd(0x20024818))) != "0x808f66c"
    if not ok and idx >= 13:      # ogon menu poziomu 3 (19 wierszy w konfiguracji FULL)
        s = U.UiSession.from_checkpoint(str(paths.FIRMWARE), os.path.join(d, "menu.state"), None); s.wait(120)
        nav = U.ListNav(s); nav.tall = Image.open(os.path.join(d, "menu_tall.png")); nav.rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb")); t = C.Tracer(s); t.log.clear()
        ok = ui_nav.tap_tail(s, nav, idx, 19)
    if not ok: print(key, "TAP_FAILED", flush=True); continue
    s.wait(700)
    if kind == "settings": s.tap(400, 245, settle=800); s.wait(500)
    ws = C.widget_table(s, t); ex = X.extract(s, ws); lab = {}
    for w in ws:
        e = ex.get(w["this"], {})
        if e.get("cls") == "text" and not e.get("hidden") and w["ax"] < 100 and w["ay"] >= 40 and w["w"] > 60 and e.get("text"): lab.setdefault(w["ay"], e["text"])
    ays = sorted(lab); base = ays[0] if ays else None; rows = {}; R_ = lst["rows"]
    known = {r["idx"]: r["slot"] for r in R_ if r.get("slot") is not None and not (r["slot"] == 0 and r["idx"] != 0)}      # zmierzone sloty (slot 0 przy idx>0 = brak danych)
    def slot_of(r):
        if r["idx"] in known: return known[r["idx"]], "zmierzony"
        lo = [i for i in known if i < r["idx"]]; hi = [i for i in known if i > r["idx"]]
        if lo and hi:
            a, b = max(lo), min(hi)
            if known[a] - a == known[b] - b: return r["idx"] + known[a] - a, "wnioskowany (kotwice o tym samym przesunieciu)"
        if lo and not hi: a = max(lo); return r["idx"] + known[a] - a, "ekstrapolowany (ostatnia kotwica)"
        if hi and not lo: b = min(hi); return r["idx"] + known[b] - b, "ekstrapolowany (pierwsza kotwica)"
        return None, None
    used = set()
    for r in R_:
        if base is None: continue
        sl, how = slot_of(r)
        if sl is None or not r.get("pid"): continue
        t_ = lab.get(base + 50 * sl)
        if t_ and (sl in used): t_ = None
        if t_: used.add(sl)
        if t_: rows[str(r["idx"])] = dict(slot=sl, label_pl=t_, pid=r.get("pid"), how=how)
    res[key] = dict(node=node, base_ay=base, labels_found=len(lab), rows=rows); json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
    print(key, node, "etykiet:", len(lab), "przypisano:", len(rows), "z", len(lst["rows"]), flush=True)
