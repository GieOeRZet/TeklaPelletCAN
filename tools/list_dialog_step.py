#!/usr/bin/env python3
"""PASS 70: dialog liczbowy wiersza listy: krok (+/-), wartosc po OK w jednostkach surowych PID, ramka 0x584. Dla kazdego wiersza number: stuknij wiersz -> dialog -> '+' raz -> OK (zapis) ->
odczyt PID i ramek 0x584; osobno '-' raz. Dialog: '-' (140,202), '+' (295,202), OK (415,228) [zmierzone PASS 66]. Wynik: raw_before, raw_after_plus, raw_after_minus, krok, ramka.
Uzycie: ESTYMA_IDLE_FAST=1 CO_OFFSET=k python3 -I tools/list_dialog_step.py FW DIR INV NODE LISTKEY RESULTS_DIR OUT.json"""
import json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, action_probe as AP, pid_diff as P
fw, d, inv_path, node, key, resdir, out = sys.argv[1:8]
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analiza_archiwum", "FW2213TK-2026-11-22", "data", "ui_model")
CO = int(os.environ.get("CO_OFFSET", "0")); PM = P.pid_meta()
n = json.load(open(os.path.join(resdir, "n_%s.json" % node)))
inv = {x["node"]: x for x in json.load(open(inv_path))}[node]; W = {w["this"]: w for w in inv["widgets"]}
rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb"))
s = U.UiSession.from_checkpoint(fw, os.path.join(d, "menu.state"), None); st = AP.enter_node(s, d, rows, node); s.b.load_state(st); s.wait(600)
recs = {p: (a, sz) for p, a, sz in AP.pid_records(s)}; rd = s.b.rd; S16 = lambda a: rd(a, 2) - 65536 if rd(a, 2) > 32767 else rd(a, 2)
def abs_y(a):
    y = 0
    for _ in range(12):
        if not (0x20000000 <= a < 0x20030000): break
        y += S16(a + 6); a = rd(a + 0x14)
    return y
def val(pid): a, sz = recs[pid]; return rd(a, sz)
res = json.load(open(out)) if os.path.exists(out) else {}
for k, e in sorted(n.items(), key=lambda x: int(x[0])):
    if k in res or e["kind"] != "number" or not e.get("pid") or not e.get("value_widget") or e["value_widget"] not in W: continue
    dec = any("." in (x.get("text") or "") for x in e.get("samples", []))
    if int(k) % int(os.environ.get("STEP_EVERY", "1")) and not dec: continue               # probka: co N-ty wiersz + wszystkie z czescia dziesietna
    pid = int(e["pid"], 16)
    if CO and PM.get(pid + CO, {}).get("name") == PM[pid]["name"]: pid += CO
    if pid not in recs: continue
    w = W[e["value_widget"]]; a = int(e["value_widget"], 16); r = dict(name_en=e["name_en"], pid="0x%04X" % pid, raw_min=e["raw_min"], raw_max=e["raw_max"])
    s.b.load_state(st); s.wait(300)
    for _ in range(14):
        y = abs_y(a)
        if 70 <= y <= 225: break
        s.drag_until_change(240, 230, 240, 80, attempts=4, ticks=240, pause_end=160) if y > 225 else s.drag_until_change(240, 80, 240, 230, attempts=4, ticks=240, pause_end=160)
    for name, bx in (("plus", 295), ("minus", 140)):                    # oba stukniecia w jednej sesji (po '+' wartosc wraca przez '-')
        y = abs_y(a); b0 = val(pid); n0 = len(s.can2.tx)
        s.tap(w["ax"] + 15, y + 20, settle=900); s.wait(200); s.tap(bx, 202, settle=400); s.tap(415, 228, settle=700); s.wait(200)
        r[name] = dict(before=b0, after=val(pid), can=[bytes(f["data"]).hex() for f in s.can2.tx[n0:] if f["id"] == 0x584 and int.from_bytes(bytes(f["data"])[1:3], "little") == pid][:2])
    r["step_up"] = r["plus"]["after"] - r["plus"]["before"]; r["step_down"] = r["minus"]["before"] - r["minus"]["after"]
    res[k] = r; json.dump(res, open(out, "w"), ensure_ascii=False, indent=1); print(k, r["name_en"], r["pid"], "step+", r["step_up"], "step-", r["step_down"], flush=True)
print("DONE")
