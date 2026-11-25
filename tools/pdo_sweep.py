#!/usr/bin/env python3
"""Kanal stanow od sterownika (wezel 4): przeszukanie ramek PDO 0x184/0x284/0x384/0x484 (8 bajtow) - dla kazdego bajtu wartosc 0xFF (potem 0x01),
pomiar zmian na ekranie (roznica pikseli + zmiany widgetow). Cel: zrodlo stanu palnika (diody), wyjsc (ikony dolnych belek), liczb nad ikonami.
Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/pdo_sweep.py SCREEN OUT.json     SCREEN = HOME | PALNIK | KOCIOL   (HOME bez nawigacji; reszta z /tmp/w/L3 wiersz menu)
Tylko emulator."""
import json, os, pickle, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths, ui_session as U, ctor_trace as C, ui_extras as X, ui_nav
from PIL import Image
scr, out = sys.argv[1:3]
ROW = {"PALNIK": 1, "KOCIOL": 0, "OGRZEWANIE1": 2, "CWU": 6}
if scr == "HOME":
    s = U.UiSession(str(paths.FIRMWARE), None); t = C.Tracer(s); s.boot(500)
    for p_, v_ in {0x2105: 4, 0x2106: 1, 0x2107: 1, 0x2108: 1}.items(): s.set_local(p_, v_)
    s.set_access(0); s.wait(4500)
else:
    d = "/tmp/w/L3"
    s = U.UiSession.from_checkpoint(str(paths.FIRMWARE), os.path.join(d, "menu.state"), None); s.wait(120)
    nav = U.ListNav(s); nav.tall = Image.open(os.path.join(d, "menu_tall.png")); nav.rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb")); t = C.Tracer(s); t.log.clear()
    assert ui_nav.tap_incremental(s, nav, ROW[scr]); s.wait(1500)
ws = C.widget_table(s, t)
def frame(cid, data, rounds=10):
    for _ in range(rounds):
        s.can(cid, data); s.wait(12)
def snap():
    ex = X.extract(s, ws); st = {k: (v.get("hidden"), v.get("text") if v.get("cls") == "text" else v.get("bmp")) for k, v in ex.items()}
    return np.asarray(s.shot().convert("L")).astype(int), st
s.wait(600)
for node in (4,):                      # heartbeat sterownika (operational), zeby panel uznal wezel za obecny
    s.can(0x700 + node, [5]); s.wait(12)
frame(0x184, [0] * 8, 6); s.wait(300); base_img, base_st = snap()
res = {"screen": scr, "trials": []}
for cid in (0x184, 0x284, 0x384, 0x484):
    for byte in range(8):
        for val in (0xFF, 0x01):
            data = [0] * 8; data[byte] = val
            frame(cid, data, 10); s.wait(400); img, st = snap()
            diff = np.abs(img - base_img); diff[:40, :] = 0            # pomijamy naglowek (zegar)
            ch = {k: [base_st.get(k), st.get(k)] for k in st if st.get(k) != base_st.get(k)}
            n_px = int((diff > 40).sum())
            if n_px > 30 or ch:
                ys, xs = np.where(diff > 40)
                res["trials"].append(dict(cob="0x%X" % cid, byte=byte, val=val, px=n_px, bbox=[int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if n_px else None, widgets=ch))
                print(hex(cid), byte, hex(val), n_px, (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())) if n_px else None, len(ch), flush=True)
            frame(cid, [0] * 8, 8); s.wait(300)
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
json.dump(res, open(out, "w"), ensure_ascii=False, indent=1); print("DONE", len(res["trials"]))
