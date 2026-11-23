#!/usr/bin/env python3
"""PASS 61: ktore prezentery (wywolania model_get 0x08046FF2 z presenter_map) sa FAKTYCZNIE wykonywane na danym ekranie.

Statyczna mapa prezenterow (PASS 58) laczy offsety widgetow z setterami wszystkich widokow naraz, wiec samo
view_off daje mnostwo przypadkowych zgodnosci (ten sam offset w roznych klasach widokow). Ten tracer wchodzi na
wezel inwentarza (ten sam punkt kontrolny co action_probe.py), zaklada hak na model_get i na settery z mapy i przez
--ticks tikow zapisuje:
  sites   - miejsca wywolania model_get (LR-4) wykonane przez GUITask, z kluczem UI (r1)
  setters - settery z mapy wykonane z r0 == aktywny widok (0x20024818) => setter nalezy do klasy tego widoku
Uzycie: python3 -I tools/presenter_trace.py FW.bin DIR presenter_map.csv OUT.json --nodes 0_screen 0_settings ...
Wynik laczy tools/ui_model.py --active OUT.json (EXACT_ACTIVE_VIEW_OFF)."""
import argparse, csv, json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U
from action_probe import enter_node
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_LR
GET = 0x08046FF2; VIEW = 0x20024818; GUI_TCB = 0x20001198

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bin"); ap.add_argument("dir"); ap.add_argument("pmap"); ap.add_argument("out")
    ap.add_argument("--nodes", nargs="+", required=True); ap.add_argument("--ticks", type=int, default=400)
    a = ap.parse_args()
    setters = sorted({int(r["setter"], 16) for r in csv.DictReader(open(a.pmap, encoding="utf-8")) if r["setter"]})
    rows = pickle.load(open(os.path.join(a.dir, "rows.pkl"), "rb"))
    s = U.UiSession.from_checkpoint(a.bin, os.path.join(a.dir, "menu.state"), None)
    res = json.load(open(a.out)) if os.path.exists(a.out) else {}
    cur = dict(on=False, sites={}, setters={})
    def on_get(uc, addr, sz, ud):
        if not cur["on"]: return
        try:
            if s.b.rd(s.b.tcb_ptr) != GUI_TCB: return
        except Exception: return
        site = (uc.reg_read(UC_ARM_REG_LR) & ~1) - 4; key = uc.reg_read(UC_ARM_REG_R1) & 0xFFFF
        cur["sites"].setdefault(hex(site), set()).add(key)
    def on_set(uc, addr, sz, ud):
        if not cur["on"]: return
        r0 = uc.reg_read(UC_ARM_REG_R0); v = s.b.rd(VIEW)
        cur["setters"].setdefault(hex(addr), set()).add("view" if r0 == v else hex(r0))
    s.b.mu.hook_add(UC_HOOK_CODE, on_get, begin=GET, end=GET)
    for t in setters: s.b.mu.hook_add(UC_HOOK_CODE, on_set, begin=t & ~1, end=t & ~1)
    for node in a.nodes:
        if node in res: continue
        st = enter_node(s, a.dir, rows, node)
        s.b.load_state(st); cur.update(on=True, sites={}, setters={}); s.wait(a.ticks); cur["on"] = False
        res[node] = dict(view=hex(s.b.rd(VIEW)), sites={k: sorted(v) for k, v in cur["sites"].items()},
                         setters={k: sorted(v) for k, v in cur["setters"].items()})
        print(node, "sites=%d setters=%d (view: %d)" % (len(res[node]["sites"]), len(res[node]["setters"]),
              sum("view" in v for v in res[node]["setters"].values())), flush=True)
        json.dump(res, open(a.out, "w"), indent=1)
    print("DONE", len(res))

if __name__ == "__main__":
    main()
