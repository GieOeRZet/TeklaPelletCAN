#!/usr/bin/env python3
"""PASS 55: katalog widgetow wszystkich zapisanych stanow ekranow (ui_fuzz): dla kazdego stanu -> widget_dump + opis (bitmapy: id/rozmiar, teksty: PL).
python3 -I tools/widget_inventory.py FW.bin OUT.json STATE_GLOB... """
import glob, json, os, struct, sys, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, widget_dump as W
fw, out = sys.argv[1], sys.argv[2]; states = sorted(f for g in sys.argv[3:] for f in glob.glob(g))
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
man = {}
mp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analiza", "FW2213TK-2026-11-22", "data", "bitmaps", "manifest.csv")
if os.path.exists(mp): man = {int(r["id"]): (r["width"], r["height"]) for r in csv.DictReader(open(mp))}
s = U.UiSession.from_checkpoint(fw, states[0], None); res = []
for st in states:
    try: s.b.load_state(st); s.wait(40); ws = W.dump(s)
    except Exception as e: print("blad", st, e); continue
    items = []
    for w in ws:
        d = dict(w)
        if w["type"] == "Image" and w["id"] in man: d["bitmap"] = w["id"]; d["bmp_size"] = "%sx%s" % man[w["id"]]
        if w["type"] == "TextArea": d["text_pl"] = pl(w["id"])
        items.append(d)
    title = next((i["text_pl"] for i in sorted(items, key=lambda i: i["y"]) if i["type"] == "TextArea" and i["y"] < 46 and 100 < i["x"] < 380), "")
    res.append(dict(state=os.path.basename(st), title=title, widgets=items)); print(os.path.basename(st), repr(title), len(items), flush=True)
    json.dump(res, open(out, "w"), ensure_ascii=False)
