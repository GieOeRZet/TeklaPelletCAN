#!/usr/bin/env python3
"""PASS 67: dane dodatkowe widgetow dla renderera (kolory, teksty) odczytane z RAM punktu kontrolnego wezla:
ui_extras.py FW DIR INV.json OUTDIR PREFIX [wezly...]  -> OUTDIR/PREFIX_<wezel>.json {this: {cls, box, alpha, text, color, font, align}}
Klasy po vptr: TextArea (0x807e15c, 0x807e1d8: id +0x26, kolor +0x2C, bufor wildcard +0x34), Label (0x807e7f8: id +0x34, kolor +0x38), Box (0x807f24c: kolor +0x28, alfa +0x26)."""
import csv, json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, action_probe as AP
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analiza", "FW2213TK-2026-11-22", "data")
TT = {int(r["typedtext_id_relative"]): r for r in csv.DictReader(open(os.path.join(D, "typedtext_database.csv"), encoding="utf-8"))}
TEXTA, LABEL, BOX = (0x807e15c, 0x807e1d8, 0x807ddd8), (0x807e7f8,), (0x807f24c,)
import collections
_BM = collections.defaultdict(list)
for _r in csv.DictReader(open(os.path.join(D, "bitmaps", "manifest.csv"))): _BM[(int(_r["width"]), int(_r["height"]))].append(int(_r["id"]))
def wc(rd, bp):
    if not (0x20000000 <= bp < 0x2002FFC0): return ""
    out = []
    for i in range(400):
        c = rd(bp + 2 * i, 2)
        if c == 0: break
        out.append(chr(c))
    return "".join(out)
def evis(rd, a, root):
    """efektywna widocznosc z RAM biezacego punktu kontrolnego: wszyscy przodkowie (+0x14) maja vis (+0x25) == 1 ORAZ lancuch konczy sie w korzeniu biezacego widoku
    (obiekty osierocone z poprzednich ekranow, parent == 0, nie naleza do sceny)"""
    for _ in range(24):
        if a == root: return rd(a + 0x25, 1) == 1
        if not (0x20000000 <= a < 0x20030000): return False
        if rd(a + 0x25, 1) != 1: return False
        a = rd(a + 0x14)
    return False
def extract(s, widgets):
    rd = s.b.rd; ex = {}; root = rd(0x20024818) + 4
    for w in widgets:
        a = int(w["this"], 16); v = rd(a); e = None
        hidden = not evis(rd, a, root)
        if v in TEXTA: tid, col, bp = rd(a + 0x26, 2), rd(a + 0x2C, 2), rd(a + 0x34)
        elif v in LABEL: tid, col, bp = rd(a + 0x34, 2), rd(a + 0x38, 2), 0
        elif w["role"] == "image":
            ex[w["this"]] = dict(cls="image", hidden=hidden); continue
        elif v in BOX: ex[w["this"]] = dict(cls="box", box=rd(a + 0x28, 2), alpha=rd(a + 0x26, 1), hidden=hidden); continue
        else:
            cand = _BM.get((w["w"], w["h"]))                       # widget-przycisk/panel oparty na bitmapie: pole z id bitmapy (pierwszy kandydat = stan nienaciśniety)
            if cand and w["role"] == "other" and w["w"] > 20 and w["h"] > 20:
                for off in range(0x20, 0x70, 2):
                    if rd(a + off, 2) in cand:
                        ex[w["this"]] = dict(cls="btn", bmp=rd(a + off, 2), off=off, vptr=hex(v), hidden=hidden)
                        ic = rd(a + off + 6, 2); sx = lambda q: q - 65536 if q > 32767 else q          # przycisk z ikona (TouchGFX ButtonWithIcon): id ikony +0x34, iconX +0x38, iconY +0x3A (przy off=0x2E)
                        if 0 < ic < 188 and ic != rd(a + off, 2) and ic != rd(a + off + 2, 2): ex[w["this"]].update(icon=ic, icon_xy=[sx(rd(a + off + 10, 2)), sx(rd(a + off + 12, 2))])
                        break
            else: ex[w["this"]] = dict(cls="other", hidden=hidden)
            continue
        t = TT.get(tid)
        if t is None: continue
        ex[w["this"]] = dict(cls="text", hidden=hidden, color=col, text=t["pl_text"].replace("\\x02", "\x02").replace("\x02", wc(rd, bp)), font=int(t["font_index"]), align=int(t["align(0=left,1=center,2=right)"]), tid=tid)
    # kolejnosc rysowania (z-order): drzewo kontenerow; rodzic +0x14, nastepny brat +0x18, poprzedni brat +0x1C; DFS: widget, potem jego dzieci w kolejnosci rodzenstwa
    addrs = {int(w["this"], 16) for w in widgets}; kids = collections.defaultdict(list)
    for w in widgets: kids[rd(int(w["this"], 16) + 0x14)].append(int(w["this"], 16))
    def chain(group):
        gs = set(group); heads = [x for x in group if rd(x + 0x1C) not in gs]; out = []; seen = set()
        for h in (heads or group[:1]):
            c = h
            while c in gs and c not in seen: seen.add(c); out.append(c); c = rd(c + 0x18)
        out += [x for x in group if x not in seen]; return out
    order = []
    def dfs(a):
        order.append(a)
        for c in chain(kids.get(a, [])): dfs(c)
    roots = [x for x in addrs if rd(x + 0x14) not in addrs]
    for r in chain(roots): dfs(r)
    for i, a in enumerate(order):
        k = "0x%x" % a; ex.setdefault(k, {})["z"] = i
    return ex
if __name__ == "__main__":
    fw, d, invp, out, prefix = sys.argv[1:6]; inv = {n["node"]: n for n in json.load(open(invp))}; nodes = sys.argv[6:] or list(inv)
    os.makedirs(out, exist_ok=True); s = U.UiSession.from_checkpoint(fw, os.path.join(d, "menu.state"), None); rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb"))
    for n in nodes:
        try:
            st = AP.enter_node(s, d, rows, n); s.b.load_state(st); s.wait(250); ex = extract(s, inv[n]["widgets"])
            json.dump(ex, open(os.path.join(out, "%s_%s.json" % (prefix, n)), "w"), ensure_ascii=False); print(n, len(ex), flush=True)
        except Exception as e: print(n, "ERR", repr(e)[:80], flush=True)
