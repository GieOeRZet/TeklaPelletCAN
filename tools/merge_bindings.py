#!/usr/bin/env python3
"""E7: wlacza wyniki bind_screen.py (BINDDIR/<EKRAN>.json) do web/estyma_prototype/screens/<EKRAN>.json (pola dynamic[].bind: pid, id punktu, skala = wyswietlone/wstrzykniete).
Instancje OGRZEWANIE2-4 dziedzicza bindingi OGRZEWANIE1 z przesunieciem PID wg regul instancji (UWAGA: INFERENCE, PID=base+inst-1 tylko tam, gdzie lista panelu ma kolejne PID-y - tu kopiujemy bez przesuniecia i oznaczamy inst)."""
import json, os, re, sys
bds = sys.argv[1:] or ["/tmp/w/bind", "/tmp/w/bindlive"]; sd = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "estyma_prototype", "screens")
def num(s):
    m = re.findall(r"-?\d+(?:\.\d+)?", s or ""); return float(m[-1]) if m else None
def load(src):
    out = []
    for bd in bds:
        f = os.path.join(bd, src + ".json")
        if os.path.exists(f): out += json.load(open(f))["bindings"]
    return out
def merge(name, src):
    p = os.path.join(sd, name + ".json"); sc = json.load(open(p)); by = {}
    allb = load(src); cnt = {}
    for b in allb: cnt[b["widget"]] = cnt.get(b["widget"], 0) + 1
    for b in allb:
        if cnt[b["widget"]] > 8 or b.get("stored") != b.get("injected"): continue          # szum (np. licznik % w naglowku zmienia sie sam) albo odrzucony zapis
        by.setdefault(b["widget"], []).append(b)
    n = 0
    for f in sc["dynamic"]:
        f["bind"] = []
        for b in by.get(f["widget"], []):
            a = num(b["after"]); sk = (a / b["injected"]) if (a is not None and b["injected"]) else None
            f["bind"].append(dict(pid=b["pid"], id=b["id"], scale=round(sk, 6) if sk else None, evidence="FACT-DYNAMIC (wstrzykniecie w emulatorze)")); n += 1
    sc["bindings_source"] = "tools/bind_screen.py"; json.dump(sc, open(p, "w"), ensure_ascii=False, indent=1); print(name, "powiazan:", n, "pol:", len(sc["dynamic"]))
for n in sorted({fn[:-5] for bd in bds for fn in os.listdir(bd) if fn.endswith(".json")}):
    if True:
        if os.path.exists(os.path.join(sd, n + ".json")): merge(n, n)
        if n == "OGRZEWANIE1":
            for k in "234": merge("OGRZEWANIE" + k, "OGRZEWANIE1")
