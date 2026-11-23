#!/usr/bin/env python3
"""PASS 67: dane dodatkowe widgetow dla renderera (kolory, teksty) odczytane z RAM punktu kontrolnego wezla:
ui_extras.py FW DIR INV.json OUTDIR PREFIX [wezly...]  -> OUTDIR/PREFIX_<wezel>.json {this: {cls, box, alpha, text, color, font, align}}
Klasy po vptr: TextArea (0x807e15c, 0x807e1d8: id +0x26, kolor +0x2C, bufor wildcard +0x34), Label (0x807e7f8: id +0x34, kolor +0x38), Box (0x807f24c: kolor +0x28, alfa +0x26)."""
import csv, json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, action_probe as AP
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analiza", "FW2213TK-2026-11-22", "data")
TT = {int(r["typedtext_id_relative"]): r for r in csv.DictReader(open(os.path.join(D, "typedtext_database.csv"), encoding="utf-8"))}
TEXTA, LABEL, BOX = (0x807e15c, 0x807e1d8), (0x807e7f8,), (0x807f24c,)
def wc(rd, bp):
    if not (0x20000000 <= bp < 0x2002FFC0): return ""
    out = []
    for i in range(64):
        c = rd(bp + 2 * i, 2)
        if c == 0: break
        out.append(chr(c))
    return "".join(out)
def extract(s, widgets):
    rd = s.b.rd; ex = {}
    for w in widgets:
        a = int(w["this"], 16); v = rd(a); e = None
        if v in TEXTA: tid, col, bp = rd(a + 0x26, 2), rd(a + 0x2C, 2), rd(a + 0x34)
        elif v in LABEL: tid, col, bp = rd(a + 0x34, 2), rd(a + 0x38, 2), 0
        elif v in BOX: ex[w["this"]] = dict(cls="box", box=rd(a + 0x28, 2), alpha=rd(a + 0x26, 1)); continue
        else: continue
        t = TT.get(tid)
        if t is None: continue
        ex[w["this"]] = dict(cls="text", color=col, text=t["pl_text"].replace("\\x02", "\x02").replace("\x02", wc(rd, bp)), font=int(t["font_index"]), align=int(t["align(0=left,1=center,2=right)"]), tid=tid)
    return ex
if __name__ == "__main__":
    fw, d, invp, out, prefix = sys.argv[1:6]; inv = {n["node"]: n for n in json.load(open(invp))}; nodes = sys.argv[6:] or list(inv)
    os.makedirs(out, exist_ok=True); s = U.UiSession.from_checkpoint(fw, os.path.join(d, "menu.state"), None); rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb"))
    for n in nodes:
        try:
            st = AP.enter_node(s, d, rows, n); s.b.load_state(st); s.wait(250); ex = extract(s, inv[n]["widgets"])
            json.dump(ex, open(os.path.join(out, "%s_%s.json" % (prefix, n)), "w"), ensure_ascii=False); print(n, len(ex), flush=True)
        except Exception as e: print(n, "ERR", repr(e)[:80], flush=True)
