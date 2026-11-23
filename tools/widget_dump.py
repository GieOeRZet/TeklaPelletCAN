#!/usr/bin/env python3
"""PASS 55: inwentarz widgetow ekranu: skan obiektow TouchGFX (Drawable) w SRAM wczytanego stanu emulatora.
Drawable (zweryfikowane): +0 vptr, +4 rect {x,y,w,h : int16}, +0xC drugi rect, +0x14 parent*, +0x18 nextSibling*, +0x24 touchable (u8), +0x25 visible (u8), +0x26 bitmap/TypedText id (u16).
Aktywny widok = *(0x20024818), kontener = widok+4. Buduje drzewo rodzic->dzieci, liczy wspolrzedne bezwzgledne, wypisuje widoczne widgety (typ po vptr: Image 0x0807F1E0, TextArea 0x0807E15C, inne = vptr).
python3 -I tools/widget_dump.py FW.bin STATE OUT.json [--all]"""
import json, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U
KNOWN = {0x0807F1E0: "Image", 0x0807E15C: "TextArea"}
def dump(s, allw=False):
    mem = bytes(s.b.mu.mem_read(0x20000000, 0x30000)); ru = lambda o, n=4: int.from_bytes(mem[o:o + n], "little")
    objs = {}
    for o in range(0, 0x30000 - 0x40, 4):
        v = ru(o)
        if not (0x08070000 <= v < 0x08090000): continue
        x, y, w, h = struct.unpack_from("<hhhh", mem, o + 4); par = ru(o + 0x14); nxt = ru(o + 0x18)
        if not (0 < w <= 480 and 0 < h <= 272 and -480 <= x <= 480 and -272 <= y <= 544): continue
        if par and not (0x20000000 <= par < 0x20030000): continue
        if nxt and not (0x20000000 <= nxt < 0x20030000): continue
        objs[0x20000000 + o] = dict(addr=0x20000000 + o, vptr=v, x=x, y=y, w=w, h=h, parent=par, vis=mem[o + 0x25], touch=mem[o + 0x24], id=ru(o + 0x26, 2))
    kids = {}
    for a, d in objs.items():
        if d["parent"] in objs: kids.setdefault(d["parent"], []).append(a)
    def absxy(a):
        x = y = 0; seen = 0
        while a in objs and seen < 20:
            x += objs[a]["x"]; y += objs[a]["y"]; a = objs[a]["parent"]; seen += 1
        return x, y
    def visible(a):
        seen = 0
        while a in objs and seen < 20:
            if not objs[a]["vis"]: return False
            a = objs[a]["parent"]; seen += 1
        return True
    cur = int.from_bytes(mem[0x24818:0x2481C], "little")                    # 0x20024818 = wskaznik aktywnego widoku; kontener glowny = widok+4
    root = cur + 4 if cur else 0
    def under_root(a):
        seen = 0
        while a in objs and seen < 30:
            if a == root: return True
            a = objs[a]["parent"]; seen += 1
        return False
    out = []
    for a, d in sorted(objs.items()):
        if root in objs and not under_root(a): continue                  # tylko widgety aktywnego ekranu
        if d["parent"] not in objs and not kids.get(a) and a != root: continue          # pomijamy sieroty bez dzieci i bez rodzica
        ax, ay = absxy(a)
        if not allw and not visible(a): continue
        if ax + d["w"] <= 0 or ay + d["h"] <= 0 or ax >= 480 or ay >= 272: continue
        out.append(dict(addr=hex(a), type=KNOWN.get(d["vptr"], hex(d["vptr"])), x=ax, y=ay, w=d["w"], h=d["h"], id=d["id"], touch=d["touch"], children=len(kids.get(a, [])), parent=hex(d["parent"]) if d["parent"] else ""))
    return out
if __name__ == "__main__":
    fw, st, dst = sys.argv[1:4]
    s = U.UiSession.from_checkpoint(fw, st, None); s.wait(60)
    w = dump(s, "--all" in sys.argv); json.dump(w, open(dst, "w"), indent=1); print(len(w), "widgetow")
