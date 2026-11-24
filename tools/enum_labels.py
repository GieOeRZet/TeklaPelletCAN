#!/usr/bin/env python3
"""1:1: etykiety opcji wyliczen list nastaw BEZ dialogu: dla kazdego wiersza typu enum (lists.json) wstrzykuje kolejne wartosci PID (inject_param, tylko emulator)
i czyta tekst wartosci w wierszu listy (widget po prawej stronie etykiety, z RAM). Wynik: ui_model/enum_labels.json {klucz: {idx: {pid, name, options: {wartosc: tekst}}}}.
Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/enum_labels.py L3DIR LC3DIR OUT.json [KLUCZ ...]"""
import json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import ui_session as U, ctor_trace as C, ui_extras as X, ui_nav
from PIL import Image
l3, lc3, out = sys.argv[1:4]; only = sys.argv[4:]
lab = json.load(open(paths.UI_MODEL / "list_labels_pl.json"))["lists"]; sc = json.load(open(paths.UI_MODEL / "list_scales.json"))["lists"]
L = json.load(open(paths.UI_MODEL / "lists.json"))["lists"]; res = json.load(open(out)) if os.path.exists(out) else {}
N = lambda v: int(str(v), 16)
for key in sc:
    if only and key not in only: continue
    rows = {str(r["idx"]): r for k2, v2 in L.items() if k2.split("|")[0] == key for r in v2 if r.get("pid") and (r.get("kind") == "enum" or (os.environ.get("ENUM_ALL") and r.get("raw_max") is not None and 0 <= int(r.get("raw_max")) - int(r.get("raw_min") or 0) <= 6))}
    rows = {i: r for i, r in rows.items() if i in lab.get(key, {}).get("rows", {})}
    if not rows: continue
    node = sc[key]["node"]; idx, kind = node.split("_", 1); idx = int(idx); d = lc3 if idx in (9, 10) else l3
    s = U.UiSession.from_checkpoint(str(paths.FIRMWARE), os.path.join(d, "menu.state"), None); s.wait(120)
    nav = U.ListNav(s); nav.tall = Image.open(os.path.join(d, "menu_tall.png")); nav.rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb")); t = C.Tracer(s); t.log.clear()
    if not (ui_nav.tap_incremental(s, nav, idx) and hex(s.b.rd(s.b.rd(0x20024818))) != "0x808f66c"): print(key, "TAP_FAILED", flush=True); continue
    s.wait(700)
    if kind == "settings": s.tap(400, 245, settle=800); s.wait(500)
    ws = C.widget_table(s, t); tmp = "/tmp/el_%s.state" % key.replace("0x", ""); s.checkpoint(tmp); res.setdefault(key, {})
    for i, r in rows.items():
        base_ay = lab[key]["base_ay"]; slot = lab[key]["rows"][i]["slot"]; ay = base_ay + 50 * slot; opts = {}
        for v in range(int(r["raw_min"]), int(r["raw_max"]) + 1):
            s.b.load_state(tmp); s.wait(100); got = s.inject_param(N(r["pid"]), v, 3, 60); s.wait(250)
            ex = X.extract(s, ws); tx = [ex[w["this"]]["text"] for w in ws if ex.get(w["this"], {}).get("cls") == "text" and not ex[w["this"]].get("hidden") and w["ay"] == ay and w["ax"] > 150 and ex[w["this"]].get("text")]
            opts[str(v)] = dict(text=tx[0] if tx else None, stored=got)
        res[key][i] = dict(pid=r["pid"], name=lab[key]["rows"][i]["label_pl"], options=opts); json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
        print(key, i, res[key][i]["name"], {k: v["text"] for k, v in opts.items()}, flush=True)
