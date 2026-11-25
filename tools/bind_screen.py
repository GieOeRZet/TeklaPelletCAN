#!/usr/bin/env python3
"""E7: binding pol dynamicznych ekranu do PID-ow przez wstrzykniecie wartosci w emulatorze (z punktu kontrolnego ekranu): dla kazdego PID-a kandydata
(odczyty.csv + punkty.csv + PID-y list ui_model) wstrzykuje wartosc, porownuje teksty widocznych widgetow z tekstami bazowymi; zmiana = binding.
Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/bind_screen.py LEVELDIR ROW NAME OUT.json     (ROW=-1 -> HOME)   [BIND_LIMIT=N ogranicza liczbe PID-ow]
Wynik: OUT.json {name, bindings: [{pid, widget, before, after, injected}]}   (wstrzykiwanie tylko w emulatorze, nigdy do kotla)"""
import csv, json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import ui_session as U, ctor_trace as C, ui_extras as X
from PIL import Image
d, row, name, out = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
N = lambda v: int(str(v), 16)
cand = {}
for r in csv.DictReader(open(paths.ROOT / "rejestry/odczyty.csv", encoding="utf-8")): cand[N(r["indeks"])] = r["id"]
for r in csv.DictReader(open(paths.ROOT / "rejestry/punkty.csv", encoding="utf-8")): cand.setdefault(N(r["indeks"]), "punkt_" + r["klucz"])
for rows in json.load(open(paths.UI_MODEL / "lists.json"))["lists"].values():
    for r in rows:
        if r.get("pid"): cand.setdefault(N(r["pid"]), "list")
if os.environ.get("BIND_ALLPIDS") == "1":      # kandydaci: wszystkie 655 PID-ow macierzy + parametry dokumentacji producenta (stany palnika/pomp itd.)
    for r in csv.DictReader(open(paths.DATA / "pid_matrix_655.csv", encoding="utf-8-sig")): cand.setdefault(N(r["pid"]), "pid_" + r["name"][:30])
    for r in json.load(open(paths.UI_MODEL / "vendor_sdo_scada.json"))["parameters"]: cand.setdefault(N(r["index"]), "vendor_" + r["name"][:30])
mm = {N(r["pid"]): (int(r["min"] or 0), int(r["max"] or 0)) for r in csv.DictReader(open(paths.DATA / "pid_matrix_655.csv", encoding="utf-8-sig"))}
pids = sorted(cand)[: int(os.environ.get("BIND_LIMIT", "100000"))]
_sh = os.environ.get("BIND_SHARD")          # "i/n": co n-ty PID zaczynajac od i (rownolegle procesy)
if _sh: _i, _n = map(int, _sh.split("/")); pids = pids[_i::_n]
STATE = os.environ.get("BIND_STATE") == "1"   # rozszerzenie: wykrywaj tez zmiany stanu nie-tekstowych widgetow (diody/ikony: bitmapa przycisku, kolor/widocznosc boxa, ukrycie)
if row < 0:
    s = U.UiSession(str(paths.FIRMWARE), None); t = C.Tracer(s); s.boot(500)
    for p_, v_ in {0x2105: 4, 0x2106: 1, 0x2107: 1, 0x2108: 1}.items(): s.set_local(p_, v_)
    s.set_access(0); s.wait(4500)
else:
    s = U.UiSession.from_checkpoint(str(paths.FIRMWARE), os.path.join(d, "menu.state"), None); s.wait(120)
    nav = U.ListNav(s); nav.tall = Image.open(os.path.join(d, "menu_tall.png")); nav.rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb")); t = C.Tracer(s); t.log.clear()
    assert nav.tap_row_from_top(row); s.wait(700)
ws = C.widget_table(s, t)
tmp = "/tmp/bind_%s.state" % name; s.checkpoint(tmp)
def texts():
    ex = X.extract(s, ws); r = {k: v["text"] for k, v in ex.items() if v.get("cls") == "text" and not v.get("hidden") and v.get("text") is not None}
    if STATE:
        for k, v in ex.items():
            c = v.get("cls")
            if c == "btn": r[k] = "#btn bmp=%s hidden=%s" % (v.get("bmp"), v.get("hidden"))
            elif c == "box": r[k] = "#box color=0x%X alpha=%s hidden=%s" % (v.get("box") or 0, v.get("alpha"), v.get("hidden"))
            elif c in ("image", "other"): r[k] = "#%s hidden=%s" % (c, v.get("hidden"))
            elif c == "text" and v.get("hidden"): r[k] = "#text hidden"
    return r
REVERT = os.environ.get("BIND_REVERT") == "1"   # HOME: po load_state widgety przestaja sie odswiezac -> bez load_state, z cofnieciem wartosci i filtrem szumu
s.b.load_state(tmp); s.wait(150); base = texts(); res = []; noise = set()
if REVERT:
    for _ in range(4):
        s.wait(350); c = texts(); noise |= {w for w in set(c) | set(base) if c.get(w) != base.get(w)}
    s.wait(300); base = texts(); print("szum (widgety zmieniajace sie bez wstrzykniec):", len(noise), flush=True)
for k, pid in enumerate(pids):
    lo, hi = mm.get(pid, (0, 100))
    val = max(lo, min(hi, (lo + hi) // 3 + 7)) if hi > lo else 7
    try:
        if REVERT:
            r_ = s._record(pid); n_ = {1: 1, 2: 2, 3: 4, 4: 2, 5: 4}[r_[1]]; o_ = s.b.rd(r_[0], n_)
            got = s.inject_param(pid, val, 3, 60); s.wait(300); cur = {w: x for w, x in texts().items() if w not in noise}; s.inject_param(pid, o_, 3, 60); s.wait(300)
            base_ = {w: x for w, x in base.items() if w not in noise}
        else:
            s.b.load_state(tmp); s.wait(100); got = s.inject_param(pid, val, 3, 60); s.wait(250); cur = texts(); base_ = base
    except Exception as e: print("ERR", hex(pid), repr(e)[:60], flush=True); continue
    for w, tx in cur.items():
        if base_.get(w) != tx: res.append(dict(pid="0x%04X" % pid, id=cand[pid], widget=w, before=base.get(w), after=tx, injected=val, stored=got))
    if res and res[-1]["pid"] == "0x%04X" % pid: print(res[-1], flush=True)
    if k % 20 == 0: json.dump(dict(name=name, bindings=res, done=k, total=len(pids)), open(out, "w"), ensure_ascii=False, indent=1)
# faza 2: zrodla LIVE przez symulator modulow CAN (LiveSim) - wartosci modulowe nie ida przez wstrzykniecie 0x584
import live_sim as LS
def live_texts(pid=None, val=55.3):
    s.b.load_state(tmp); s.wait(100); sim = LS.LiveSim(s)
    if pid is not None: sim.set(pid, val)
    sim.run(500); s.wait(200); return texts()
try:
    if _sh and _i != 0: raise RuntimeError('faza LIVE tylko w shardzie 0')
    base2 = live_texts()
    for pid in sorted(LS.LiveSim(s).where):
        cur = live_texts(pid)
        for w, tx in cur.items():
            if base2.get(w) != tx: res.append(dict(pid="0x%04X" % pid, id=cand.get(pid, "live"), widget=w, before=base2.get(w), after=tx, injected=553, stored=553, source="LiveSim 55.3 C")); print(res[-1], flush=True)
except Exception as e: print("LIVE ERR", repr(e)[:100], flush=True)
json.dump(dict(name=name, bindings=res, done=len(pids), total=len(pids)), open(out, "w"), ensure_ascii=False, indent=1); print("DONE", name, len(res), "powiazan")
