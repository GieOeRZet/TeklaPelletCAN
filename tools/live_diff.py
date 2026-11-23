#!/usr/bin/env python3
"""PASS 67: wiazania PID LIVE (zrodla modulowe) metoda roznicowa: dla wezla wczytuje punkt kontrolny, karmi moduly CAN IO (LiveSim) typowymi temperaturami i zmienia JEDEN PID
(0x2001 itd.) przez ramki PDO; odczytuje stan widgetow jak pid_diff. Wynik w formacie pid_diff (pid_diff_report.py).
live_diff.py FW DIR INV NODE OUT.json [--pids 0x2001 ...] [--temps 10 40 65 90]"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, action_probe as AP, pid_diff as P, live_sim as L
ap = argparse.ArgumentParser(); ap.add_argument("fw"); ap.add_argument("dir"); ap.add_argument("inv"); ap.add_argument("node"); ap.add_argument("out")
ap.add_argument("--pids", nargs="*"); ap.add_argument("--temps", nargs="*", type=float, default=[10, 40, 65, 90]); a = ap.parse_args()
inv = {n["node"]: n for n in json.load(open(a.inv))}[a.node]; ws = P.good_widgets(inv); meta = P.pid_meta()
s = U.UiSession.from_checkpoint(a.fw, os.path.join(a.dir, "menu.state"), None); rows = __import__("pickle").load(open(os.path.join(a.dir, "rows.pkl"), "rb"))
st = AP.enter_node(s, a.dir, rows, a.node); sim = L.LiveSim(s)
pids = [int(p, 16) for p in a.pids] if a.pids else sorted(sim.where)
def settle(vals):
    s.b.load_state(st)
    for pid, t in vals.items(): sim.set(pid, t)
    sim.run(700); s.wait(200)
base_t = {pid: 40.0 for pid in sim.where}; res = dict(node=a.node, widgets=ws, control=None, pids={}); settle(base_t); res["control"] = P.read_state(s, ws)
for pid in pids:
    runs = []
    for t in a.temps:
        sim.raw = {n: [1000] * 12 for n in sim.raw}; settle({**base_t, pid: t}); runs.append(dict(value=int(round(t * 10)), stored=s.b.rd(s._record(pid)[0], 2), view_vptr=hex(s.b.rd(s.b.rd(AP.VIEW))), state=P.read_state(s, ws), shot=None))
    m = meta.get(pid, {}); res["pids"]["0x%04X" % pid] = dict(name=m.get("name", "?"), type=m.get("type", ""), min=m.get("min", ""), max=m.get("max", ""), runs=runs)
    print("0x%04X" % pid, [r["stored"] for r in runs], flush=True); json.dump(res, open(a.out, "w"), ensure_ascii=False)
