#!/usr/bin/env python3
"""E7: eksport ekranu menu do karty web: tlo statyczne (PNG, bez pol dynamicznych) + JSON pol dynamicznych (prostokat, czcionka, kolor, wyrownanie, szablon tekstu, widget, PID jesli znany z bindingu).
Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/export_card_screen.py LEVELDIR ROW NAME OUTDIR [BINDING.json] [--settings]
 LEVELDIR = katalog z menu.state/rows.pkl (np. /tmp/w/L1), ROW = indeks wiersza menu (tap od gory), NAME = nazwa pliku (np. KOCIOL)."""
import json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import ui_session as U, ctor_trace as C, ui_extras as X, ui_render as R
from PIL import Image
args = [a for a in sys.argv[1:] if not a.startswith("--")]; settings = "--settings" in sys.argv
d, row, name, out = args[0], int(args[1]), args[2], args[3]; bind = json.load(open(args[4])) if len(args) > 4 else []
wpid = {}
for b in bind:
    for w in b.get("widgets", []):
        if w.get("widget"): wpid.setdefault(w["widget"], []).append(dict(pid=b["pid"], fmt=w.get("fmt")))
os.makedirs(out, exist_ok=True)
if row < 0:      # ROW=-1: ekran glowny (swiezy rozruch, konfiguracja jak home_inventory.py)
    s = U.UiSession(str(paths.FIRMWARE), None); t = C.Tracer(s); s.boot(500)
    for p_, v_ in {0x2105: 4, 0x2106: 1, 0x2107: 1, 0x2108: 1}.items(): s.set_local(p_, v_)
    s.set_access(0); s.wait(4500)
else:
    s = U.UiSession.from_checkpoint(str(paths.FIRMWARE), os.path.join(d, "menu.state"), None); s.wait(120)
    nav = U.ListNav(s); nav.tall = Image.open(os.path.join(d, "menu_tall.png")); nav.rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb")); t = C.Tracer(s); t.log.clear()
    assert nav.tap_row_from_top(row); s.wait(700)
if settings: s.tap(400, 245, settle=800); s.wait(500)
for tp in filter(None, os.environ.get("EXTRA_TAPS", "").split(";")):      # np. EXTRA_TAPS="414,130" (kolejne stukniecia po wejsciu w ekran)
    x_, y_ = [int(v) for v in tp.split(",")]; s.tap(x_, y_, settle=900); s.wait(400)
ws = C.widget_table(s, t); ex = X.extract(s, ws); ref = s.shot()
dyn = []; static = []
for w in ws:
    e = ex.get(w["this"], {})
    if e.get("hidden"): continue
    if e.get("cls") == "text" and ("\x02" in (e.get("text") or "") or w.get("wildcard")):
        dyn.append(dict(widget=w["this"], rect=[w["ax"], w["ay"], w["w"], w["h"]], font=e["font"], align=e["align"], color="#%02x%02x%02x" % R.rgb565(e["color"]), template=(e["text"] or "").replace("\x02", "{}"), sample=e["text"], bind=wpid.get(w["this"], [])))
    else: static.append(w)
keep = {w["this"] for w in static}
img = R.render([w for w in ws if w["this"] in keep], ex)
img.save(os.path.join(out, name + ".png")); ref.save(os.path.join(out, name + "_ref.png"))
json.dump(dict(name=name, size=[480, 272], dynamic=dyn, source="emulator render z danych (STRONG); bindingi PID: data_binding.py gdzie dostepne"), open(os.path.join(out, name + ".json"), "w"), ensure_ascii=False, indent=1)
print(name, "dynamicznych pol:", len(dyn), "statycznych widgetow:", len(static))
