#!/usr/bin/env python3
"""PASS 66: atlas zrzutow ekranow (wzorzec dla renderera): atlas_build.py FW DIR INV.json OUTDIR PREFIX [wezly...]
Dla kazdego wezla wchodzi (action_probe.enter_node: punkt kontrolny wezla), odczekuje i zapisuje PNG OUTDIR/PREFIX_<wezel>.png"""
import json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, action_probe as AP
fw, d, invp, out, prefix = sys.argv[1:6]; nodes = sys.argv[6:] or [n["node"] for n in json.load(open(invp))]
os.makedirs(out, exist_ok=True)
s = U.UiSession.from_checkpoint(fw, os.path.join(d, "menu.state"), None); rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb"))
for n in nodes:
    try:
        st = AP.enter_node(s, d, rows, n); s.b.load_state(st); s.wait(250)
        s.shot().save(os.path.join(out, "%s_%s.png" % (prefix, n))); print(n, hex(s.b.rd(s.b.rd(AP.VIEW))), flush=True)
    except Exception as e: print(n, "ERR", repr(e)[:60], flush=True)
