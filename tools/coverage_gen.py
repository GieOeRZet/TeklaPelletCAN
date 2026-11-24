#!/usr/bin/env python3
"""E3: automat pokrycia. Dla pary (poziom PIN, konfiguracja) buduje punkt kontrolny (ui_prepare_cfg), potem dla kazdego widocznego wiersza MENU
wchodzi w ekran i (stukniecie 400,245) w nastawy, wyciaga tablice widgetow (ctor_trace) + extras, renderuje z danych i porownuje ze zrzutem emulatora.
Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/coverage_gen.py LEVEL CONFIG OUTROOT      (CONFIG jak w menu_tree.visible_in: DEFAULT|FULL|2105=N|0x2106=0|350C=1|3525=1|350C=1,3525=1)
Wynik: OUTROOT/L<level>_<slug>/result.json (+ PNG ref/render dla komorek > 8%). Mapowanie konfiguracji -> PID: INFERENCE, weryfikowane liczba wierszy MENU vs visible_in (pole rows_match)."""
import json, os, pickle, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import ui_session as U, ctor_trace as C, ui_extras as X, ui_render as R
from PIL import Image
import numpy as np
level, config, outroot = int(sys.argv[1]), sys.argv[2], sys.argv[3]
BASE = {0x2105: 4, 0x2106: 1, 0x2107: 1, 0x2108: 1}
def cfg_pids(c):
    p = dict(BASE)
    if c == "DEFAULT": p.update({0x2105: 1, 0x2106: 0, 0x2107: 0, 0x2108: 0})
    elif c == "FULL": pass
    else:
        for part in c.split(","):
            k, v = part.split("="); k = int(k, 16); v = int(v)
            p[k] = v
            if k == 0x350C: p[0x351A] = 2
    return p
if False: pass
pids = cfg_pids(config); slug = re.sub(r"[^0-9A-Za-z]+", "_", config).strip("_")
out = os.path.join(outroot, "L%d_%s" % (level, slug)); os.makedirs(out, exist_ok=True)
fw = str(paths.FIRMWARE)
_m = json.load(open(paths.UI_MODEL / "menu_tree.json"))
if not any("%s|L%d" % (config, level) in r["visible_in"] for r in _m["menu_rows"]): print("BRAK wierszy w komorce", level, config); sys.exit(0)
if not os.path.exists(os.path.join(out, "rows.pkl")):
    subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_prepare_cfg.py"), fw, out, str(level)] + ["0x%X=%d" % kv for kv in pids.items()], check=True, stdout=subprocess.DEVNULL)
menu = json.load(open(paths.UI_MODEL / "menu_tree.json")); nodes = {n["id"]: n for n in menu["nodes"]}
exp = sorted([r for r in menu["menu_rows"] if "%s|L%d" % (config, level) in r["visible_in"]], key=lambda r: r["row"])
rows = pickle.load(open(os.path.join(out, "rows.pkl"), "rb"))
def true_rows():      # rzeczywista dlugosc MENU: przewin do konca (ListNav.build bywa zawyzone przy zszywaniu)
    s0 = U.UiSession.from_checkpoint(fw, os.path.join(out, "menu.state"), None); s0.wait(120)
    nv = U.ListNav(s0); nv.tall = Image.open(os.path.join(out, "menu_tall.png")); nv.rows = rows
    for _ in range(30):
        if not s0.drag_until_change(240, 235, 240, 175, attempts=4): break
    o = nv.offset(s0.shot())[1]; return round((o + 272 - 46 - 4) / 50), o
n_true, o_end = true_rows()
res = dict(level=level, config=config, pids={hex(k): v for k, v in pids.items()}, rows_actual=n_true, rows_stitched=len(rows), rows_expected=len(exp), rows_match=n_true == len(exp), cells=[])
def metrics(ws, ex, ref):
    a = R.render(ws, ex); dd = np.abs(np.asarray(a).astype(int) - np.asarray(ref.convert("RGB")).astype(int)).sum(axis=2)
    return a, round(float(dd.mean() / 3), 2), round(float((dd > 40).mean() * 100), 1)
for i, er in enumerate(exp):
    tgt = er.get("target")
    if i >= n_true and tgt and nodes.get(tgt, {}).get("kind") == "screen":
        res["cells"].append(dict(row=er["row"], index=i, node=tgt, title=er["title_pl"], kind="screen", status="NOT_VISIBLE_IN_EMULATOR (wg visible_in oczekiwany, brak w MENU)")); continue
    if i >= len(rows) or not tgt or nodes.get(tgt, {}).get("kind") != "screen" or tgt == "PROGRAM": continue
    s = U.UiSession.from_checkpoint(fw, os.path.join(out, "menu.state"), None); s.wait(120)
    nav = U.ListNav(s); nav.tall = Image.open(os.path.join(out, "menu_tall.png")); nav.rows = rows; t = C.Tracer(s); t.log.clear()
    if not nav.tap_row_from_top(i): res["cells"].append(dict(row=er["row"], index=i, node=tgt, kind="screen", status="TAP_FAILED")); continue
    s.wait(700)
    cell = {}
    for kind, tap in (("screen", None), ("settings", (400, 245))):
        try:
            if kind == "settings" and cell.get("view") == "0x808f944": break      # ekran jest juz lista nastaw (brak kafla nastaw)
            if tap: s.tap(tap[0], tap[1], settle=800); s.wait(500)
            ws = C.widget_table(s, t); ex = X.extract(s, ws); ref = s.shot(); a, mae, pct = metrics(ws, ex, ref)
            cell = dict(row=er["row"], index=i, node=tgt, title=er["title_pl"], kind=kind, mae=mae, pct_diff=pct, view=hex(s.b.rd(s.b.rd(0x20024818))), widgets=len(ws))
            if pct > 8:
                base = os.path.join(out, "%s_%s_%d" % (tgt, kind, er["row"])); ref.save(base + "_ref.png"); a.save(base + "_render.png")
        except Exception as e: cell = dict(row=er["row"], index=i, node=tgt, kind=kind, error=repr(e)[:120])
        if cell.get("kind"): res["cells"].append(cell)
        print(level, config, cell, flush=True)
    json.dump(res, open(os.path.join(out, "result.json"), "w"), ensure_ascii=False, indent=1)
json.dump(res, open(os.path.join(out, "result.json"), "w"), ensure_ascii=False, indent=1)
print("DONE", out, "rows_match", res["rows_match"], len(res["cells"]), "komorek")
