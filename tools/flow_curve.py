#!/usr/bin/env python3
"""PASS 70: krzywa przepływomierza (PDO1 0x180+0x54, bajty 6-7 -> PID 0x371A): surowy u16 -> wartosc PID. Wyjscie OUT.json (wznawialne).
Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/flow_curve.py FW STATE OUT.json [start stop step]"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, action_probe as AP
fw, state, out = sys.argv[1:4]; lo, hi, step = (int(x) for x in sys.argv[4:7]) if len(sys.argv) > 6 else (0, 4100, 25)
s = U.UiSession.from_checkpoint(fw, state, None); s.wait(4500)
for p, v in ((0x362B, 1),): s.inject_param(p, v)
s.wait(300); st = out + ".state"; s.checkpoint(st); recs = {p: a for p, a, n in AP.pid_records(s)}
res = json.load(open(out)) if os.path.exists(out) else {}
for raw in range(lo, hi, step):
    if str(raw) in res: continue
    s.b.load_state(st)
    for _ in range(12): s.can(0x180 + 0x54, bytes([0, 0, 0, 0, 0, 0, raw & 255, raw >> 8])); s.wait(12); s.wait(40)
    s.wait(200); res[str(raw)] = s.b.rd(recs[0x371A], 2); json.dump(res, open(out, "w"))
print("done", len(res))
