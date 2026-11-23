#!/usr/bin/env python3
"""PASS 54: polskie etykiety wierszy ekranu NASTAWY w kolejnosci rysowania. Wchodzi na ekran (wiersz menu + kafel ustawien), przewija w gore
i zapisuje identyfikatory TypedText czytane przez firmware (w kolejnosci pierwszego odczytu) po kazdym kroku -> ids + tekst PL.
python3 -I tools/settings_labels.py FW.bin OUTDIR ROW_IDX LEVEL OUT.json   (OUTDIR: menu.state/rows.pkl/menu_tall.png z ui_explore --prepare)"""
import os, sys, json, pickle, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U
from unicorn import UC_HOOK_MEM_READ
from PIL import Image
fw, out, idx, level, dst = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
raw = open(fw, "rb").read(); B = 0x08010000
def pl(i):
    try:
        p = struct.unpack_from("<I", raw, 0x5BD80 + 4 * i)[0]; o = p - B; r = []
        while True:
            c = struct.unpack_from("<H", raw, o)[0]
            if c == 0: break
            r.append(chr(c)); o += 2
        return "".join(r)
    except Exception: return "?"
rows = pickle.load(open(os.path.join(out, "rows.pkl"), "rb"))
s = U.UiSession.from_checkpoint(fw, os.path.join(out, "menu.state"), None); s.wait(120)
nav = U.ListNav(s); nav.tall = Image.open(os.path.join(out, "menu_tall.png")); nav.rows = rows
nav.tap_row_from_top(idx); s.wait(600); s.tap(400, 245, settle=1200)
order = []
tb = U.UiSession.TEXT_LANG_PTRS[0] - 57 * 4
def rt(uc, a, ad, sz, v, ud):
    i = (ad - tb) // 4
    if i not in order: order.append(i)
s.b.mu.hook_add(UC_HOOK_MEM_READ, rt, begin=tb, end=tb + 495 * 4 - 1)
pages = []; last = None
for step in range(14):
    s.wait(400); h = s.body_hash(s.shot())
    pages.append(list(order)); order.clear()
    if h == last: break
    last = h; s.drag_until_change(240, 235, 240, 150, attempts=3)
json.dump(dict(row=idx, level=level, pages=[[(i, pl(i)) for i in p] for p in pages]), open(dst, "w"), ensure_ascii=False, indent=1)
print("OK", idx, "kroki", len(pages))
