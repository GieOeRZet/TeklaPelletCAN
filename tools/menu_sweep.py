#!/usr/bin/env python3
"""PASS 65 etap 2: ktore wiersze menu istnieja przy danej konfiguracji i poziomie dostepu (wiersze rozpoznawane po ikonie A z menu_rows_21.csv,
rejestrowanej przy konstrukcji menu). Uzycie: menu_sweep.py FW.bin OUT.json  (maks. 3 procesy -> uzyj --part i --parts)"""
import csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, ctor_trace as C
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analiza", "FW2213TK-2026-11-22", "data")
A2ROW = {int(r["bitmap_A"]): int(r["row"]) for r in csv.DictReader(open(os.path.join(D, "menu_rows_21.csv")))}
FULL = {0x2105: 4, 0x2106: 1, 0x2107: 1, 0x2108: 1, 0x350C: 0, 0x3525: 0}
def variants():
    out = []
    for lvl in (0, 1, 2, 3):
        out.append(("FULL", lvl, dict(FULL)))
        out.append(("DEFAULT", lvl, {0x2105: 1, 0x2106: 0, 0x2107: 0, 0x2108: 0, 0x350C: 0, 0x3525: 0}))
    for lvl in (0, 1):
        for n in (0, 1, 2, 3): out.append(("2105=%d" % n, lvl, {**FULL, 0x2105: n}))
        for p in (0x2106, 0x2107, 0x2108): out.append(("%#x=0" % p, lvl, {**FULL, p: 0}))
        out.append(("350C=1", lvl, {**FULL, 0x350C: 1})); out.append(("3525=1", lvl, {**FULL, 0x3525: 1}))
        out.append(("350C=1,3525=1", lvl, {**FULL, 0x350C: 1, 0x3525: 1}))
    for lvl in (2, 3): out.append(("350C=1,3525=1", lvl, {**FULL, 0x350C: 1, 0x3525: 1}))
    return out
def run(fw, part, parts, outp):
    from unicorn import UC_HOOK_CODE
    from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1
    res = json.load(open(outp)) if os.path.exists(outp) else {}
    for i, (name, lvl, cfg) in enumerate(variants()):
        key = "%s|L%d" % (name, lvl)
        if i % parts != part or key in res: continue
        s = U.UiSession(fw, None); s.boot(500); log = []
        def h(uc, a, sz, ud): log.append((uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_R1)))
        s.b.mu.hook_add(UC_HOOK_CODE, h, begin=0x0805BC6C, end=0x0805BC6C)       # konstruktor wiersza menu (A = bitmapa ikony), hak dodany PRZED uruchomieniem
        for pid, v in cfg.items(): s.set_local(pid, v)
        s.set_access(lvl); s.wait(300); log.clear(); s.tap(34, 235, settle=700); s.wait(300)
        rd = s.b.rd; seen = {}
        for obj, a_ in log: seen[a_] = obj
        rows = sorted(A2ROW[a_] for a_, o in seen.items() if a_ in A2ROW and rd(o + 0x14) != 0)      # wiersz ukryty konfiguracja/poziomem = nie dodany do kontenera (parent == 0)
        built = sorted(A2ROW[a_] for a_ in seen if a_ in A2ROW)
        res[key] = dict(level=lvl, config={hex(k): v for k, v in cfg.items()}, rows_visible=rows, rows_built=built, view_vptr=hex(rd(rd(0x20024818))))
        json.dump(res, open(outp, "w"), indent=1); print(key, "visible", rows, "built", len(built), flush=True)
if __name__ == "__main__":
    run(sys.argv[1], int(sys.argv[3]) if len(sys.argv) > 3 else 0, int(sys.argv[4]) if len(sys.argv) > 4 else 1, sys.argv[2])
