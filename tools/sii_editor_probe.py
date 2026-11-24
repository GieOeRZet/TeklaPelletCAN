#!/usr/bin/env python3
"""PASS 70: edytor tekstowy INTERNET (klawiatura 'rolkowa'): tap SSID -> sekwencja stukniec, po kazdej: zrzut ciala, vtable, nowe ramki 0x584.
Uzycie: sii_editor_probe.py FW STATE_18 OUT"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U
from PIL import Image
FW, ST, OUT = sys.argv[1:4]; os.makedirs(OUT, exist_ok=True)
s = U.UiSession.from_checkpoint(FW, ST, None); s.wait(300)
SEQ = [("tap_SSID", 180, 62), ("up", 287, 170), ("up", 287, 170), ("down", 336, 170), ("ABC", 285, 209), ("abc", 336, 209), ("num", 386, 209), ("sym", 436, 209), ("up", 287, 170), ("OK", 386, 170)]
ims = []; log = []
for name, x, y in SEQ:
    n0 = len(s.can2.tx); s.tap(x, y, settle=700); im = s.shot(); ims.append(im.crop((0, 46, 480, 272)))
    log.append(dict(step=name, tap=[x, y], view=hex(s.b.rd(s.b.rd(0x20024818))), tx584=[bytes(f["data"]).hex() for f in s.can2.tx[n0:] if f["id"] == 0x584 and int.from_bytes(bytes(f["data"])[1:3], "little") not in (0x2167, 0x229A, 0x3723)]))
    print(log[-1], flush=True)
W, H = ims[0].size; m = Image.new("RGB", (W * 2, H * ((len(ims) + 1) // 2)))
for i, im in enumerate(ims): m.paste(im, ((i % 2) * W, (i // 2) * H))
m.save(os.path.join(OUT, "editor_seq.png")); json.dump(log, open(os.path.join(OUT, "editor_seq.json"), "w"), indent=1)
