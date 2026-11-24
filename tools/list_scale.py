#!/usr/bin/env python3
"""PASS 70: skala/format wartosci wierszy listy parametrow (NASTAWY/Konfiguracja/Statystyki): dla kazdego wiersza listy wstrzykuje surowe wartosci PID
(min, srodek, max, domyslna) i czyta tekst WYSWIETLANY w widgecie wartosci wiersza (bufor +0x34) -> skala dziesietna, format, jednostka (jesli w tekscie), wyliczenia.
Wiersz = widget tekstowy etykiety (ax==30) + widget wartosci (ax==275) na tej samej wysokosci; kolejnosc wierszy = ay. PID wiersza: ui_model/lists.json (poziom 3).
Uzycie: ESTYMA_IDLE_FAST=1 python3 -I tools/list_scale.py FW DIR INV NODE LISTKEY OUT.json   (DIR: punkt kontrolny z ui_prepare_cfg + enter_node)"""
import json, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_session as U, action_probe as AP, pid_diff as P
fw, d, inv_path, node, key, out = sys.argv[1:7]
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analiza_archiwum", "FW2213TK-2026-11-22", "data", "ui_model")
lists = json.load(open(os.path.join(D, "lists.json")))["lists"]
CO = int(os.environ.get("CO_OFFSET", "0"))       # obwody CO2..CO4: PID wiersza = PID bazowy + (k-1), jesli rekord o tej samej nazwie istnieje (lists.json podaje PID CO1)
PM = P.pid_meta()
rows_meta = [r for r in [v for k, v in lists.items() if k.startswith(key + "|")][0]]
inv = {n["node"]: n for n in json.load(open(inv_path))}[node]
ws = inv["widgets"]
labs = sorted([w for w in ws if w["role"] == "text" and w["ax"] == 30 and w["w"] > 0 and w["ay"] >= 55], key=lambda w: w["ay"])
vals = {w["ay"]: w for w in ws if w["role"] == "text" and w["ax"] == 275 and w["w"] > 0}
rows = pickle.load(open(os.path.join(d, "rows.pkl"), "rb"))
s = U.UiSession.from_checkpoint(fw, os.path.join(d, "menu.state"), None)
st = AP.enter_node(s, d, rows, node); s.b.load_state(st); s.wait(600)
rd = s.b.rd; S16 = lambda a: rd(a, 2) - 65536 if rd(a, 2) > 32767 else rd(a, 2)
chk = [(S16(int(w["this"], 16) + 4), S16(int(w["this"], 16) + 6)) for w in labs[:3]]
print("kontrola adresow widgetow (rect z RAM vs inwentarz):", chk, [(w["x"], w["y"]) for w in labs[:3]], flush=True)
print("wierszy w inwentarzu", len(labs), "wierszy w lists.json", len(rows_meta), flush=True)
res = json.load(open(out)) if os.path.exists(out) else {}
def text_of(w): return P.read_text(s, int(w["this"], 16))
for i, meta in enumerate(rows_meta):
    k = "%d" % meta["idx"]
    if CO and meta.get("pid"):
        b = int(meta["pid"], 16); q = PM.get(b + CO)
        if q and q["name"] == PM[b]["name"]: meta = dict(meta, pid="0x%04X" % (b + CO))
    if k in res or i >= len(labs): continue
    vw = next(iter(vals.values()))
    e = dict(row=i, name_en=meta["name_en"], pid=meta["pid"], kind=meta["kind"], raw_min=meta.get("raw_min"), raw_max=meta.get("raw_max"), value_widget=vw["this"] if vw else None, samples=[])
    if meta["pid"] and vw and meta["kind"] in ("number", "enum"):
        lo, hi, df = meta["raw_min"], meta["raw_max"], meta["raw_default"]
        pts = sorted({lo, hi, df, (lo + hi) // 2, min(hi, lo + 1)} if hi - lo > 8 else set(range(lo, hi + 1)))
        for v in pts:
            s.b.load_state(st); s.wait(200)
            got = s.inject_param(int(meta["pid"], 16), v); s.wait(300)
            e["samples"].append(dict(raw=v, stored=got, all={w2["this"]: text_of(w2) for w2 in vals.values()}))
    if e["samples"]:
        cand = [a for a in e["samples"][0]["all"] if len({x["all"][a] for x in e["samples"]}) > 1]      # widget, ktorego tekst zmienia sie z wartoscia PID
        e["value_widget"] = cand[0] if len(cand) == 1 else None; e["bound_candidates"] = cand
        if len(cand) == 1: e["samples"] = [dict(raw=x["raw"], stored=x["stored"], text=x["all"][cand[0]]) for x in e["samples"]]
        else: e["samples"] = [dict(raw=x["raw"], stored=x["stored"]) for x in e["samples"]]
    res[k] = e; json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
    print(k, e["name_en"], [(x["raw"], x.get("text")) for x in e["samples"]][:5], flush=True)
print("DONE")
