#!/usr/bin/env python3
"""PASS 54: etykiety wierszy NASTAWY przez dialog: dla kazdego wiersza listy (k-ty od gory) dotyka go i zapisuje tytul dialogu (TypedText) + zrzut.
Kolejnosc wierszy = kolejnosc listy z panel_lists_by_level.csv (poziom/klasa). python3 -I tools/settings_rows.py FW.bin OUTDIR ROW_IDX LEVEL DST_DIR
OUTDIR: menu.state/rows.pkl/menu_tall.png z ui_explore --prepare (poziom jak LEVEL)."""
import os, sys, json, pickle, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U
from unicorn import UC_HOOK_MEM_READ
from PIL import Image
fw, out, idx, level, dst = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]; os.makedirs(dst, exist_ok=True)
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
s = U.UiSession.from_checkpoint(fw, os.path.join(out, "menu.state"), dst); s.wait(120)
nav0 = U.ListNav(s); nav0.tall = Image.open(os.path.join(out, "menu_tall.png")); nav0.rows = rows
nav0.tap_row_from_top(idx); s.wait(600); s.tap(400, 245, settle=1200)
top = os.path.join(dst, "list_top.state"); s.checkpoint(top)
nav = U.ListNav(s); lrows = nav.build(); nav.tall.save(os.path.join(dst, "list_tall.png")); print("wierszy listy:", len(lrows), flush=True)
order = []; tb = U.UiSession.TEXT_LANG_PTRS[0] - 57 * 4
def rt(uc, a, ad, sz, v, ud):
    i = (ad - tb) // 4
    if i not in order: order.append(i)
s.b.mu.hook_add(UC_HOOK_MEM_READ, rt, begin=tb, end=tb + 495 * 4 - 1)
res = []
for k in range(len(lrows)):
    s.b.load_state(top); s.wait(80); nav.rows = lrows; order.clear()
    ok = nav.tap_row_from_top(k, settle=900); s.wait(500)
    im = s.shot("row%02d" % k) if False else s.shot(); im.save(os.path.join(dst, "row%02d.png" % k))
    res.append(dict(k=k, tapped=ok, texts=[(i, pl(i)) for i in order]))
    print(k, ok, [(i, pl(i)[:30]) for i in order][:6], flush=True)
    json.dump(dict(row=idx, level=level, items=res), open(os.path.join(dst, "rows.json"), "w"), ensure_ascii=False, indent=1)
