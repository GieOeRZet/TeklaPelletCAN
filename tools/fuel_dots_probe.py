#!/usr/bin/env python3
"""Ikona paliwa na kafelku HOME: (1) ktore instrukcje firmware czytaja licznik paliwa 0x3601 i pojemnosc 0x3600 (hak odczytu pamieci Unicorn -> PC),
(2) skan 0..N kg: liczba kropek zasobnika (komponenty spojne jasnych pikseli w obszarze ikony) + stan widgetow 51/52. Tylko emulator.
Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/fuel_dots_probe.py OUT.json [CAP=135] [MAX=140]"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths, ui_session as U, ctor_trace as C, ui_extras as X
from unicorn import UC_HOOK_MEM_READ
from unicorn.arm_const import UC_ARM_REG_PC, UC_ARM_REG_LR

out = sys.argv[1]
cap = int(sys.argv[2]) if len(sys.argv) > 2 else 135
mx = int(sys.argv[3]) if len(sys.argv) > 3 else 140
s = U.UiSession(str(paths.FIRMWARE), None); t = C.Tracer(s); s.boot(500)
_cfg = {0x2105: 4, 0x2106: 1, 0x2107: 1, 0x2108: 1, 0x3600: cap}
if os.environ.get("FUEL_RESERVE") is not None: _cfg[0x3603] = int(os.environ["FUEL_RESERVE"])   # rezerwa paliwa (0x3603; domyslnie 40, u wlasciciela 0)
for p_, v_ in _cfg.items():
    s.set_local(p_, v_)
s.set_access(0); s.wait(4500)
ws = C.widget_table(s, t)
st_fuel, ty = s._record(0x3601); st_cap, _ = s._record(0x3600)
readers = {"fuel_0x3601": {}, "cap_0x3600": {}}
def mk(name, lo):
    def h(uc, a, ad, sz, v, ud):
        pc = uc.reg_read(UC_ARM_REG_PC); lr = uc.reg_read(UC_ARM_REG_LR)
        readers[name][hex(pc)] = hex(lr)
    return h
s.b.mu.hook_add(UC_HOOK_MEM_READ, mk("fuel_0x3601", st_fuel), begin=st_fuel, end=st_fuel + 3)
s.b.mu.hook_add(UC_HOOK_MEM_READ, mk("cap_0x3600", st_cap), begin=st_cap, end=st_cap + 3)
vt = None
for w in ws:
    if int(w["this"], 16) == 0x20016998: vt = hex(s.b.rd(0x20016998))
def dots(img):
    a = np.asarray(img.convert("L").crop((86, 220, 120, 258))).astype(int)
    m = a > 150; seen = np.zeros_like(m); n = 0; sizes = []
    for y in range(m.shape[0]):
        for x in range(m.shape[1]):
            if m[y, x] and not seen[y, x]:
                st = [(y, x)]; seen[y, x] = True; c = 0
                while st:
                    yy, xx = st.pop(); c += 1
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = yy + dy, xx + dx
                        if 0 <= ny < m.shape[0] and 0 <= nx < m.shape[1] and m[ny, nx] and not seen[ny, nx]: seen[ny, nx] = True; st.append((ny, nx))
                sizes.append(c)
    return sorted(sizes), int(m.sum())
res = {"capacity_set": cap, "storage": {"fuel": hex(st_fuel), "cap": hex(st_cap)}, "widget_0x20016998_vtable": vt, "scan": {}}
for v in range(0, mx + 1):
    s.inject_param(0x3601, v, 3, 60); s.wait(700)
    img = s.shot(); sizes, area = dots(img)
    ex = X.extract(s, ws)
    h = {k: ex.get(k, {}).get("hidden") for k in ("0x200165e0", "0x2001660c", "0x2001ae70", "0x2001af64", "0x2001ac60", "0x2001af90", "0x2001b2fc")}
    if os.environ.get("FUEL_SHOTS") and v in [int(x) for x in os.environ["FUEL_SHOTS"].split(",")]: img.crop((60, 190, 140, 272)).resize((320, 328)).save("/tmp/w/fuelshot_%d.png" % v)
    res["scan"][str(v)] = dict(components=len(sizes), area=area, sizes=sizes[:30], hidden=h)
    if v % 10 == 0: print(v, len(sizes), area, h, flush=True)
    res["readers"] = readers
    json.dump(res, open(out, "w"), indent=1)
print("READERS", json.dumps(readers, indent=1))
