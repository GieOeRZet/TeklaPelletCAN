#!/usr/bin/env python3
"""PASS 48: sledzi wejscia do 17 wrapperow z bramka 'poziom>=3' (dodajacych dziecko +0x23C) podczas eksploracji ekranow.
Uzycie: gate_trace.py FW.bin OUTDIR LEVEL ROW_IDX [gear]   (OUTDIR z menu.state/rows.pkl z ui_explore --prepare)
Zapisuje OUTDIR/gate_<nazwa>.json: lista trafien {wrapper, lr, this, ctx12A/B/C, access, t23c_id, t23c_word24}."""
import os, sys, json, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, ui_explore as E
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_LR
WRAPPERS = [0x0805A510,0x0805A9EC,0x0805B1D4,0x0805C104,0x0805E9DC,0x0805F400,0x0805F744,0x0805FE9C,0x0806019C,0x08060458,0x08060714,0x08060A28,0x08060CE4,0x08060FA0,0x0806125C,0x08061518,0x0806FAB4]
CTXPTR = 0x20024814
def install(s, hits):
    b = s.b
    def h(uc, a, sz, ud):
        this = uc.reg_read(UC_ARM_REG_R0); ctx = b.rd(CTXPTR, 4)
        o = this + 0x23C
        hits.append(dict(wrapper=hex(a), lr=hex(uc.reg_read(UC_ARM_REG_LR)), this=hex(this), ctx12A=b.rd(ctx + 0x12A, 1), ctx12B=b.rd(ctx + 0x12B, 1), ctx12C=b.rd(ctx + 0x12C, 1),
                         access=b.rd(ctx + 0x158, 1), t23c_vptr=hex(b.rd(o, 4)), t23c_id=b.rd(o + 0x26, 2), t23c_word24=hex(b.rd(o + 0x24, 4)), tick=s.n))
    for w in WRAPPERS: b.mu.hook_add(UC_HOOK_CODE, h, begin=w, end=w)
if __name__ == "__main__":
    fw, out, level, idx = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]); gear = len(sys.argv) > 5 and sys.argv[5] == "gear"
    rows = pickle.load(open(os.path.join(out, "rows.pkl"), "rb")); nm = E.name(idx)
    s = U.UiSession.from_checkpoint(fw, os.path.join(out, "menu.state"), out); hits = []; install(s, hits); s.wait(120)
    nav = U.ListNav(s); nav.tall = __import__("PIL.Image", fromlist=["Image"]).open(os.path.join(out, "menu_tall.png")); nav.rows = rows
    ok = nav.tap_row_from_top(idx)
    if ok:
        s.scroll_capture("gt_" + nm, dy=120)
        if gear: s.tap(400, 245, settle=800); s.scroll_capture("gt_" + nm + "_ust", dy=120)
    json.dump(dict(row=nm, entered=ok, level=level, hits=hits), open(os.path.join(out, "gate_%s%s.json" % (nm, "_ust" if gear else "")), "w"), indent=1)
    print(nm, "gear" if gear else "", "entered" if ok else "FAIL", "hits", len(hits), flush=True)
