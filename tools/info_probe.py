#!/usr/bin/env python3
"""Etap E2: ekran INFO (Informacje o programie) - teksty i zrodla wypelnienia. Baza + wstrzykniecie PID (0x3664, 0x3665, 0x2170 i inne z pid_matrix o nazwach 'soft'/'version') z kontrola szumu.
Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/info_probe.py LDIR OUT.json ROW_INFO. Tylko emulator."""
import json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths, ui_session as U, ctor_trace as C, ui_extras as X, ui_nav
from PIL import Image
d, out, idx = sys.argv[1], sys.argv[2], int(sys.argv[3])
s = U.UiSession.from_checkpoint(str(paths.FIRMWARE), os.path.join(d, "menu.state"), None); s.wait(120)
nav = U.ListNav(s); nav.tall = Image.open(os.path.join(d, "menu_tall.png")); nav.rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb")); t = C.Tracer(s); t.log.clear()
ok = ui_nav.tap_incremental(s, nav, idx) or ui_nav.tap_tail(s, nav, idx, 19); s.wait(1200)
def texts():
    ws = C.widget_table(s, t); ex = X.extract(s, ws)
    return {w["this"]: (w["ay"], w["ax"], ex[w["this"]]["text"]) for w in ws if w["this"] in ex and ex[w["this"]].get("cls") == "text" and not ex[w["this"]].get("hidden") and (ex[w["this"]].get("text") or "").strip()}
base = texts(); s.wait(600); b2 = texts(); noise = {k for k in base if base[k] != b2.get(k)}
res = dict(opened=bool(ok), base=sorted(v for v in b2.values()), noise=len(noise), effects=[])
import csv
cand = [0x3664, 0x3665, 0x2170, 0x3666, 0x3667, 0x3658, 0x3659, 0x3630, 0x3635, 0x3638, 0x363D]
for r in csv.DictReader(open(paths.DATA / "pid_matrix_655.csv", encoding="utf-8-sig")):
    if any(x in r["name"].lower() for x in ("soft", "version", "ver.")) : cand.append(int(r["pid"], 16))
for pid in dict.fromkeys(cand):
    if s._record(pid) is None: continue
    r_ = s._record(pid); n_ = {1: 1, 2: 2, 3: 4, 4: 2, 5: 4}[r_[1]]; o_ = s.b.rd(r_[0], n_)
    for v in (0, 1, 5, 21, 100, 5678, 65535):
        s.inject_param(pid, v, 3, 60); s.wait(500); c = texts()
        ch = [dict(before=b2[k][2], after=c[k][2], pos=[b2[k][0], b2[k][1]]) for k in c if k in b2 and k not in noise and c[k][2] != b2[k][2]]
        if ch: res["effects"].append(dict(pid="0x%04X" % pid, value=v, changed=ch)); print("0x%04X" % pid, v, ch, flush=True)
    s.inject_param(pid, o_, 3, 60); s.wait(400)
json.dump(res, open(out, "w"), ensure_ascii=False, indent=1); print("DONE", len(res["effects"]), res["base"][:40])
