#!/usr/bin/env python3
"""PASS 70: wiersze przelacznikow i wyliczen listy: wstrzykuje 0/1 (lub wartosci wyliczenia) i zapisuje, KTORE widgety listy zmieniaja stan (vis/bitmapa/rect/tekst); slot wiersza = (ay-59)//50.
Uzycie: ESTYMA_IDLE_FAST=1 CO_OFFSET=k python3 -I tools/list_switch.py FW DIR INV NODE LISTKEY OUT.json"""
import json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, action_probe as AP, pid_diff as P
fw, d, inv_path, node, key, out = sys.argv[1:7]
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analiza_archiwum", "FW2213TK-2026-11-22", "data", "ui_model")
rows_meta = [v for k, v in json.load(open(os.path.join(D, "lists.json")))["lists"].items() if k.startswith(key + "|")][0]
CO = int(os.environ.get("CO_OFFSET", "0")); PM = P.pid_meta()
ws = P.good_widgets({n["node"]: n for n in json.load(open(inv_path))}[node])
ws = [w for w in ws if w["role"] in ("text", "image", "other") and w["w"] > 0]
rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb"))
s = U.UiSession.from_checkpoint(fw, os.path.join(d, "menu.state"), None); st = AP.enter_node(s, d, rows, node); s.b.load_state(st); s.wait(600)
res = json.load(open(out)) if os.path.exists(out) else {}
import struct
RAW = open(fw, "rb").read()
def pl(i):
    if i >= 495: return ''
    try:
        p0 = struct.unpack_from("<I", RAW, 0x5BD80 + 4 * i)[0]
        if not 0x08010000 <= p0 < 0x08210000: return ""
        o = p0 - 0x08010000; r = []
        while len(r) < 80:
            c = struct.unpack_from("<H", RAW, o)[0]
            if c == 0: break
            r.append(chr(c)); o += 2
        return "".join(ch for ch in r if ch.isprintable() and not 0xD800 <= ord(ch) <= 0xDFFF)
    except Exception: return "?"
for meta in rows_meta:
    k = "%d" % meta["idx"]
    if k in res or meta["kind"] not in ("switch", "enum") or not meta["pid"]: continue
    pid = int(meta["pid"], 16)
    if CO and PM.get(pid + CO, {}).get("name") == PM[pid]["name"]: pid += CO
    lo, hi = meta["raw_min"], meta["raw_max"]; vals = list(range(lo, min(hi, lo + 6) + 1)); runs = []
    for v in vals:
        s.b.load_state(st); s.wait(200); got = s.inject_param(pid, v); s.wait(300); stt = P.read_state(s, ws)
        for w in ws:
            if w["role"] == "text": stt[w["this"]]["tid"] = s.b.rd(int(w["this"], 16) + 0x26, 2); stt[w["this"]]["label"] = pl(stt[w["this"]]["tid"])
        runs.append((v, got, stt))
    changed = []
    for w in ws:
        sts = [r[2][w["this"]] for r in runs]
        if any(x != sts[0] for x in sts[1:]):
            changed.append(dict(widget=w["this"], role=w["role"], ax=w["ax"], ay=w["ay"], w=w["w"], h=w["h"], slot=(w["ay"] - 59) // 50, per_value={str(r[0]): {k2: v2 for k2, v2 in r[2][w["this"]].items() if k2 in ("vis", "bmp", "text", "rect", "tid", "label")} for r in runs}))
    res[k] = dict(name_en=meta["name_en"], pid="0x%04X" % pid, kind=meta["kind"], values=vals, stored=[r[1] for r in runs], changed=changed); json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
    print(k, meta["name_en"], "0x%04X" % pid, [(c["role"], c["ax"], c["ay"], c["slot"]) for c in changed][:4], flush=True)
print("DONE")
