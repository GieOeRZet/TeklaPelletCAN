#!/usr/bin/env python3
"""PASS 61: ktore prezentery (wywolania model_get 0x08046FF2 z presenter_map) sa FAKTYCZNIE wykonywane na danym ekranie.

Statyczna mapa prezenterow (PASS 58) laczy offsety widgetow z setterami wszystkich widokow naraz, wiec samo
view_off daje mnostwo przypadkowych zgodnosci (ten sam offset w roznych klasach widokow). Ten tracer wchodzi na
wezel inwentarza (ten sam punkt kontrolny co action_probe.py), zaklada hak na model_get i na settery z mapy i przez
--ticks tikow zapisuje:
  sites   - miejsca wywolania model_get (LR-4) wykonane przez GUITask, z kluczem UI (r1)
  setters - settery z mapy wykonane z r0 == aktywny widok (0x20024818) => setter nalezy do klasy tego widoku
Uzycie: python3 -I tools/presenter_trace.py FW.bin DIR presenter_map.csv OUT.json --nodes 0_screen 0_settings ...
Wynik laczy tools/ui_model.py --active OUT.json (EXACT_ACTIVE_VIEW_OFF).
--inv INV.json (v2): dynamiczne wiazanie. Wewnatrz wykonania settera (od wejscia do powrotu pod LR) kazdy zapis
pamieci w obiekt widgetu z inwentarza wezla (lub w jego bufor wildcard, wskaznik +0x34) jest przypisywany do
(setter, ostatnie miejsce model_get w GUITask, klucz UI). Wynik: res[node]["writes"] = lista
{setter, site, key, widget, field_offs[]} - to sa ZAOBSERWOWANE zapisy, nie dopasowanie stalych."""
import argparse, csv, json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U
from action_probe import enter_node
import bisect
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_LR, UC_ARM_REG_SP
GET = 0x08046FF2; VIEW = 0x20024818; GUI_TCB = 0x20001198

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bin"); ap.add_argument("dir"); ap.add_argument("pmap"); ap.add_argument("out")
    ap.add_argument("--nodes", nargs="+", required=True); ap.add_argument("--ticks", type=int, default=400)
    ap.add_argument("--inv", help="inwentarz wezlow (screen_inventory_menu.py) do dynamicznego wiazania zapisow")
    a = ap.parse_args()
    inv = {n["node"]: n for n in json.load(open(a.inv, encoding="utf-8"))} if a.inv else {}
    setters = sorted({int(r["setter"], 16) for r in csv.DictReader(open(a.pmap, encoding="utf-8")) if r["setter"]})
    rows = pickle.load(open(os.path.join(a.dir, "rows.pkl"), "rb"))
    s = U.UiSession.from_checkpoint(a.bin, os.path.join(a.dir, "menu.state"), None)
    res = json.load(open(a.out)) if os.path.exists(a.out) else {}
    cur = dict(on=False, sites={}, setters={}, last=None, stack=[], writes={}, objs=[], starts=[], bufs={})
    def on_get(uc, addr, sz, ud):
        if not cur["on"]: return
        try:
            if s.b.rd(s.b.tcb_ptr) != GUI_TCB: return
        except Exception: return
        site = (uc.reg_read(UC_ARM_REG_LR) & ~1) - 4; key = uc.reg_read(UC_ARM_REG_R1) & 0xFFFF
        cur["sites"].setdefault(hex(site), set()).add(key); cur["last"] = (site, key)
    def on_ret(uc, addr, sz, ud):
        st = cur["stack"]
        while st and st[-1][2] == addr and uc.reg_read(UC_ARM_REG_SP) >= st[-1][3]: st.pop()
    def on_set(uc, addr, sz, ud):
        if not cur["on"]: return
        r0 = uc.reg_read(UC_ARM_REG_R0); v = s.b.rd(VIEW)
        cur["setters"].setdefault(hex(addr), set()).add("view" if r0 == v else hex(r0))
        if r0 == v and cur["objs"]:
            lr = uc.reg_read(UC_ARM_REG_LR) & ~1
            cur["stack"].append((addr, cur["last"], lr, uc.reg_read(UC_ARM_REG_SP)))
            if lr not in rets:                         # wywolanie przez b.w (tail call): powrot pod adres spoza listy BL
                rets.add(lr); uc.hook_add(UC_HOOK_CODE, on_ret, begin=lr, end=lr)
    def on_wr(uc, acc, ad, sz, val, ud):
        if not cur["on"] or not cur["stack"]: return
        sp = uc.reg_read(UC_ARM_REG_SP); st = cur["stack"]
        while st and sp > st[-1][3]: st.pop()          # setter zakonczony (np. wywolany przez b.w / tail call - brak haka powrotu)
        if not st: return
        try:
            if s.b.rd(s.b.tcb_ptr) != GUI_TCB: return  # zapisy innych zadan (przelaczenie kontekstu w trakcie settera)
        except Exception: return
        w = cur["bufs"].get(ad & ~1)
        if w is None:
            i = bisect.bisect_right(cur["starts"], ad) - 1
            if i < 0: return
            base, end, this = cur["objs"][i]
            if ad >= end: return
            w, off = this, ad - base
        else: off = "buf"
        setter, last, _, _ = cur["stack"][-1]
        k = (hex(setter), hex(last[0]) if last else None, last[1] if last else None, w)
        cur["writes"].setdefault(k, set()).add(off)
    # adresy powrotu z setterow: wszystkie BL do setterow z mapy (hak dodawany przed emulacja; dodawanie w trakcie psuje Unicorn)
    raw = open(a.bin, "rb").read(); SB = 0x08010000; tset = {t & ~1 for t in setters}; rets = set()
    for i in range(0, len(raw) - 3, 2):
        h1, h2 = raw[i] | raw[i + 1] << 8, raw[i + 2] | raw[i + 3] << 8
        if (h1 & 0xF800) != 0xF000 or (h2 & 0xD000) != 0xD000: continue
        sg = (h1 >> 10) & 1; i1 = ~(((h2 >> 13) & 1) ^ sg) & 1; i2 = ~(((h2 >> 11) & 1) ^ sg) & 1
        imm = (sg << 24) | (i1 << 23) | (i2 << 22) | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
        if sg: imm -= 1 << 25
        if SB + i + 4 + imm in tset: rets.add(SB + i + 4)
    if inv:
        for r in rets: s.b.mu.hook_add(UC_HOOK_CODE, on_ret, begin=r, end=r)
    s.b.mu.hook_add(UC_HOOK_CODE, on_get, begin=GET, end=GET)
    for t in setters: s.b.mu.hook_add(UC_HOOK_CODE, on_set, begin=t & ~1, end=t & ~1)
    wh = [None]
    for node in a.nodes:
        if node in res: continue
        st = enter_node(s, a.dir, rows, node)
        s.b.load_state(st)
        objs, bufs = [], {}
        if node in inv:
            ws = sorted(inv[node]["widgets"], key=lambda w: int(w["this"], 16))
            for i, w in enumerate(ws):
                b0 = int(w["this"], 16); nxt = int(ws[i + 1]["this"], 16) if i + 1 < len(ws) else b0 + 0x40
                objs.append((b0, min(nxt, b0 + 0x80), w["this"]))
                if w.get("role") == "text":
                    bp = s.b.rd(b0 + 0x34)
                    if 0x20000000 <= bp < 0x2002FFC0 and bp != 0:
                        for j in range(0, 96, 2): bufs[bp + j] = w["this"]
        if wh[0] is not None: s.b.mu.hook_del(wh[0]); wh[0] = None
        if objs:
            lo = min([o[0] for o in objs] + list(bufs)); hi = max([o[1] for o in objs] + [b + 2 for b in bufs])
            wh[0] = s.b.mu.hook_add(UC_HOOK_MEM_WRITE, on_wr, begin=lo, end=hi - 1)
        cur.update(on=True, sites={}, setters={}, last=None, stack=[], writes={}, objs=objs, starts=[o[0] for o in objs], bufs=bufs)
        s.wait(a.ticks); cur["on"] = False
        res[node] = dict(view=hex(s.b.rd(VIEW)), sites={k: sorted(v) for k, v in cur["sites"].items()},
                         setters={k: sorted(v) for k, v in cur["setters"].items()},
                         writes=[dict(setter=k[0], site=k[1], key=k[2], widget=k[3], field_offs=sorted(v, key=str)) for k, v in cur["writes"].items()])
        print(node, "sites=%d setters=%d (view: %d) writes=%d" % (len(res[node]["sites"]), len(res[node]["setters"]),
              sum("view" in v for v in res[node]["setters"].values()), len(res[node]["writes"])), flush=True)
        json.dump(res, open(a.out, "w"), indent=1)
    print("DONE", len(res))

if __name__ == "__main__":
    main()
