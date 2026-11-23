#!/usr/bin/env python3
"""PASS 57: inwentarz widgetow wg ekranow z powtorki przejsc ui_fuzz: dla wezla k (z logu 'nowy ekran #k (z #p tap x,y)') wczytuje stan rodzica p, stuka (x,y) z sledzeniem konstrukcji
(tools/ctor_trace.py) i zapisuje liste widgetow (rect, rola, id tekstu/bitmapy, rodzic) + tytul (TextArea y<46 srodek). python3 -I tools/screen_inventory.py FW.bin FUZZ_DIR TAG OUT.json"""
import os, re, sys, json, struct, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, ctor_trace as C
fw, d, tag, out = sys.argv[1:5]
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
DB = [(raw[0x8071958 - B + 2 * i], raw[0x8071958 - B + 2 * i + 1]) for i in range(496)]    # TypedText: indeks WZGLEDNY id -> (czcionka, wyrownanie); tekst = pl(id+57)
trans = []
for line in open(os.path.join(d, tag + ".log"), errors="ignore"):
    m = re.match(r"nowy ekran #(\d+) \(z #(\d+) tap (\d+),(\d+)\)", line)
    if m: trans.append(tuple(int(x) for x in m.groups()))
s = U.UiSession.from_checkpoint(fw, os.path.join(d, "%s_%03d.state" % (tag, trans[0][1])), None); t = C.Tracer(s); res = []
for k, p, x, y in trans:
    try:
        s.b.load_state(os.path.join(d, "%s_%03d.state" % (tag, p))); s.wait(30); t.log.clear(); s.tap(x, y, hold=140, settle=280); s.wait(500)
        ws = C.widget_table(s, t)
    except Exception as e: print("blad", k, e); continue
    for w in ws:
        if w["text_id"] is not None: w["text_pl"] = pl(w["text_id"] + 57); w["font"], w["align"] = DB[w["text_id"]] if w["text_id"] < len(DB) else (None, None)
    title = next((w["wildcard"] or w["text_pl"] for w in sorted(ws, key=lambda w: w["y"]) if w["role"] == "text" and 0 <= w["y"] < 46 and 150 < w["x"] + w["w"] // 2 < 330 and (w["wildcard"] or w.get("text_pl"))), "")
    res.append(dict(node=k, parent=p, tap=[x, y], title=title, widgets=ws, ctor_events=len(t.log))); print(k, repr(title), len(ws), flush=True)
    json.dump(res, open(out, "w"), ensure_ascii=False)
