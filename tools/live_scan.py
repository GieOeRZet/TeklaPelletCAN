#!/usr/bin/env python3
"""PASS 70: skan zrodel LIVE: dla modulu CAN IO (node) i kazdego z 12 kanalow analogowych podaje surowa wartosc przez ramki PDO (LiveSim, pojedynczo z odstepem)
i zapisuje, ktore PID-y zmieniaja sie wzgledem przebiegu bazowego (wszystkie kanaly 1000). Tylko odczyt/wstrzykniecie na emulatorze (nie dotyka kotla).
live_scan.py FW DIR OUT.json NODE [--chan 0 1 ..] [--vals 500 2000 3000] [--set PID=VAL ...]   (--set: wstepna konfiguracja przez inject_param)"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, action_probe as AP, live_sim as L
ap = argparse.ArgumentParser(); ap.add_argument("fw"); ap.add_argument("dir"); ap.add_argument("out"); ap.add_argument("node")
ap.add_argument("--chan", nargs="*", type=int, default=list(range(12))); ap.add_argument("--vals", nargs="*", type=int, default=[500, 2000, 3000])
ap.add_argument("--set", nargs="*", default=[]); a = ap.parse_args()
node = int(a.node, 16); BG = {0x3726, 0x2311, 0x2312, 0x2313, 0x2314, 0x2167, 0x229A}
s = U.UiSession.from_checkpoint(a.fw, os.path.join(a.dir, "menu.state"), None); s.wait(4500)
for kv in a.set:
    p, v = kv.split("="); s.inject_param(int(p, 16), int(v, 0))
s.wait(300); base = os.path.join(os.path.dirname(a.out) or ".", "scanbase_%s.state" % a.node); s.checkpoint(base)
sim = L.LiveSim(s); sim.raw.setdefault(node, [1000] * 12); recs = AP.pid_records(s)
def run(ch, v):
    s.b.load_state(base); sim.raw = {n: [1000] * 12 for n in set(sim.raw) | {node}}
    if ch is not None: sim.raw[node][ch] = v
    sim.run(800, nodes=(node,)); s.wait(200); return AP.pid_snap(s, recs)
b0 = run(None, 0); res = json.load(open(a.out)) if os.path.exists(a.out) else {}
res.setdefault("node", a.node); res.setdefault("chan", {})
for ch in a.chan:
    if str(ch) in res["chan"]: continue
    out = {}
    for v in a.vals:
        sn = run(ch, v)
        for p in sn:
            if p not in BG and sn[p] != b0.get(p): out.setdefault("0x%04X" % p, {})[v] = [b0.get(p), sn[p]]
    res["chan"][str(ch)] = out; json.dump(res, open(a.out, "w"), indent=1)
    print(ch, {k: [x[1] for x in v.values()] for k, v in out.items()}, flush=True)
