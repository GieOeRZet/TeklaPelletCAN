#!/usr/bin/env python3
"""PASS 65: jak ui_explore.py --prepare, ale z dowolna konfiguracja i poziomem: ui_prepare_cfg.py FW OUT LEVEL [0xPID=wartosc ...]
Domyslnie jak ui_explore (0x2105=4, 0x2106..0x2108=1); podane PID-y nadpisuja. Wynik: OUT/menu.state, rows.pkl, menu_tall.png, rows.txt"""
import os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, ui_explore as X
fw, out, level = sys.argv[1], sys.argv[2], int(sys.argv[3])
cfg = {0x2105: 4, 0x2106: 1, 0x2107: 1, 0x2108: 1}
for a in sys.argv[4:]:
    k, v = a.split("="); cfg[int(k, 16)] = int(v)
os.makedirs(out, exist_ok=True)
s = U.UiSession(fw, out); s.boot(500); s.enable_trace()
for pid, v in cfg.items(): s.set_local(pid, v)
s.set_access(level); s.wait(300); s.shot("home"); s.tap(34, 235, settle=700); s.go_top()
s.checkpoint(os.path.join(out, "menu.state"))
nav = U.ListNav(s); rows = nav.build(); nav.tall.save(os.path.join(out, "menu_tall.png"))
with open(os.path.join(out, "rows.txt"), "w") as f:
    for r in rows: f.write("%d %s cy=%d chevron=%d\n" % (r["idx"], X.name(r["idx"]), r["cy"], r["chevron"]))
pickle.dump(rows, open(os.path.join(out, "rows.pkl"), "wb")); print("rows", len(rows))
