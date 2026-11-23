#!/usr/bin/env python3
"""PASS 65: inwentarz widgetow EKRANU GLOWNEGO + punkt kontrolny: home_inventory.py FW OUTDIR INV.json [0xPID=wartosc ...]
Zapisuje OUTDIR/node_home.state (punkt kontrolny jak wezly action_probe/pid_diff; skopiuj do niego rows.pkl + menu.state z ui_explore --prepare) i INV.json z wezlem 'home'."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, ctor_trace as C
fw, out, invp = sys.argv[1:4]; cfg = {0x2105: 4, 0x2106: 1, 0x2107: 1, 0x2108: 1}
for a in sys.argv[4:]:
    k, v = a.split("="); cfg[int(k, 16)] = int(v)
s = U.UiSession(fw, out); t = C.Tracer(s); s.boot(500)
for p, v in cfg.items(): s.set_local(p, v)
s.set_access(0); s.wait(4500); ws = C.widget_table(s, t); s.shot("home")
s.checkpoint(os.path.join(out, "node_home.state"))
json.dump([dict(node="home", widgets=ws)], open(invp, "w")); print(len(ws), "widgetow; vptr", hex(s.b.rd(s.b.rd(0x20024818))))
