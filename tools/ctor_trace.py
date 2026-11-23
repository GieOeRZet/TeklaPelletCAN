#!/usr/bin/env python3
"""PASS 57: sledzenie konstrukcji widgetow TouchGFX przez haki na settery (podczas wejscia na ekran):
  0x080413A4 setTypedText(this, id u16 w r1)      0x08040358 setPosition(this, x=r1, y=r2, w=r3, h=[sp])
  0x080407BC setBitmap/Image(this, &id w r1)       0x08040380 add(container=r0, child=r1)       0x0805272C setX(this, r1, r2)  (znaczenie do potwierdzenia)
Log: lista zdarzen (op, this, args). Uzycie: from ctor_trace import Tracer; t = Tracer(session); ...akcja UI...; t.widgets()."""
import struct
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
FUNCS = {0x080413A4: "text", 0x08040358: "pos", 0x080407BC: "bitmap", 0x08040380: "add", 0x0805272C: "f272c", 0x0804079A: "f479a"}
class Tracer:
    def __init__(self, s):
        self.s = s; self.log = []
        for a in FUNCS: s.b.mu.hook_add(UC_HOOK_CODE, self._h, begin=a, end=a)
    def _h(self, uc, a, sz, ud):
        op = FUNCS[a]; r0, r1, r2, r3 = (uc.reg_read(x) for x in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)); sp = uc.reg_read(UC_ARM_REG_SP)
        rd = lambda ad, n=4: int.from_bytes(bytes(uc.mem_read(ad, n)), "little")
        if op == "text": rec = dict(op=op, this=r0, id=r1 & 0xFFFF)
        elif op == "pos": rec = dict(op=op, this=r0, x=r1, y=r2, w=r3, h=rd(sp))
        elif op == "bitmap":
            try: rec = dict(op=op, this=r0, id=rd(r1, 2))
            except Exception: rec = dict(op=op, this=r0, id=None)
        elif op == "add": rec = dict(op=op, this=r0, child=r1)
        else: rec = dict(op=op, this=r0, r1=r1, r2=r2, r3=r3)
        rec["lr"] = uc.reg_read(UC_ARM_REG_LR); rec["tick"] = self.s.n; self.log.append(rec)

def widget_table(s, tracer):
    """z logu konstrukcji + stanu RAM: lista widgetow {this, role(text/image/other), rect(x,y,w,h), parent, vis, touch, text_id, bitmap_id}. Rect/parent/vis z pol Drawable (+4 rect, +0x14 parent, +0x24 touch, +0x25 vis)."""
    ids_t = {}; ids_b = {}; seen = set()
    for r in tracer.log:
        if r["op"] == "text": ids_t[r["this"]] = r["id"]; seen.add(r["this"])
        elif r["op"] == "bitmap" and r["id"] is not None: ids_b[r["this"]] = r["id"]; seen.add(r["this"])
        elif r["op"] in ("pos", "f272c"): seen.add(r["this"])
        elif r["op"] == "add": seen.add(r["this"]); seen.add(r["child"])
    out = []; rd = s.b.rd
    for a in sorted(seen):
        if not (0x20000000 <= a < 0x20030000): continue
        try:
            x, y, w, h = (int.from_bytes(bytes([rd(a + 4 + 2 * i, 1), rd(a + 5 + 2 * i, 1)]), "little", signed=True) for i in range(4))
            out.append(dict(this=hex(a), role="text" if a in ids_t else "image" if a in ids_b else "other", x=x, y=y, w=w, h=h, parent=hex(rd(a + 0x14, 4)), vis=rd(a + 0x25, 1), touch=rd(a + 0x24, 1), text_id=ids_t.get(a), bitmap_id=ids_b.get(a)))
        except Exception: pass
    return out
