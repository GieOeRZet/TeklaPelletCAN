#!/usr/bin/env python3
"""Etap C: wskazniki kafelkow dolnej belki HOME. Dla kazdego PID (shard i/n) wstrzykuje wartosci probne, mierzy (ukryty, id bitmapy +0x26) ikon belki i bitmapy kafelkow,
cofa wartosc i filtruje szum. Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/home_indicators_probe.py OUT.json [i n] [PID ...]. Tylko emulator."""
import csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths, ui_session as U, ctor_trace as C, ui_extras as X
out = sys.argv[1]; sh = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 and sys.argv[2].isdigit() else (0, 1)
N = lambda v: int(str(v), 16)
mm = {N(r["pid"]): (int(r["min"] or 0), int(r["max"] or 0), r["name"]) for r in csv.DictReader(open(paths.DATA / "pid_matrix_655.csv", encoding="utf-8-sig"))}
pids = sorted(mm)[sh[0]::sh[1]]
if len(sys.argv) > 4: pids = [N(x) for x in sys.argv[4:]]
s = U.UiSession(str(paths.FIRMWARE), None); t = C.Tracer(s); s.boot(500)
for p_, v_ in {0x2105: 4, 0x2106: 1, 0x2107: 1, 0x2108: 1}.items(): s.set_local(p_, v_)
s.set_access(0); s.wait(4500)
ws = C.widget_table(s, t); rd = s.b.rd
ICONS = {"palnik_138": 0x20016504, "co1_207": 0x20016530, "co2_276": 0x2001655c, "cwu_345": 0x20016588, "zasilanie_414": 0x200165b4, "paliwo_51": 0x200165e0, "paliwo_52": 0x2001660c}
TILES = {"x0": 0x20016360, "x138": 0x2001639c, "x207": 0x200163d8, "x276": 0x20016414, "x345": 0x20016450, "x69": 0x2001648c, "x414": 0x200164c8}
def sig():
    ex = X.extract(s, ws); r = {}
    for k, a in ICONS.items(): r[k] = (ex.get("0x%x" % a, {}).get("hidden"), rd(a + 0x26, 2))
    for k, a in TILES.items(): r["tile_" + k] = (ex.get("0x%x" % a, {}).get("hidden"), ex.get("0x%x" % a, {}).get("bmp"))
    return r
def old(pid):
    r = s._record(pid); n = {1: 1, 2: 2, 3: 4, 4: 2, 5: 4}[r[1]]; return rd(r[0], n)
s.wait(600); base = sig(); s.wait(600); b2 = sig(); noise = {k for k in base if base[k] != b2[k]}; base = b2
res = {"noise": sorted(noise), "base": {k: list(v) for k, v in base.items()}, "effects": []}
for pid in pids:
    if s._record(pid) is None: continue
    lo, hi, nm = mm[pid]; vals = sorted({v for v in (lo, 1, 2, 3, 5, 10, (lo + hi) // 2, hi) if lo <= v <= hi}) if hi > lo else [1]
    o = old(pid)
    for v in vals:
        try: s.inject_param(pid, v, 3, 60); s.wait(900); c = sig()
        except Exception as e: print("ERR", hex(pid), repr(e)[:60], flush=True); break
        d = {k: [list(base[k]), list(c[k])] for k in c if c[k] != base[k] and k not in noise}
        if d: res["effects"].append(dict(pid="0x%04X" % pid, name=nm, value=v, changed=d)); print("0x%04X" % pid, nm[:30], v, {k: (x[0][1], x[1][1], x[0][0], x[1][0]) for k, x in d.items()}, flush=True)
    s.inject_param(pid, o, 3, 60); s.wait(700)
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
json.dump(res, open(out, "w"), ensure_ascii=False, indent=1); print("DONE", len(res["effects"]), "efektow")
