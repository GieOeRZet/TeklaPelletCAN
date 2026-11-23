#!/usr/bin/env python3
"""PASS 52: pokrycie funkcji dla rozruchu + ekranu glownego + okna power + dialogow + historii alarmow (czesc nieobjeta tools/gate_trace.py).
python3 -I tools/coverage_boot.py FW.bin OUTDIR   -> OUTDIR/cov_boot.json"""
import os, sys, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U
from unicorn import UC_HOOK_BLOCK
fw, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
s = U.UiSession(fw, out, rtc_start=datetime.datetime(2026, 11, 23, 14, 35, 0)); cov = set()
s.b.mu.hook_add(UC_HOOK_BLOCK, lambda uc, a, sz, ud: cov.add(a), begin=0x08010000, end=0x080A0000)
s.boot(700)
for pid, v in ((0x2105, 4), (0x2106, 1), (0x2107, 1), (0x2108, 1)): s.set_local(pid, v)
s.set_access(3); s.wait(400)
s.tap(448, 240, settle=600); s.tap(430, 230, settle=500)            # kafelek power, OK
s.tap(100, 240, settle=700); s.tap(240, 250, settle=400)            # kafelek paliwo (dialog), zamkniecie
s.tap(380, 75, settle=700); s.tap(240, 250, settle=400)             # kafelek AUTO / tryb
s.tap(34, 235, settle=700)                                          # MENU
json.dump(sorted(cov), open(os.path.join(out, "cov_boot.json"), "w")); print("boot cov blocks", len(cov))
