#!/usr/bin/env python3
"""PASS 70: poprawiony harness akceptacyjny SIEC / INFO / INTERNET (zastepuje screen_acceptance_sii.py z gałęzi ChatGPT).
Realny firmware -> emulator (UiSession) -> punkt kontrolny ekranu (ui_prepare_cfg/action_probe: node_10/17/18) -> BEFORE -> akcja -> AFTER.
Poprawki wzgledem wersji ChatGPT: (1) wejscie przez punkty kontrolne, nie ListNav; (2) diff tylko ciala (y>=46) z przebiegiem kontrolnym tej samej dlugosci;
(3) CAN TX liczony przed i po akcji (nowe ramki 0x584, bez okresowych 0x2167/0x229A); (4) sprawdzenie `stored` po inject_param; (5) widok = vtable [[0x20024818]]; (6) wyniki do OUT/RUN_SUMMARY.json + PNG.
Uzycie: sii_acceptance.py FW STATEDIR OUT {siec|info|internet|all}"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U
from PIL import Image, ImageChops
FW, SD, OUT, WHICH = sys.argv[1:5]; os.makedirs(OUT, exist_ok=True)
PER = {0x2167, 0x229A}; VIEW = 0x20024818
def new(node): s = U.UiSession.from_checkpoint(FW, os.path.join(SD, "node_%s_screen.state" % node), None); s.wait(300); return s
def body(im): return im.crop((0, 46, 480, 272))
def bb(a, b): return ImageChops.difference(body(a), body(b)).getbbox()
def vt(s): return hex(s.b.rd(s.b.rd(VIEW)))
def tx584(s, n0): return [bytes(f["data"]).hex() for f in s.can2.tx[n0:] if f["id"] == 0x584 and int.from_bytes(bytes(f["data"])[1:3], "little") not in PER]
def save(im, name): body(im).save(os.path.join(OUT, name + ".png"))
def step(s, name, act, settle=300):
    """BEFORE -> kontrola (bez akcji, ta sama dlugosc) -> akcja -> AFTER; kontrola i akcja z tego samego punktu: zapis stanu przed akcja"""
    st = os.path.join(OUT, "_tmp.state"); s.checkpoint(st)
    b = s.shot(); s.wait(settle); c = s.shot(); ctrl = bb(b, c)
    s.b.load_state(st); b = s.shot(); n0 = len(s.can2.tx); info = act(s); s.wait(settle); a = s.shot(); save(a, name)
    return dict(test=name, control_diff=ctrl, action_diff=bb(b, a), changed=bool(bb(b, a)) and not ctrl, view=vt(s), tx584=tx584(s, n0), info=info)
res = {}
if WHICH in ("siec", "all"):
    def feed(nodes):
        def f(s):
            for _ in range(6):
                for n in nodes: s.can(0x700 + n, [5]); s.wait(12); s.can(0x580 + n, [0x43, 0x18, 0x10, 2, 0, 0, 0, 0]); s.wait(12)
                s.wait(120)
        return f
    res["SIEC"] = [step(new(17), "siec_" + n, feed(x), 100) for n, x in (("empty", []), ("n56", [0x56]), ("n57", [0x57]), ("n56_57", [0x56, 0x57]), ("n57_56", [0x57, 0x56]), ("n5B", [0x5B]), ("n45", [0x45]), ("n22_unknown", [0x22]))]
if WHICH in ("info", "all"):
    r = []
    for pid, v in ((0x3664, 0x0214), (0x3664, 0x0215), (0x3665, 1), (0x2170, 0), (0x2170, 1), (0x2170, 5678), (0x2170, 65535)):
        r.append(step(new(10), "info_%04X_%d" % (pid, v), lambda s, p=pid, v=v: dict(stored=s.inject_param(p, v), pid=hex(p), value=v)))
    res["INFO"] = r
if WHICH in ("internet", "all"):
    r = []
    for pid, v in ((0x373E, 1), (0x373E, 0), (0x3741, 1), (0x3741, 0), (0x373D, 2), (0x373D, 0)):
        r.append(step(new(18), "int_%04X_%d" % (pid, v), lambda s, p=pid, v=v: dict(stored=s.inject_param(p, v), pid=hex(p), value=v)))
    def ssid(s): return dict(stored=[s.inject_param(0x3730 + i, x) for i, x in enumerate([0x486f6d65, 0, 0, 0, 0, 0])])
    r.append(step(new(18), "int_ssid_chunks", ssid))
    r.append(step(new(18), "int_tap_ssid", lambda s: s.tap(180, 62, settle=1000)))
    res["INTERNET"] = r
json.dump(res, open(os.path.join(OUT, "RUN_SUMMARY.json"), "w"), ensure_ascii=False, indent=1, default=str)
for k, v in res.items():
    for t in v: print(k, t["test"], "changed=%s ctrl=%s view=%s tx=%s %s" % (t["changed"], t["control_diff"], t["view"], t["tx584"][:3], t["info"] if not isinstance(t["info"], type(None)) else ""))
